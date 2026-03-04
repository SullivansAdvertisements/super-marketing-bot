from openai import OpenAI
import os

def generate_pack(brand,offer,platform,audience):

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt=f'''
Return JSON with hooks, angles, headlines, descriptions, scripts.

Brand:{brand}
Offer:{offer}
Platform:{platform}
Audience:{audience}
'''

    r=client.responses.create(model="gpt-4.1-mini",input=prompt)

    return r.output_text
