from pytrends.request import TrendReq

def fetch_google_trends_interest(keyword: str, geo: str = "US", timeframe: str = "now 7-d"):
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload([keyword], timeframe=timeframe, geo=geo)

    interest = pytrends.interest_over_time()
    related = pytrends.related_queries()

    interest_rows = interest.reset_index().to_dict(orient="records") if not interest.empty else []

    related_top = []
    related_rising = []
    rq = related.get(keyword, {}) if isinstance(related, dict) else {}
    if rq.get("top") is not None:
        related_top = rq["top"].to_dict(orient="records")
    if rq.get("rising") is not None:
        related_rising = rq["rising"].to_dict(orient="records")

    return {
        "keyword": keyword,
        "timeframe": timeframe,
        "geo": geo,
        "interest_over_time": interest_rows,
        "related_top": related_top,
        "related_rising": related_rising,
    }
