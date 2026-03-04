import requests

GRAPH="https://graph.facebook.com/v20.0"

def insights(cid,token):

    r=requests.get(
        f"{GRAPH}/{cid}/insights",
        params={
            "fields":"spend,impressions,clicks",
            "access_token":token
        }
    )

    return r.json()
