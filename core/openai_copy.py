import json
from openai import OpenAI

SYSTEM = (
    "You are an elite direct-response performance marketer. "
    "Return ONLY valid JSON. No markdown. No extra text."
)

def generate_copy_json(openai_api_key: str, brand: str, product: str, platform: str,
                       offer: str, audience: str, tone: str, n: int = 10) -> dict:
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    client = OpenAI(api_key=openai_api_key)

    user = f"""
Brand: {brand}
Product/Offer: {product}
Platform: {platform}
Offer/Hook: {offer}
Audience: {audience}
Tone: {tone}

Generate:
- headlines: {n} short options
- descriptions: {n} options (1–2 lines)
- ctas: 10 options

Return JSON with keys: headlines, descriptions, ctas.
"""

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
    )

    text = (resp.output_text or "").strip()
    data = safe_json_loads(text)
    if not isinstance(data, dict):
        raise RuntimeError("OpenAI did not return valid JSON.")
    data.setdefault("headlines", [])
    data.setdefault("descriptions", [])
    data.setdefault("ctas", [])
    return data

def safe_json_loads(s: str):
    try:
        return json.loads(s)
    except Exception:
        start = s.find("{")
        end = s.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(s[start:end+1])
            except Exception:
                return None
        return None
