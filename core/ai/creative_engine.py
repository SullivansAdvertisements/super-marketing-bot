import os
import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


def _key():
    # Streamlit secrets first (Streamlit Cloud)
    try:
        k = st.secrets.get("OPENAI_API_KEY", "")
        if k:
            return k
    except Exception:
        pass
    # env fallback (local)
    return os.getenv("OPENAI_API_KEY", "")


def generate_pack(brand, offer, platform, audience):
    if OpenAI is None:
        raise RuntimeError("OpenAI SDK not installed. Add `openai` to requirements.txt")

    api_key = _key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing in Streamlit Secrets.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
Return JSON with: hooks, angles, headlines, descriptions, scripts.

Brand: {brand}
Offer: {offer}
Platform: {platform}
Audience: {audience}
""".strip()

    # Model fallback so you don’t get stuck if one model isn’t allowed
    last_err = None
    for model in ["gpt-4.1-mini", "gpt-4o-mini"]:
        try:
            r = client.responses.create(model=model, input=prompt)
            return r.output_text
        except Exception as e:
            last_err = e

    raise RuntimeError(f"OpenAI request failed: {last_err}")
