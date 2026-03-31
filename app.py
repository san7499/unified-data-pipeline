import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from collections import Counter
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="Unified Data Pipeline", layout="wide")

st.title("🚀 Job + News Data Pipeline Dashboard")

# ---------------- JOB SCRAPER ---------------- #
def scrape_jobs():
    url = "https://realpython.github.io/fake-jobs/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    titles, companies, locations = [], [], []

    jobs = soup.find_all("div", class_="card-content")

    for job in jobs:
        titles.append(job.find("h2").text.strip())
        companies.append(job.find("h3").text.strip())
        locations.append(job.find("p").text.strip())

    return pd.DataFrame({
        "Title": titles,
        "Company": companies,
        "Location": locations,
        "Type": "Job"
    })

# ---------------- NEWS SCRAPER (BBC) ---------------- #
def scrape_bbc():
    url = "https://www.bbc.com/news"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    headlines = []
    for item in soup.find_all("h3"):
        text = item.get_text().strip()
        if len(text) > 30:
            headlines.append(text)

    return pd.DataFrame({
        "Title": headlines,
        "Company": "BBC",
        "Location": "Global",
        "Type": "News"
    })

# ---------------- NEWS SCRAPER (REUTERS) ---------------- #
def scrape_reuters():
    url = "https://www.reuters.com/world/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    headlines = []
    for item in soup.find_all("h3"):
        text = item.get_text().strip()
        if len(text) > 30:
            headlines.append(text)

    return pd.DataFrame({
        "Title": headlines,
        "Company": "Reuters",
        "Location": "Global",
        "Type": "News"
    })

# ---------------- MAIN BUTTON ---------------- #
if st.button("🔍 Run Data Pipeline"):

    # Scrape data
    jobs_df = scrape_jobs()
    bbc_df = scrape_bbc()
    reuters_df = scrape_reuters()

    # Combine all data
    combined_df = pd.concat([jobs_df, bbc_df, reuters_df])

    # Clean data
    combined_df.drop_duplicates(inplace=True)
    combined_df["Title"] = combined_df["Title"].str.lower()

    # Save to CSV
    combined_df.to_csv("combined_data.csv", index=False)

    # Save to SQLite
    conn = sqlite3.connect("data.db")
    combined_df.to_sql("data_pipeline", conn, if_exists="replace", index=False)
    conn.close()

    st.success("✅ Data Pipeline Executed Successfully")

    # Show data
    st.subheader("📋 Combined Data")
    st.dataframe(combined_df.head(50))

    # ---------------- NLP TREND ANALYSIS ---------------- #
    text_data = " ".join(combined_df["Title"])
    words = re.findall(r'\b[a-z]+\b', text_data)

    stopwords = {"the", "and", "is", "in", "to", "of", "for", "on", "with"}
    filtered_words = [word for word in words if word not in stopwords]

    word_counts = Counter(filtered_words)
    top_words = word_counts.most_common(10)

    trend_df = pd.DataFrame(top_words, columns=["Word", "Count"])

    st.subheader("🔥 Trending Topics Across Jobs + News")
    st.dataframe(trend_df)

    # Chart
    fig, ax = plt.subplots()
    ax.bar(trend_df["Word"], trend_df["Count"])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Download
    csv = combined_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Data", csv, "combined_data.csv")

else:
    st.info("Click button to run full pipeline")
