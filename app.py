import streamlit as st
import feedparser
import re
from urllib.parse import urlparse

import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import heapq
from textblob import TextBlob


# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Smart News Analyzer", layout="wide")


# -------------------------------
# SAFE PREMIUM UI (NO BREAKING EFFECTS)
# -------------------------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0b0f19;
    color: white;
}

/* Soft glowing background (SAFE) */
body {
    background:
        radial-gradient(circle at 15% 20%, rgba(99,102,241,0.18), transparent 35%),
        radial-gradient(circle at 85% 30%, rgba(14,165,233,0.14), transparent 40%),
        radial-gradient(circle at 50% 85%, rgba(236,72,153,0.10), transparent 45%),
        #0b0f19;
}

.title {
    text-align: center;
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(90deg, #7C3AED, #06B6D4, #F97316);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

/* Subtitle */
.subtitle {
    text-align: center;
    font-size: 16px;
    color: #94a3b8;
    margin-bottom: 25px;
}

/* Input box */
.stTextInput > div > div > input {
    background-color: #111827;
    color: white;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Card */
.card {
    background: rgba(17, 24, 39, 0.75);
    backdrop-filter: blur(10px);
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,0.08);
    transition: 0.2s;
}

.card:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(255,255,255,0.18);
}

/* Buttons */
.stButton > button {
    background-color: #1f2937;
    color: white;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 10px 18px;
    font-weight: 500;
}
.stButton > button:hover {
    background-color: #374151;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}
</style>
""", unsafe_allow_html=True)


# -------------------------------
# HEADER
# -------------------------------
st.markdown("<div class='title'>Smart News Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Clean AI-powered news breakdown </div>", unsafe_allow_html=True)


# -------------------------------
# FUNCTIONS
# -------------------------------
def validate_url(url):
    return url.startswith(("http://", "https://")) and urlparse(url).netloc


def fetch_feed(url):
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return None, "No entries found"
        return feed, None
    except Exception as e:
        return None, str(e)


def clean_html(text):
    if not text:
        return ""
    return re.sub(r'<[^>]+>', '', text)


# NLP FUNCTIONS
def summarize_text(text, n=2):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())

    freq = Counter(words)

    scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            scores[sent] = scores.get(sent, 0) + freq.get(word, 0)

    summary = heapq.nlargest(n, scores, key=scores.get)
    return " ".join(summary)


def extract_keywords(text, n=5):
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalnum()]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(n)]


def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        return "🟢 Positive"
    elif polarity < 0:
        return "🔴 Negative"
    return "🟡 Neutral"


def detect_category(text):
    text = text.lower()
    if "cricket" in text:
        return "Sports"
    elif "ai" in text or "technology" in text:
        return "Tech"
    elif "market" in text:
        return "Finance"
    elif "election" in text:
        return "Politics"
    return "General"


# -------------------------------
# INPUT
# -------------------------------
url = st.text_input("Paste RSS Feed URL")

st.sidebar.header("Controls")
num_articles = st.sidebar.slider("Articles", 1, 10, 5)


# -------------------------------
# RUN BUTTON
# -------------------------------
if st.button("Analyze") and url:

    if not validate_url(url):
        st.error("Invalid URL")
    else:
        with st.spinner("Analyzing news..."):
            feed, error = fetch_feed(url)

            if error:
                st.error(error)
            else:
                for entry in feed.entries[:num_articles]:

                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader(entry.title)

                    description = ""
                    if hasattr(entry, 'summary'):
                        description = entry.summary
                    elif hasattr(entry, 'description'):
                        description = entry.description

                    if description:
                        description = clean_html(description)

                        summary = summarize_text(description)
                        keywords = extract_keywords(description)
                        sentiment = get_sentiment(description)
                        category = detect_category(description)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("###  Summary")
                            st.write(summary)
                            st.markdown("###  Sentiment")
                            st.write(sentiment)

                        with col2:
                            st.markdown("###  Keywords")
                            st.write(", ".join(keywords))
                            st.markdown("###  Category")
                            st.write(category)

                    if hasattr(entry, 'link'):
                        st.markdown(f"[🔗 Read Full Article]({entry.link})")

                    st.markdown("</div>", unsafe_allow_html=True)
