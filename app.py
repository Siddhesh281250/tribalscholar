import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import fuzz

st.set_page_config(
    page_title="MoTA AI Scholarship Management System",
    page_icon="🎓",
    layout="wide"
)

# Mock Application Dataset
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame([
        {
            "App ID": "NOS-2026-001",
            "Scheme": "NOS",
            "Name": "Sunita Marandi",
            "State": "Jharkhand",
            "Income (₹)": 420000,
            "University / Inst": "University of Melbourne",
            "QS Rank / NAAC": 14,
            "ST Cert Name Extracted": "Sunita Marandi",
            "Status": "Auto Verified",
            "Deficiency Note": "None"
        },
        {
            "App ID": "NFST-2026-042",
            "Scheme": "NFST",
            "Name": "Anil Birhor",
            "State": "Odisha",
            "Income (₹)": 280000,
            "University / Inst": "IIT Kharagpur",
            "QS Rank / NAAC": 1,
            "ST Cert Name Extracted": "Anil Kumar Birhor",
            "Status": "Flagged Deficient",
            "Deficiency Note": "Name mismatch on ST Certificate (82% match)"
        },
        {
            "App ID": "NOS-2026-089",
            "Scheme": "NOS",
            "Name": "Pooja Bhagat",
            "State": "Chhattisgarh",
            "Income (₹)": 680000,
            "University / Inst": "King's College London",
            "QS Rank / NAAC": 40,
            "ST Cert Name Extracted": "Pooja Bhagat",
            "Status": "Manual Scrutiny Required",
            "Deficiency Note": "Income exceeds ceiling (₹6,00,000)"
        },
        {
            "App ID": "NFST-2026-104",
            "Scheme": "NFST",
            "Name": "Devendra Gond",
            "State": "Madhya Pradesh",
            "Income (₹)": 190000,
            "University / Inst": "Jawaharlal Nehru University",
            "QS Rank / NAAC": 1,
            "ST Cert Name Extracted": "Devendra Gond",
            "Status": "Approved",
            "Deficiency Note": "None"
        }
    ])

st.title("🏛️ Ministry of Tribal Affairs (MoTA)")
st.caption("AI-Enabled Single Platform for Scholarship & Fellowship Management (NFST & NOS)")

# Role Navigation
role = st.sidebar.radio("Select Portal Interface:", [
    "🔍 Admin Scrutiny & Verification Desk",
    "📝 Applicant Portal & Tracking",
    "📊 Scheme Analytics & Performance",
    "⚙️ Scheme Rule Configurator"
])

# ---------------------------------------------------------
# INTERFACE 1: ADMIN SCRUTINY DESK
# ---------------------------------------------------------
if role == "🔍 Admin Scrutiny & Verification Desk":
    st.subheader("Applications Processing Queue")
    
    col1, col2, col3, col4 = st.columns(4)
    df = st.session_state.applications
    col1.metric("Total Received", len(df))
    col2.metric("Auto Verified", len(df[df["Status"] == "Auto Verified"]))
    col3.metric("Deficient", len(df[df["Status"] == "Flagged Deficient"]))
    col4.metric("Approved", len(df[df["Status"] == "Approved"]))
    
    st.markdown("---")
    scheme_filter = st.selectbox("Filter by Scheme", ["All", "NOS", "NFST"])
    filtered_df = df if scheme_filter == "All" else df[df["Scheme"] == scheme_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    st.subheader("Take Action on Pending Application")
    selected_id = st.selectbox("Select Application ID", filtered_df["App ID"].tolist())
    app_row = df[df["App ID"] == selected_id].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Applicant Name:** {app_row['Name']}")
        st.write(f"**Scheme:** {app_row['Scheme']}")
        st.write(f"**Income:** ₹{app_row['Income (₹)']:,.0f}")
        st.write(f"**Institution:** {app_row['University / Inst']}")
    with c2:
        st.write(f"**Extracted ST Cert Name:** {app_row['ST Cert Name Extracted']}")
        match_score = fuzz.token_sort_ratio(app_row['Name'], app_row['ST Cert Name Extracted'])
        st.write(f"**AI Match Score:** {match_score:.1f}%")
        st.write(f"**Current Status:** {app_row['Status']}")
        
    btn1, btn2, btn3 = st.columns(3)
    if btn1.button("✅ Approve Application", use_container_width=True):
        st.session_state.applications.loc[st.session_state.applications["App ID"] == selected_id, "Status"] = "Approved"
        st.success(f"Application {selected_id} Approved!")
        st.rerun()
        
    if btn2.button("⚠️ Mark Deficient (Request Correction)", use_container_width=True):
        st.session_state.applications.loc[st.session_state.applications["App ID"] == selected_id, "Status"] = "Flagged Deficient"
        st.warning(f"Deficiency raised for {selected_id}")
        st.rerun()

# ---------------------------------------------------------
# INTERFACE 2: APPLICANT PORTAL
# ---------------------------------------------------------
elif role == "📝 Applicant Portal & Tracking":
    st.subheader("Applicant Service Desk")
    
    tab1, tab2 = st.tabs(["Check Application Status", "New Document Pre-Check Simulator"])
    
    with tab1:
        app_id_input = st.text_input("Enter your Application ID", "NOS-2026-001")
        record = st.session_state.applications[st.session_state.applications["App ID"] == app_id_input]
        if not record.empty:
            rec = record.iloc[0]
            st.info(f"**Current Status:** {rec['Status']}")
            st.write(f"**Scheme:** {rec['Scheme']}")
            st.write(f"**Registered Name:** {rec['Name']}")
            st.write(f"**Deficiency Note / Remarks:** {rec['Deficiency Note']}")
            
            if rec["Status"] == "Flagged Deficient":
                st.warning("Please upload corrected ST Certificate below to clear deficiency:")
                st.file_uploader("Upload Corrected Document (PDF/JPG)", type=["pdf", "jpg", "png"])
                if st.button("Submit Corrected Document"):
                    st.success("Resubmitted successfully! Sent to AI verification queue.")
        else:
            st.error("Application ID not found.")

    with tab2:
        st.subheader("Instant Document AI Pre-Check")
        uploaded_file = st.file_uploader("Upload Caste Certificate for Instant OCR Extraction", type=["jpg", "png"])
        claimed_name = st.text_input("Enter your full name as per Aadhaar", "Sunita Marandi")
        
        if uploaded_file and claimed_name:
            st.success("Document analyzed successfully by OCR Engine!")
            extracted_name = "Sunita Marandi"  # Simulated OCR extraction
            score = fuzz.token_sort_ratio(claimed_name.lower(), extracted_name.lower())
            
            st.metric("Name Verification Match", f"{score:.1f}%")
            if score >= 85:
                st.success("Name Verification Passed! High confidence match.")
            else:
                st.error("Name mismatch detected. Please review before final submission.")

# ---------------------------------------------------------
# INTERFACE 3: ANALYTICS & SCHEME PERFORMANCE
# ---------------------------------------------------------
elif role == "📊 Scheme Analytics & Performance":
    st.subheader("MoTA Executive Insights")
    df = st.session_state.applications
    
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.histogram(df, x="State", color="Scheme", title="Applications Distribution by State")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.pie(df, names="Status", title="Application Verification Pipeline Status")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------
# INTERFACE 4: SCHEME RULE CONFIGURATOR
# ---------------------------------------------------------
elif role == "⚙️ Scheme Rule Configurator":
    st.subheader("Configure Scheme Rules & AI Thresholds")
    
    scheme = st.selectbox("Select Scheme to Modify", ["NOS", "NFST"])
    
    if scheme == "NOS":
        income_limit = st.number_input("Maximum Family Income Limit (₹)", value=600000, step=50000)
        qs_rank_limit = st.number_input("Maximum Foreign University QS Rank", value=500, step=50)
        st.info(f"Rule configured: NOS eligible for universities ranked $\le$ {qs_rank_limit} and income $\le$ ₹{income_limit:,.0f}")
    else:
        st.info("Rule configured: NFST applies to M.Phil / Ph.D. in UGC recognized Indian institutes.")
        
    match_threshold = st.slider("Minimum AI Name Match Confidence Threshold (%)", 70, 95, 85)
    
    if st.button("Save & Update Scheme Rules"):
        st.success("Scheme rules updated across system engine!")