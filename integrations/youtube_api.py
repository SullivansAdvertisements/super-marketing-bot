import requests

YOUTUBE_API = "https://www.googleapis.com/youtube/v3/videos"

def fetch_youtube_trending(api_key: str, region_code: str = "US", max_results: int = 25):
    if not api_key:
        raise RuntimeError("YOUTUBE_API_KEY missing")

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": max_results,
        "key": api_key,
    }
    r = requests.get(YOUTUBE_API, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    rows = []
    for item in data.get("items", []):
        sn = item.get("snippet", {}) or {}
        st = item.get("statistics", {}) or {}
        rows.append({
            "video_id": item.get("id"),
            "title": sn.get("title"),
            "channelTitle": sn.get("channelTitle"),
            "publishedAt": sn.get("publishedAt"),
            "categoryId": sn.get("categoryId"),
            "viewCount": st.get("viewCount"),
            "likeCount": st.get("likeCount"),
            "commentCount": st.get("commentCount"),
        })
    return rows
