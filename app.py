import streamlit as st
import feedparser
import re
from urllib.parse import urlparse
from textblob import TextBlob
from collections import Counter
import plotly.express as px
from transformers import pipeline

st.set_page_config(page_title="AI News Dashboard", layout="wide")


# -------------------------------
# AI MODEL
# -------------------------------
@st.cache_resource
def load_model():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_model()


# -------------------------------
# CSS STYLING
# -------------------------------
st.markdown("""
<style>

/* Background */
body {
    background-color: #0b0f19;
    color: white;
    font-family: 'Inter', sans-serif;
}

/* TITLE (YOUR ADDED STYLE) */
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

/* Cards */
.card {
    background: rgba(17, 24, 39, 0.75);
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 18px;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Buttons */
.stButton > button {
    background-color: #1f2937;
    color: white;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.1);
}
.stButton > button:hover {
    background-color: #374151;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------
# HEADER (IMPORTANT)
# -------------------------------
st.markdown("<div class='title'>Smart News Analyzer</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-powered news breakdown with insights ✨</div>", unsafe_allow_html=True)


# -------------------------------
# FUNCTIONS
# -------------------------------
def validate_url(url):
    return url.startswith(("http://", "https://")) and urlparse(url).netloc


def fetch_feed(url):
    feed = feedparser.parse(url)
    if not feed.entries:
        return None, "No news found"
    return feed, None


def clean_text(text):
    return re.sub(r'<[^>]+>', '', text or "")


def ai_summary(text):
    try:
        text = text[:1000]
        return summarizer(text, max_length=80, min_length=30, do_sample=False)[0]["summary_text"]
    except:
        return "Summary not available"


def sentiment(text):
    score = TextBlob(text).sentiment.polarity
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    return "Neutral"


def keywords(text):
    words = re.findall(r'\w+', text.lower())
    return Counter(words).most_common(5)


def category(text):
    t = text.lower()
    if "ai" in t or "tech" in t:
        return "Tech"
    if "stock" in t:
        return "Finance"
    if "cricket" in t:
        return "Sports"
    if "politics" in t:
        return "Politics"
    return "General"


# -------------------------------
# INPUT
# -------------------------------
url = st.text_input("Enter RSS Feed URL")
num = st.slider("Articles", 1, 10, 5)


# -------------------------------
# RUN
# -------------------------------
if st.button("Analyze") and url:

    if not validate_url(url):
        st.error("Invalid URL")
    else:
        feed, error = fetch_feed(url)

        if error:
            st.error(error)
        else:

            sentiments = []
            categories = []

            for entry in feed.entries[:num]:

                title = entry.title
                desc = clean_text(getattr(entry, "summary", ""))

                summary = ai_summary(desc)
                s = sentiment(desc)
                c = category(desc)
                k = keywords(desc)

                sentiments.append(s)
                categories.append(c)

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader(title)

                st.write(" Summary:", summary)
                st.write(" Sentiment:", s)
                st.write("Category:", c)
                st.write(" Keywords:", k)

                if hasattr(entry, "link"):
                    st.markdown(f"[Read More]({entry.link})")

                st.markdown("</div>", unsafe_allow_html=True)

            # -------------------------------
            # DASHBOARD
            # -------------------------------
            st.subheader("📊 Analytics Dashboard")

            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(
                    names=list(Counter(sentiments).keys()),
                    values=list(Counter(sentiments).values()),
                    title="Sentiment Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(
                    x=list(Counter(categories).keys()),
                    y=list(Counter(categories).values()),
                    title="Category Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)

