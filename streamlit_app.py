import os
import json
import pandas as pd
import streamlit as st

from core.storage import (
    init_db,
    db_insert_budget_plan, db_list_budget_plans,
    db_insert_research_item, db_list_research_items, db_get_research_payload,
    db_insert_copy_bank, db_list_copy_bank, db_get_copy_payload,
    db_insert_campaign_draft, db_list_campaign_drafts, db_get_campaign_payload,
)
from core.budget import DEFAULT_PLATFORMS, normalize_weights, allocate_budget
from core.openai_copy import generate_copy_json

from integrations.youtube_api import fetch_youtube_trending
from integrations.google_trends_pytrends import fetch_google_trends_interest
from integrations.meta_ad_library import search_meta_ad_library
from integrations.tiktok_ingest import ingest_tiktok_creative_center_csv

st.set_page_config(page_title="Super Marketing Bot", page_icon="🚀", layout="wide")
init_db()

st.title("🚀 Super Digital Marketing Bot")
st.caption("Budget Planner • Real Research Data • OpenAI Copy • Campaign Draft Builder")

def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return os.getenv(key, default)

tabs = st.tabs(["💰 Budget Planner", "📈 Research (Real Data)", "🧠 Copy (OpenAI)", "🧩 Campaign Builder", "🗃️ Library"])

# TAB 1
with tabs[0]:
    st.subheader("Budget Planner (Allocate spend across platforms)")
    colA, colB = st.columns([1, 1])
    with colA:
        plan_name = st.text_input("Plan name", value="My Plan")
        total = st.number_input("Total budget ($)", min_value=0.0, value=2000.0, step=50.0)
    with colB:
        st.write("Allocation weights")
        st.caption("Weights auto-normalize so you don’t have to make them sum to 1.0.")
        weights = {}
        cols = st.columns(3)
        for i, p in enumerate(DEFAULT_PLATFORMS):
            with cols[i % 3]:
                weights[p] = st.number_input(p, min_value=0.0, max_value=1.0, value=round(1/len(DEFAULT_PLATFORMS), 2), step=0.01)

    norm = normalize_weights(weights)
    allocations = allocate_budget(float(total), norm)
    st.write("### Allocation result")
    st.dataframe(pd.DataFrame([{"Total": float(total), **allocations}]), use_container_width=True)

    if st.button("Save budget plan", type="primary"):
        db_insert_budget_plan(plan_name, float(total), allocations)
        st.success("Saved budget plan.")

    st.divider()
    st.write("### Saved plans")
    plans = db_list_budget_plans(limit=25)
    st.dataframe(plans if not plans.empty else pd.DataFrame(), use_container_width=True)

# TAB 2
with tabs[1]:
    st.subheader("Research (Real Data Only)")
    st.caption("YouTube Trending + Google Trends + Meta Ad Library + TikTok Creative Center CSV ingest.")

    source = st.selectbox("Choose a research source", ["YouTube Trending (API)", "Google Trends (pytrends)", "Meta Ad Library (API)", "TikTok Creative Center (CSV Upload)"])

    if source == "YouTube Trending (API)":
        yt_key = get_secret("YOUTUBE_API_KEY")
        if not yt_key:
            st.warning("Missing YOUTUBE_API_KEY in Streamlit secrets.")
        region = st.text_input("Region code", value="US")
        max_results = st.slider("Results", min_value=5, max_value=50, value=25, step=5)

        if st.button("Fetch YouTube Trending", type="primary"):
            rows = fetch_youtube_trending(api_key=yt_key, region_code=region, max_results=int(max_results))
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            db_insert_research_item("youtube_trending", region, df.to_dict(orient="records"))
            st.success("Saved to Research Library.")

    elif source == "Google Trends (pytrends)":
        kw = st.text_input("Keyword", value="music promotion")
        geo = st.text_input("Geo", value="US")
        timeframe = st.selectbox("Timeframe", ["now 7-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y"])

        if st.button("Fetch Google Trends", type="primary"):
            payload = fetch_google_trends_interest(keyword=kw, geo=geo, timeframe=timeframe)
            st.write("Interest over time")
            st.dataframe(pd.DataFrame(payload["interest_over_time"]), use_container_width=True)
            st.write("Related (Top)")
            st.dataframe(pd.DataFrame(payload["related_top"]), use_container_width=True)
            st.write("Related (Rising)")
            st.dataframe(pd.DataFrame(payload["related_rising"]), use_container_width=True)
            db_insert_research_item("google_trends", kw, payload)
            st.success("Saved to Research Library.")

    elif source == "Meta Ad Library (API)":
        token = get_secret("META_AD_LIBRARY_TOKEN")
        if not token:
            st.warning("Missing META_AD_LIBRARY_TOKEN in Streamlit secrets.")
        terms = st.text_input("Search terms", value="music promotion")
        status = st.selectbox("Ad active status", ["ACTIVE", "ALL", "INACTIVE"])
        limit = st.slider("Results", min_value=10, max_value=200, value=50, step=10)

        if st.button("Search Meta Ad Library", type="primary"):
            data = search_meta_ad_library(token=token, search_terms=terms, ad_active_status=status, limit=int(limit))
            df = pd.json_normalize(data)
            st.dataframe(df, use_container_width=True)
            db_insert_research_item("meta_ad_library", terms, df.to_dict(orient="records"))
            st.success("Saved to Research Library.")

    else:
        st.caption("Upload a CSV you exported from TikTok Creative Center (Trend Discovery).")
        file = st.file_uploader("TikTok CSV", type=["csv"])
        if file is not None:
            df = ingest_tiktok_creative_center_csv(file)
            st.dataframe(df, use_container_width=True)
            if st.button("Save TikTok Trend Data", type="primary"):
                db_insert_research_item("tiktok_csv", "creative_center_export", df.to_dict(orient="records"))
                st.success("Saved to Research Library.")

    st.divider()
    st.subheader("Recent Research Items")
    r = db_list_research_items(limit=25)
    st.dataframe(r if not r.empty else pd.DataFrame(), use_container_width=True)

# TAB 3
with tabs[2]:
    st.subheader("OpenAI Copy Generator (Headlines • Descriptions • CTAs)")
    st.caption("Generates structured JSON you can push into Campaign Builder.")
    api_key = get_secret("OPENAI_API_KEY")
    if not api_key:
        st.warning("Missing OPENAI_API_KEY in Streamlit secrets.")

    col1, col2 = st.columns([1, 1])
    with col1:
        brand = st.text_input("Brand", value="Sullivan’s Innovative")
        product = st.text_input("Product / Offer", value="Music Promo Package")
        platform = st.selectbox("Platform (copy style)", ["Spotify", "TikTok", "YouTube", "Meta/Instagram", "Google"])
        offer = st.text_input("Offer / Hook", value="Run ads across YouTube + Spotify + IG")
    with col2:
        audience = st.text_input("Audience", value="Independent artists who want more streams")
        tone = st.selectbox("Tone", ["Luxury", "Authority", "Hype", "Friendly", "Aggressive", "Minimal"])
        n = st.slider("How many headline/description options?", min_value=4, max_value=20, value=10, step=2)

    if st.button("Generate Copy (JSON)", type="primary"):
        out = generate_copy_json(
            openai_api_key=api_key,
            brand=brand,
            product=product,
            platform=platform,
            offer=offer,
            audience=audience,
            tone=tone,
            n=int(n),
        )
        st.json(out)
        if st.button("Save to Copy Bank"):
            db_insert_copy_bank(brand, product, platform, out)
            st.success("Saved to Copy Bank.")

    st.divider()
    st.subheader("Recent Copy Bank Items")
    cb = db_list_copy_bank(limit=20)
    st.dataframe(cb if not cb.empty else pd.DataFrame(), use_container_width=True)

# TAB 4
with tabs[3]:
    st.subheader("Campaign Builder (Draft JSON payloads)")
    st.caption("Combine Research + Copy Bank into exportable JSON drafts for each platform.")
    left, right = st.columns([1, 1])

    with left:
        plat = st.selectbox("Platform", ["Spotify", "TikTok", "YouTube", "Meta/Instagram", "Google"])
        name = st.text_input("Campaign name", value="New Campaign")
        objective = st.selectbox("Objective", ["Awareness", "Traffic", "Conversions", "Video Views", "Leads", "App Installs"])
        daily_budget = st.number_input("Daily budget ($)", min_value=0.0, value=25.0, step=5.0)
        geo = st.text_input("Geo / Location", value="United States")
        age = st.selectbox("Age range", ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"])
        gender = st.selectbox("Gender", ["All", "Male", "Female"])
        interests = st.text_area("Interests / Keywords (comma separated)", value="music, hip hop, rap, new music, spotify")

    with right:
        st.write("### Attach Research")
        research_df = db_list_research_items(limit=50)
        research_id = None
        research_payload = None
        if not research_df.empty:
            research_id = st.selectbox("Pick a research item ID", options=list(research_df["id"]))
            research_payload = db_get_research_payload(int(research_id))
            st.caption("Research payload preview (first 5,000 chars)")
            st.text_area("Research JSON", value=json.dumps(research_payload)[:5000], height=180)
        else:
            st.info("No research saved yet—use the Research tab first.")

        st.write("### Attach Copy Bank")
        copy_df = db_list_copy_bank(limit=50)
        copy_id = None
        copy_payload = None
        if not copy_df.empty:
            copy_id = st.selectbox("Pick a copy bank ID", options=list(copy_df["id"]))
            copy_payload = db_get_copy_payload(int(copy_id))
            st.json(copy_payload)
        else:
            st.info("No copy saved yet—use the Copy tab first.")

    st.divider()
    st.write("### Draft Payload")
    draft = {
        "platform": plat,
        "campaign_name": name,
        "objective": objective,
        "budget": {"type": "daily", "amount_usd": float(daily_budget)},
        "targeting": {
            "geo": geo,
            "age_range": age,
            "gender": gender,
            "interests_keywords": [x.strip() for x in interests.split(",") if x.strip()],
        },
        "creative": copy_payload or {"headlines": [], "descriptions": [], "ctas": []},
        "research_context": {"research_id": int(research_id) if research_id else None},
        "notes": "Draft JSON only. Map this to each platform’s create endpoints for live campaign creation.",
    }
    st.json(draft)

    colS, colE = st.columns([1, 1])
    with colS:
        if st.button("Save Draft", type="primary"):
            db_insert_campaign_draft(plat, name, draft)
            st.success("Saved to Campaign Drafts.")

    with colE:
        st.download_button("Download Draft JSON", data=json.dumps(draft, indent=2), file_name="campaign_draft.json", mime="application/json")

# TAB 5
with tabs[4]:
    st.subheader("Library")
    st.write("### Campaign Drafts")
    cd = db_list_campaign_drafts(limit=200)
    st.dataframe(cd if not cd.empty else pd.DataFrame(), use_container_width=True)
    if not cd.empty:
        pick = st.selectbox("View draft payload (by draft id)", options=list(cd["id"]))
        st.json(db_get_campaign_payload(int(pick)))
