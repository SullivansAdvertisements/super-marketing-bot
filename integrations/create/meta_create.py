import requests

GRAPH="https://graph.facebook.com/v20.0"

def create_campaign(account,token,name):

    r=requests.post(
        f"{GRAPH}/act_{account}/campaigns",
        data={
            "name":name,
            "objective":"TRAFFIC",
            "status":"PAUSED",
            "access_token":token
        }
    )

    return r.json()
