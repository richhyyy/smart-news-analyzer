import streamlit as st
import feedparser
import re
from urllib.parse import urlparse

import nltk
nltk.download('punkt')
nltk.download('punkt_tab')

from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import heapq
from textblob import TextBlob


# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Smart News Analyzer", layout="wide")


# -------------------------------
# CUSTOM CSS (Premium look)
# -------------------------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
.block-container {
    padding-top: 2rem;
}
h1 {
    font-weight: 700;
}
.card {
    background-color: #161B22;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    box-shadow: 0 0 10px rgba(124, 58, 237, 0.3);
}
</style>
""", unsafe_allow_html=True)


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
    text = re.sub(r'<[^>]+>', '', text)
    return text.replace('&amp;', '&').strip()


# NLP
def summarize_text(text, n=2):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    freq = Counter(words)

    scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in freq:
                scores[sent] = scores.get(sent, 0) + freq[word]

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
        return "Positive 🙂"
    elif polarity < 0:
        return "Negative 😐"
    return "Neutral 😶"


def detect_category(text):
    text = text.lower()
    if "cricket" in text or "match" in text:
        return "Sports"
    elif "ai" in text or "technology" in text:
        return "Technology"
    elif "market" in text or "stock" in text:
        return "Finance"
    elif "election" in text:
        return "Politics"
    return "General"


# -------------------------------
# UI HEADER
# -------------------------------
st.title("Smart News Analyzer")
st.caption("AI-powered insights from live news feeds")


# Sidebar
st.sidebar.header("Controls")
num_articles = st.sidebar.slider("Articles", 1, 10, 5)

# Input
url = st.text_input("🔗 Enter RSS Feed URL")

# Button
if st.button("Analyze"):
    if not validate_url(url):
        st.error("Invalid URL")
    else:
        with st.spinner("Analyzing news..."):
            feed, error = fetch_feed(url)

            if error:
                st.error(error)
            else:
                for entry in feed.entries[:num_articles]:
                    st.markdown("---")
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

                        st.markdown('<div class="card">', unsafe_allow_html=True)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("### Summary")
                            st.write(summary)

                            st.markdown("###  Sentiment")
                            st.write(sentiment)

                        with col2:
                            st.markdown("###  Keywords")
                            st.write(", ".join(keywords))

                            st.markdown("###  Category")
                            st.write(category)

                        st.markdown('</div>', unsafe_allow_html=True)

                    if hasattr(entry, 'link'):
                        st.markdown(f"[🔗 Read Full Article]({entry.link}")