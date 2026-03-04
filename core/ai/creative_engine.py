import os
import streamlit as st

try:
    from openai import OpenAI
except Exception as e:
    OpenAI = None


def _get_openai_key() -> str:
    # Streamlit Cloud: st.secrets is the reliable place
    try:
        v = st.secrets.get("OPENAI_API_KEY", "")
        if v:
            return v
    except Exception:
        pass

    # Fallback to env var (works locally if you export it)
    return os.getenv("OPENAI_API_KEY", "")


def generate_pack(brand: str, offer: str, platform: str, audience: str):
    if OpenAI is None:
        raise RuntimeError("OpenAI SDK not installed. Add `openai` to requirements.txt.")

    api_key = _get_openai_key()
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Add it in Streamlit Cloud → Settings → Secrets.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
Return JSON with:
hooks
angles
headlines
descriptions
scripts

Brand: {brand}
Offer: {offer}
Platform: {platform}
Audience: {audience}
""".strip()

    try:
        r = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )
        return r.output_text

    except Exception as e:
        # Show the real API error reason in Streamlit
        # Many OpenAI errors include a status code + message in str(e)
        raise RuntimeError(f"OpenAI request failed: {e}") from e