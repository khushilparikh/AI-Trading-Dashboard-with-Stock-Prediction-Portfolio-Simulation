import requests
import re
from xml.etree import ElementTree

# ==============================
# GET NEWS (SAFE + ROBUST)
# ==============================
def get_stock_news(symbol):
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+stock"

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            return []

        root = ElementTree.fromstring(response.content)

        news_list = []

        for item in root.findall(".//item")[:7]:
            title = item.find("title").text
            link = item.find("link").text

            # Clean title
            title = re.sub(r"[^\w\s]", "", title)

            news_list.append({
                "title": title,
                "link": link
            })

        return news_list

    except Exception as e:
        print(f"[NEWS ERROR]: {e}")
        return []


# ==============================
# ADVANCED SENTIMENT
# ==============================
def analyze_sentiment(news_list):
    if not news_list:
        return "Neutral", 0, 0

    positive_words = [
        "gain", "rise", "growth", "profit", "surge",
        "strong", "record", "beat", "expansion", "bullish"
    ]

    negative_words = [
        "fall", "drop", "loss", "decline",
        "weak", "crash", "miss", "cut", "bearish"
    ]

    total_score = 0
    impact = 0

    for news in news_list:
        text = news["title"].lower()

        for word in positive_words:
            if word in text:
                total_score += 1.5
                impact += 1

        for word in negative_words:
            if word in text:
                total_score -= 1.5
                impact += 1

    avg_score = total_score / max(len(news_list), 1)

    if avg_score > 0.3:
        sentiment = "Positive"
    elif avg_score < -0.3:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return sentiment, round(avg_score, 2), impact


# ==============================
# KEYWORD EXTRACTION (IMPROVED)
# ==============================
def extract_keywords(news_list):
    words = []

    for news in news_list:
        words.extend(news["title"].lower().split())

    # Remove common words
    stopwords = ["the", "is", "in", "of", "and", "to", "for", "on", "with"]

    keywords = [w for w in words if w not in stopwords and len(w) > 3]

    return list(set(keywords[:6]))


# ==============================
# LLM-STYLE SUMMARY (IMPROVED)
# ==============================
def generate_llm_summary(symbol, news_list, sentiment, score, impact):
    if not news_list:
        return "No recent news available for analysis."

    keywords = extract_keywords(news_list)
    keyword_text = ", ".join(keywords)

    if sentiment == "Positive":
        return (
            f"{symbol} is showing strong positive sentiment in recent news coverage. "
            f"Key developments include {keyword_text}. "
            f"The stock is likely benefiting from favorable conditions and investor optimism. "
            f"If momentum continues, it may present potential buying opportunities."
        )

    elif sentiment == "Negative":
        return (
            f"{symbol} is currently under negative sentiment pressure. "
            f"News highlights concerns such as {keyword_text}. "
            f"This could indicate weakness or risk in the short term. "
            f"Investors should remain cautious and monitor further developments."
        )

    else:
        return (
            f"{symbol} is showing neutral sentiment with mixed signals in recent news. "
            f"Topics such as {keyword_text} are being discussed. "
            f"The market lacks clear direction, so waiting for confirmation may be a prudent approach."
        )