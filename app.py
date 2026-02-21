import streamlit as st
import pandas as pd
import time
from etl import load_data, perform_etl
from stats import generate_descriptive_stats, calculate_health_score
from visuals import generate_visuals
from export import generate_pdf_report

st.set_page_config(page_title="LuminaData", page_icon="💡", layout="wide")

# Custom CSS for extra styling
st.markdown("""
<style>
    .metric-box {
        background-color: #1e212f;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border-left: 5px solid #00e6ff;
    }
    .metric-title {
        color: #a0aab5;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: #ffffff;
        font-size: 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("💡 LuminaData: Autonomous Insight Engine")
st.markdown("Upload your dataset and let the engine uncover the hidden stories.")

# Initialize session state for process log
if 'process_status' not in st.session_state:
    st.session_state.process_status = []
    
def add_status(msg):
    st.session_state.process_status.append(msg)

with st.sidebar:
    st.header("Agent Status")
    status_container = st.empty()
    
    def render_status():
        with status_container.container():
            for msg in st.session_state.process_status:
                st.code(f"> {msg}")
    
    render_status()

# Smart Uploader
uploaded_file = st.file_uploader("Drop your CSV or Excel file here", type=["csv", "xls", "xlsx"])

if uploaded_file is not None:
    if 'data_processed' not in st.session_state or st.session_state.get('uploaded_file_name') != uploaded_file.name:
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.process_status = []
        
        # --- Processing Pipeline ---
        add_status("Initiating data load...")
        render_status()
        time.sleep(0.5)
        
        df_raw, err = load_data(uploaded_file)
        if err:
            st.error(f"Error loading file: {err}")
        else:
            add_status("Data loaded successfully.")
            add_status("Starting ETL pipeline...")
            render_status()
            
            # Run ETL
            with st.spinner("Cleaning and transforming data..."):
                time.sleep(1) # Simulated thought process
                df_clean, etl_stats = perform_etl(df_raw)
                
            add_status(f"ETL Complete: {etl_stats['missing_imputed']} missing imputed, {etl_stats['duplicates_removed']} duplicates removed.")
            render_status()
            
            # Generate Stats
            add_status("Calculating statistics and Data Health Score...")
            render_status()
            with st.spinner("Analyzing numbers..."):
                stats_df = generate_descriptive_stats(df_clean)
                health_score = calculate_health_score(df_raw, df_clean, etl_stats)
            
            # Generate Visuals
            add_status("Selecting best visualizations...")
            render_status()
            with st.spinner("Drawing charts..."):
                figures = generate_visuals(df_clean)
                
            add_status("Analysis complete. Ready for review.")
            render_status()
            
            # Store in session state
            st.session_state.df_clean = df_clean
            st.session_state.etl_stats = etl_stats
            st.session_state.stats_df = stats_df
            st.session_state.health_score = health_score
            st.session_state.figures = figures
            st.session_state.data_processed = True

    if st.session_state.get('data_processed'):
        # UI Tabs
        tab1, tab2, tab3 = st.tabs(["Data Health & Stats", "Visual Storytelling", "Export Hub"])
        
        with tab1:
            st.header("Data Health & Descriptive Statistics")
            # Health Score Display
            score = st.session_state.health_score
            color = "#00e6ff" if score >= 80 else "#f5a623" if score >= 50 else "#ff4b4b"
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-box" style="border-left-color: {color};">
                    <div class="metric-title">Data Health Score</div>
                    <div class="metric-value" style="color: {color};">{score} / 100</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-title">Rows</div>
                    <div class="metric-value">{st.session_state.df_clean.shape[0]}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-title">Columns</div>
                    <div class="metric-value">{st.session_state.df_clean.shape[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("### Descriptive Statistics")
            if st.session_state.stats_df is not None:
                st.dataframe(st.session_state.stats_df, use_container_width=True)
            else:
                st.info("No numerical data available to generate statistics.")
                
        with tab2:
            st.header("Visual Storytelling")
            figures = st.session_state.figures
            if not figures:
                st.info("Not enough numerical columns to generate meaningful visuals.")
            else:
                for item in figures:
                    st.plotly_chart(item["fig"], use_container_width=True)
                    st.info(f"💡 **Insight Engine:** {item['interpretation']}")
                    st.divider()
                    
        with tab3:
            st.header("Export Hub")
            st.markdown("Download the cleaned dataset or the comprehensive PDF report.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                csv_data = st.session_state.df_clean.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv_data,
                    file_name="cleaned_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
            with col2:
                with st.spinner("Generating PDF..."):
                    pdf_data = generate_pdf_report(
                        st.session_state.stats_df,
                        st.session_state.etl_stats,
                        st.session_state.health_score,
                        figures=st.session_state.figures if 'figures' in st.session_state else None
                    )
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name="luminadata_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
