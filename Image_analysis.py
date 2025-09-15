import streamlit as st
import pandas as pd
from transformers import pipeline
import PyPDF2
import os

# Load Hugging Face models
sentiment_analyzer = pipeline("sentiment-analysis")
toxic_analyzer = pipeline("text-classification", model="unitary/toxic-bert")

# File reader
def read_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    texts = []

    if ext == ".csv":
        df = pd.read_csv(file)
        for col in df.columns:
            texts.extend(df[col].dropna().astype(str).tolist())

    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file)
        for col in df.columns:
            texts.extend(df[col].dropna().astype(str).tolist())

    elif ext == ".pdf":
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.extend(text.split("\n"))

    else:
        st.error("❌ Unsupported file format. Use CSV, Excel, or PDF.")
    
    return [t.strip() for t in texts if t.strip()]

# Analyzer
def analyze_texts(texts):
    results = []
    for msg in texts:
        try:
            sent_res = sentiment_analyzer(msg)[0]
            sentiment = sent_res['label']
            sent_score = round(sent_res['score'], 4)

            tox_res = toxic_analyzer(msg)[0]
            toxicity = tox_res['label']
            tox_score = round(tox_res['score'], 4)

            results.append({
                "Message": msg,
                "Sentiment": sentiment,
                "Sentiment_Score": sent_score,
                "Toxicity": toxicity,
                "Toxicity_Score": tox_score
            })
        except:
            results.append({
                "Message": msg,
                "Sentiment": "ERROR",
                "Sentiment_Score": 0,
                "Toxicity": "ERROR",
                "Toxicity_Score": 0
            })
    return pd.DataFrame(results)

# Streamlit UI
st.title("📊 Message Analysis Tool")
st.write("Upload a CSV, Excel, or PDF file and analyze comments for sentiment & toxicity.")

uploaded_file = st.file_uploader("Upload your file", type=["csv", "xlsx", "xls", "pdf"])

if uploaded_file:
    st.info("📂 File uploaded. Analyzing...")
    texts = read_file(uploaded_file)
    if texts:
        df_results = analyze_texts(texts)

        # Show preview
        st.dataframe(df_results.head(10))

        # Download full report
        csv = df_results.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv,
            file_name="analysis_results.csv",
            mime="text/csv"
        )

        # Filter negative/toxic
        df_filtered = df_results[
            (df_results["Sentiment"] == "NEGATIVE") | (df_results["Toxicity"] == "toxic")
        ]
        if not df_filtered.empty:
            csv_filtered = df_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⚠️ Download Negative/Toxic Report (CSV)",
                data=csv_filtered,
                file_name="negative_toxic_comments.csv",
                mime="text/csv"
            )