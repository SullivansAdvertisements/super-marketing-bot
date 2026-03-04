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

tabs = st.tabs(["Clients","Creative AI","Campaign Builder","Meta Launch","Reporting","Logs"])

# CLIENTS
with tabs[0]:
    st.header("Client Manager")
    name = st.text_input("Client Name")
    notes = st.text_area("Notes")

    if st.button("Add Client"):
        db.insert("clients",{"name":name,"notes":notes})

    st.dataframe(pd.DataFrame(db.list("clients")))

# CREATIVE
with tabs[1]:
    st.header("AI Creative Generator")

    brand = st.text_input("Brand")
    offer = st.text_input("Offer")
    platform = st.selectbox("Platform",["Meta","Google","TikTok","YouTube"])
    audience = st.text_input("Audience")

    if st.button("Generate Creative"):
        st.write(generate_pack(brand,offer,platform,audience))

# CAMPAIGN BUILDER
with tabs[2]:
    st.header("Campaign Builder")

    name = st.text_input("Campaign Name")
    platform = st.selectbox("Platform",["Meta","Google"])
    budget = st.number_input("Budget",10)
    geo = st.text_input("Geo","US")
    interests = st.text_input("Interests","music,hiphop")
    landing = st.text_input("Landing Page")

    if st.button("Save Campaign"):
        spec = CampaignSpec(name,platform,budget,geo,interests,landing)
        db.insert("campaigns",{
            "name":name,
            "platform":platform,
            "payload":json.dumps(spec.to_dict())
        })

    st.dataframe(pd.DataFrame(db.list("campaigns")))

# META LAUNCH
with tabs[3]:
    st.header("Meta Campaign Launch")

    ad_account = st.text_input("Ad Account ID")
    token = st.text_input("Access Token")
    name = st.text_input("Campaign Name")

    if st.button("Create Campaign"):
        st.write(create_campaign(ad_account,token,name))

# REPORTING
with tabs[4]:
    st.header("Meta Reporting Dashboard")

    cid = st.text_input("Campaign ID")
    token = st.text_input("Token")

    if st.button("Fetch Insights"):
        st.write(insights(cid,token))

# LOGS
with tabs[5]:
    st.header("System Logs")
    st.dataframe(pd.DataFrame(db.list("logs")))
