import requests

GRAPH = "https://graph.facebook.com/v20.0/ads_archive"

def search_meta_ad_library(token: str, search_terms: str, ad_active_status: str = "ACTIVE", limit: int = 50):
    if not token:
        raise RuntimeError("META_AD_LIBRARY_TOKEN missing")

    params = {
        "access_token": token,
        "search_terms": search_terms,
        "ad_active_status": ad_active_status,
        "ad_type": "ALL",
        "fields": ",".join([
            "ad_archive_id",
            "page_name",
            "ad_delivery_start_time",
            "ad_delivery_stop_time",
            "ad_creative_bodies",
            "ad_creative_link_titles",
            "ad_creative_link_descriptions",
            "publisher_platforms",
        ]),
        "limit": limit,
    }
    r = requests.get(GRAPH, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])
