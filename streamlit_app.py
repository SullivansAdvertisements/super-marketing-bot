import streamlit as st
import pandas as pd
import json
from pathlib import Path

from core.db import db
from core.ai.creative_engine import generate_pack
from core.campaign_spec import CampaignSpec
from integrations.create.meta_create import create_campaign
from integrations.reporting.meta_reporting import insights

st.set_page_config(page_title="Sullivan Marketing OS V6.5", layout="wide")

# PREMIUM UI CSS
st.markdown("""
<style>

.stApp {
background: radial-gradient(circle at 20% 20%, #1a1a1a, #000000);
color:white;
}

.sidebar .sidebar-content {
background: linear-gradient(180deg,#000000,#0f0f0f);
}

.gold-glow {
text-align:center;
font-size:42px;
font-weight:bold;
color:#ffd700;
text-shadow:0 0 10px #ffd700,0 0 20px #00ff9c;
}

.star-bg {
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
pointer-events:none;
background-image:
radial-gradient(#ffd700 1px, transparent 1px),
radial-gradient(#00ff9c 1px, transparent 1px);
background-size:60px 60px;
background-position:0 0,30px 30px;
opacity:0.25;
z-index:-1;
}

</style>
<div class="star-bg"></div>
""", unsafe_allow_html=True)

# HEADER
logo = Path("data/assets/logo.jpg")
if logo.exists():
    st.image(str(logo), width=450)

st.markdown('<div class="gold-glow">Sullivan Marketing OS V6.5</div>', unsafe_allow_html=True)

tabs = st.tabs(["Clients", "Creative AI", "Campaign Builder", "Meta Launch", "Reporting", "Logs"])

# CLIENTS
with tabs[0]:
    st.header("Client Manager")

    client_name = st.text_input("Client Name", key="clients_name")
    client_notes = st.text_area("Notes", key="clients_notes")

    if st.button("Add Client", key="clients_add_btn"):
        db.insert("clients", {"name": client_name, "notes": client_notes})

    st.dataframe(pd.DataFrame(db.list("clients")), use_container_width=True)

# CREATIVE
with tabs[1]:
    st.header("AI Creative Generator")

    brand = st.text_input("Brand", key="creative_brand")
    offer = st.text_input("Offer", key="creative_offer")
    creative_platform = st.selectbox("Platform", ["Meta", "Google", "TikTok", "YouTube"], key="creative_platform")
    audience = st.text_input("Audience", key="creative_audience")

if st.button("Generate Creative", key="creative_generate_btn"):
    try:
        out = generate_pack(brand, offer, creative_platform, audience)
        st.success("Creative generated ✅")
        st.write(out)
    except Exception as e:
        st.error("OpenAI call failed. Full details:")
        st.exception(e)
        
# CAMPAIGN BUILDER
with tabs[2]:
    st.header("Campaign Builder")

    campaign_name = st.text_input("Campaign Name", key="builder_campaign_name")
    builder_platform = st.selectbox("Platform", ["Meta", "Google"], key="builder_platform")
    budget = st.number_input("Budget", 10, key="builder_budget")
    geo = st.text_input("Geo", "US", key="builder_geo")
    interests = st.text_input("Interests", "music,hiphop", key="builder_interests")
    landing = st.text_input("Landing Page", key="builder_landing")

    if st.button("Save Campaign", key="builder_save_btn"):
        spec = CampaignSpec(campaign_name, builder_platform, budget, geo, interests, landing)
        db.insert(
            "campaigns",
            {
                "name": campaign_name,
                "platform": builder_platform,
                "payload": json.dumps(spec.to_dict()),
            },
        )

    st.dataframe(pd.DataFrame(db.list("campaigns")), use_container_width=True)

# META LAUNCH
with tabs[3]:
    st.header("Meta Campaign Launch")

    ad_account = st.text_input("Ad Account ID", key="meta_launch_ad_account")
    access_token = st.text_input("Access Token", key="meta_launch_access_token")
    launch_campaign_name = st.text_input("Campaign Name", key="meta_launch_campaign_name")

    if st.button("Create Campaign", key="meta_launch_create_btn"):
        st.write(create_campaign(ad_account, access_token, launch_campaign_name))

# REPORTING
with tabs[4]:
    st.header("Meta Reporting Dashboard")

    campaign_id = st.text_input("Campaign ID", key="reporting_campaign_id")
    reporting_token = st.text_input("Token", key="reporting_token")

    if st.button("Fetch Insights", key="reporting_fetch_btn"):
        st.write(insights(campaign_id, reporting_token))

# LOGS
with tabs[5]:
    st.header("System Logs")
    st.dataframe(pd.DataFrame(db.list("logs")), use_container_width=True)
