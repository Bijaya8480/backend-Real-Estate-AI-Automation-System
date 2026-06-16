import streamlit as st
import pandas as pd
from email_classifier import classify_email
from document_processor import extract_info
from lead_qualifier import qualify_lead
import os
import re

st.set_page_config(page_title="Real Estate AI Pro Automation", layout="wide", initial_sidebar_state="expanded")

# Load custom professional CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

col1, col2 = st.columns([3,1])
with col1:
    st.title("🏠 Real Estate AI Pro Dashboard")
with col2:
    st.metric("Automations", "3", "100% Ready")

tab1, tab2, tab3 = st.tabs(["📧 Email Classification", "📄 Document Processing", "🔥 Lead Qualification"])

with tab1:
    st.header("Classify Property Email")
    email_text = st.text_area("Enter email body:", height=150, placeholder="e.g., Interested in 2BHK viewing...")
    if st.button("Classify", key="email"):
        if email_text:
            result = classify_email(email_text)
            st.success(f"**Category:** {result['category']} (confidence: {result['confidence']})")
            st.json(result['scores'])
    
    st.subheader("Samples")
    if st.button("Sales Sample"):
        st.text_area("", "Interested in viewing the 2BHK apartment. Budget 500k.", key="sales")
    if st.button("Support Sample"):
        st.text_area("", "Leak in kitchen unit 101.", key="sup")

with tab2:
    st.header("Process Lease/Invoice")
    uploaded = st.file_uploader("Upload PDF/TXT", type=['pdf', 'txt'])
    text_input = st.text_area("Or paste text:", height=200)
    
    if st.button("Extract Info", key="doc"):
        if uploaded:
            with open("temp_doc.txt", "wb") as f:
                f.write(uploaded.getvalue())
            path = "temp_doc.txt" if uploaded.type == "text/plain" else uploaded.name  # Mock
            try:
                result = extract_info(path)
                st.success("**Extracted:**")
                st.json(result)
            except:
                st.error("Error processing. Use text for demo.")
        elif text_input:
            # Mock extract_from_text
            st.info("Demo text extract:")
            rent_match = re.search(r'rent[:\\s]*([\\$0-9,]+)', text_input, re.I)
            st.json({"demo_rent": rent_match.group(1) if rent_match else "Not found", "demo_tenant": "parsed"})
    
    st.subheader("Samples")
    with open("data/sample_lease.txt") as f:
        if st.button("Lease Sample"):
            st.text_area("", f.read(), key="lease")

with tab3:
    st.header("Qualify Lead")
    lead_text = st.text_area("Enter lead inquiry:", height=150, placeholder="Budget $500k, ready now...")
    if st.button("Qualify", key="lead"):
        if lead_text:
            result = qualify_lead(lead_text)
            st.success(f"**Lead: {result['qualification']}** (score: {result['score']})")
            st.info(result['reasoning'])
    
    st.subheader("Samples")
    hot_txt = open("data/sample_lead_hot.txt").read()
    warm_txt = open("data/sample_lead_warm.txt").read()
    cold_txt = open("data/sample_lead_cold.txt").read()
    samples = {"Hot": hot_txt, "Warm": warm_txt, "Cold": cold_txt}
    for name, txt in samples.items():
        if st.button(name):
            st.text_area("", txt, key=name.lower())

# Bonus CRM export
if st.sidebar.button("Export Results to CSV (CRM)"):
    df = pd.DataFrame([{"module": "demo", "result": "export"}])
    csv = df.to_csv()
    st.sidebar.download_button("Download CRM.csv", csv)

st.sidebar.markdown("---")
st.sidebar.info("Install deps & run: `streamlit run app/dashboard.py`")

# Clean temp
import atexit
import os
atexit.register(os.remove, "temp_doc.txt")
