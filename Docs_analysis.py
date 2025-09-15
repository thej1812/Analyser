import streamlit as st
import pandas as pd
import PyPDF2
import os
import io
from transformers import pipeline
from fpdf import FPDF
import matplotlib.pyplot as plt

# ---------------------------
# Initialize Hugging Face pipeline
# ---------------------------
try:
    sentiment_pipeline = pipeline("sentiment-analysis")  # DistilBERT for Positive/Negative
except Exception as e:
    st.error(f"Error initializing sentiment pipeline: {e}")

# ---------------------------
st.title("📊 Comment Analyzer (Positive / Negative)")

# File uploader
uploaded_file = st.file_uploader("Upload CSV, Excel, or PDF", type=["csv", "xlsx", "xls", "pdf"])

# ---------------------------
# Read uploaded file
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
        st.error("❌ Unsupported file format.")
    
    # Clean: remove empty strings and duplicates
    cleaned_texts = list(dict.fromkeys([t.strip() for t in texts if t.strip()]))
    return cleaned_texts

# ---------------------------
# Analyze comments
def analyze_comments(comments):
    results = []
    for comment in comments:
        sent = sentiment_pipeline(comment)[0]
        label = sent["label"]
        score = sent["score"]

        # Percentages
        if label == "POSITIVE":
            positive_pct = round(score * 100, 2)
            negative_pct = round((1 - score) * 100, 2)
            final_label = "Positive"
        else:  # NEGATIVE
            negative_pct = round(score * 100, 2)
            positive_pct = round((1 - score) * 100, 2)
            final_label = "Negative"

        results.append({
            "Comment": comment,
            "Positive %": positive_pct,
            "Negative %": negative_pct,
            "Category": final_label
        })
    return pd.DataFrame(results)

# ---------------------------
# PDF helper
def create_pdf(df, filename):
    if not os.path.exists("DejaVuSans.ttf"):
        st.error("❌ DejaVuSans.ttf font not found! Place it in the same folder as this script.")
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.set_font("DejaVu", size=12)

    pdf.cell(0, 10, f"{filename} Comments", ln=True, align="C")
    pdf.ln(10)

    # Table header
    pdf.multi_cell(0, 8, f"{'Comment':<60} {'Positive %':>10} {'Negative %':>10} {'Category':>15}")
    pdf.ln(2)

    # Table rows
    for _, row in df.iterrows():
        pdf.multi_cell(0, 8, f"{row['Comment']} | {row['Positive %']} | {row['Negative %']} | {row['Category']}")
        pdf.ln(1)

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    return pdf_bytes

# ---------------------------
# Download full analysis
def download_full(df, filename):
    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(f"📥 Download Full Analysis as CSV", data=csv, file_name=f"{filename}.csv", mime="text/csv")

    # Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    st.download_button(f"📥 Download Full Analysis as Excel", data=output.getvalue(), file_name=f"{filename}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # PDF
    pdf_output = create_pdf(df, filename)
    if pdf_output:
        st.download_button(f"📥 Download Full Analysis as PDF", data=pdf_output, file_name=f"{filename}.pdf", mime="application/pdf")

# ---------------------------
# Main
if uploaded_file:
    comments = read_file(uploaded_file)
    if comments:
        st.info(f"Analyzing {len(comments)} comments...")
        df_results = analyze_comments(comments)

        # Split tables
        df_positive = df_results[df_results["Category"]=="Positive"].drop(columns=["Category"])
        df_negative = df_results[df_results["Category"]=="Negative"].drop(columns=["Category"])

        st.subheader("✅ Positive Comments")
        st.dataframe(df_positive)

        st.subheader("⚠️ Negative Comments")
        st.dataframe(df_negative)

        # Bar chart
        st.subheader("📊 Comment Category Distribution")
        category_counts = df_results['Category'].value_counts()
        fig, ax = plt.subplots()
        ax.bar(category_counts.index, category_counts.values, color=['green', 'red'])
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Comments")
        ax.set_title("Comments Distribution")
        for i, v in enumerate(category_counts.values):
            ax.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        st.pyplot(fig)

        # Only full analysis download
        download_full(df_results, "Full_Analysis")