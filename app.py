"""
FLIPKART AUTOMATION - Streamlit Web Application
Organized, modular architecture with elevated UX, interactive charts,
and pure direct row extraction.
"""
import sys
import os
import io
import pandas as pd
import streamlit as st

# Import modular components from src
from src.core.extractor import extract_pnl_data_direct
from src.core.matcher import load_master_sku_sheet, enrich_pnl_data
from src.core.calculator import compute_profit_analysis_df, calculate_kpis
from src.core.reader import normalize_text
from src.cli import run_cli_enriched, run_cli_standalone
from src.ui.styles import get_custom_css
from src.ui.components import (
    render_header,
    render_kpi_cards,
    render_validation_banner,
    render_match_status,
    render_download_section
)
from src.ui.charts import (
    render_returns_funnel_chart,
    render_top_skus_chart,
    render_profit_distribution_chart
)


# Cached master catalog indexing for ultra-fast UI response
@st.cache_data(show_spinner="Indexing Master SKU Sheet in memory (~67k-293k entries)...")
def cached_load_master(file_bytes, filename):
    return load_master_sku_sheet(io.BytesIO(file_bytes), filename=filename)


def run_streamlit_app():
    st.set_page_config(
        page_title="FLIPKART AUTOMATION",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Inject modern design styling
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Render Hero Banner
    render_header()

    # File Input Section
    pnl_file = None
    master_file = None
    master_filename = "master"

    sample_pnl_path = os.path.join(os.path.dirname(__file__), "Flipkart_PnL_Sample.xlsx")
    sample_master_path = os.path.join(os.path.dirname(__file__), "Flipkart_Master_SKU_Sample.csv")
    has_sample_files = os.path.exists(sample_pnl_path) and os.path.exists(sample_master_path)

    opt_col, _ = st.columns([2, 2])
    use_sample = False
    if has_sample_files:
        with opt_col:
            use_sample = st.checkbox("📂 Quick Test: Load built-in sample files", value=False)

    if not use_sample:
        col_up1, col_up2 = st.columns(2)

        with col_up1:
            st.markdown("#### 1️⃣ Flipkart P&L Report")
            pnl_file = st.file_uploader(
                "Upload Flipkart P&L Excel (.xlsx)",
                type=["xlsx"],
                help="Upload the seller Profit & Loss report exported from Flipkart."
            )
            if pnl_file:
                st.caption(f"📁 `{pnl_file.name}` ({pnl_file.size / 1024:.1f} KB)")

        with col_up2:
            st.markdown("#### 2️⃣ Master SKU Catalog (Optional)")
            master_file = st.file_uploader(
                "Upload Master SKU Sheet (.csv / .xlsx)",
                type=["csv", "xlsx"],
                help="Optional: Upload to enrich with STYLE NAME, PAYOUT, and compute Net Profit."
            )
            if master_file:
                master_filename = master_file.name
                st.caption(f"📁 `{master_file.name}` ({master_file.size / 1024:.1f} KB)")
    else:
        st.info("📂 **Demo Mode Active:** Utilizing sample files `Flipkart_PnL_Sample.xlsx` and `Flipkart_Master_SKU_Sample.csv`.")
        pnl_file = open(sample_pnl_path, "rb")
        master_file = open(sample_master_path, "rb")
        master_filename = "Flipkart_Master_SKU_Sample.csv"

    # Guide prompt if no P&L uploaded
    if not pnl_file:
        st.markdown("""
            <div style="background: #ffffff; border: 2px dashed #cbd5e1; border-radius: 16px; padding: 3rem 2rem; text-align: center; margin-top: 1.5rem;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <h3 style="color: #1e293b; margin-bottom: 0.5rem;">Awaiting Flipkart P&L Report</h3>
                <p style="color: #64748b; max-width: 500px; margin: 0 auto 1.2rem auto;">
                    Upload your Flipkart Profit & Loss Excel file above, or check <strong>'Use Built-in Sample Data'</strong> in the sidebar to test immediately.
                </p>
            </div>
        """, unsafe_allow_html=True)
        return

    # Sheet Selection (if report contains multiple sheets)
    try:
        excel_inspect = pd.ExcelFile(pnl_file, engine='openpyxl')
        candidate_sheets = [
            s for s in excel_inspect.sheet_names
            if any(k in s.lower() for k in ['p&l', 'sku', 'order', 'orders'])
        ]
        if not candidate_sheets:
            candidate_sheets = excel_inspect.sheet_names
    except Exception:
        candidate_sheets = ['SKU-level P&L']

    # Sort sheets giving priority to Orders P&L (preserves un-added line-by-line order data line 1-1000+)
    def sort_pnl_sheets(name):
        n = normalize_text(name)
        if 'order' in n:
            return 0
        if 'sku' in n:
            return 1
        return 2

    candidate_sheets.sort(key=sort_pnl_sheets)
    selected_sheet = candidate_sheets[0]

    if len(candidate_sheets) > 1:
        c_sheet, _ = st.columns([2, 2])
        with c_sheet:
            selected_sheet = st.selectbox(
                "📑 Source Sheet Mode (Preserves Line-by-Line Without Adding Gross Units)",
                options=candidate_sheets,
                index=0,
                help="Default is 'Orders P&L' to preserve individual order rows line 1 to 1000+ directly without adding/grouping gross units across SKUs."
            )

    # Process P&L Data
    with st.spinner(f"Reading & validating rows from sheet '{selected_sheet}'..."):
        try:
            df_pnl, pnl_meta = extract_pnl_data_direct(pnl_file, sheet_name_override=selected_sheet)
        except Exception as err:
            st.error(f"❌ Error extracting data from P&L Report: {err}")
            return

    # Master Catalog Enrichment
    df_final = df_pnl.copy()
    has_master = False
    enrichment_info = None

    if master_file is not None:
        with st.spinner("Matching SKUs against Master Catalog..."):
            try:
                master_bytes = master_file.read() if hasattr(master_file, 'read') else open(master_file, 'rb').read()
                master_lookup, master_conflicts = cached_load_master(master_bytes, master_filename)
                df_final, enrichment_info = enrich_pnl_data(df_pnl, master_lookup, master_conflicts)
                has_master = True
            except Exception as err:
                st.warning(f"⚠️ Master SKU sheet could not be processed: {err}. Displaying un-enriched data.")
    else:
        st.info("💡 **Master SKU sheet not provided:** Displaying extracted P&L volume. Upload Master SKU sheet in Box #2 to calculate Net Production Cost and Profit.")

    # Compute Profit Analysis
    df_profit = compute_profit_analysis_df(df_final)

    # Calculate KPIs
    kpis = calculate_kpis(pnl_meta, df_profit, has_master=has_master)

    # Master matching feedback
    render_match_status(enrichment_info)

    # Executive KPI Cards Grid
    st.markdown("### 📊 Financial & Operational Overview")
    render_kpi_cards(kpis)

    # Mathematical Verification Banner
    render_validation_banner(kpis)

    # Interactive Tabs: Tables & Visualizations
    tab_profit, tab_summary, tab_charts = st.tabs([
        "💰 Profit & Cost Analysis",
        "📋 SKU Summary",
        "📈 Visual Analytics"
    ])

    with tab_profit:
        f_col1, f_col2, f_col3 = st.columns([3, 2, 2])

        with f_col1:
            query_profit = st.text_input(
                "🔍 Search SKU or Style Name",
                placeholder="Type to filter SKUs...",
                key="profit_search"
            )

        with f_col2:
            status_filter = st.selectbox(
                "Filter by Profitability",
                options=["All SKUs", "Profitable Only (>₹0)", "Loss-Making Only (<₹0)", "Break-Even (=₹0)"],
                index=0,
                key="profit_filter"
            )

        with f_col3:
            sort_profit = st.selectbox(
                "Sort Table By",
                options=[
                    "PROFIT (High to Low)",
                    "Net Production Cost (High to Low)",
                    "Bank Settlement (High to Low)",
                    "Gross Units (High to Low)",
                    "Net Units (High to Low)",
                    "SKU Name (A-Z)"
                ],
                key="profit_sort"
            )

        filtered_profit = df_profit.copy()

        # Apply search query
        if query_profit.strip():
            q = query_profit.strip()
            filtered_profit = filtered_profit[
                filtered_profit['SKU Name'].str.contains(q, case=False, na=False) |
                filtered_profit['Style name'].str.contains(q, case=False, na=False)
            ]

        # Apply profitability filter
        profit_col = 'PROFIT [ Bank Settelement - Net Production Cost ]'
        if status_filter == "Profitable Only (>₹0)":
            filtered_profit = filtered_profit[filtered_profit[profit_col] > 0.01]
        elif status_filter == "Loss-Making Only (<₹0)":
            filtered_profit = filtered_profit[filtered_profit[profit_col] < -0.01]
        elif status_filter == "Break-Even (=₹0)":
            filtered_profit = filtered_profit[(filtered_profit[profit_col] >= -0.01) & (filtered_profit[profit_col] <= 0.01)]

        # Apply sorting
        if sort_profit == "PROFIT (High to Low)":
            filtered_profit = filtered_profit.sort_values(by=profit_col, ascending=False)
        elif sort_profit == "Net Production Cost (High to Low)":
            filtered_profit = filtered_profit.sort_values(by="Net Production Cost [ Unit * ]", ascending=False)
        elif sort_profit == "Bank Settlement (High to Low)":
            filtered_profit = filtered_profit.sort_values(by="Bank Settlement [Projected] (INR)", ascending=False)
        elif sort_profit == "Gross Units (High to Low)":
            filtered_profit = filtered_profit.sort_values(by="Gross Units", ascending=False)
        elif sort_profit == "Net Units (High to Low)":
            filtered_profit = filtered_profit.sort_values(by="Net Units", ascending=False)
        elif sort_profit == "SKU Name (A-Z)":
            filtered_profit = filtered_profit.sort_values(by="SKU Name", ascending=True)

        # Value formatters for Streamlit dataframe
        profit_formatter = {
            "Payout": lambda v: f"₹{v:,.2f}" if pd.notna(v) and str(v) != "" and v != 0 else "",
            "Gross Units": "{:,.0f}",
            "RTO (Logistics Return)": "{:,.0f}",
            "RVP (Customer Return)": "{:,.0f}",
            "Cancelled Units": "{:,.0f}",
            "Net Units": "{:,.0f}",
            "Net Production Cost [ Unit * ]": "₹{:,.2f}",
            "Bank Settlement [Projected] (INR)": "₹{:,.2f}",
            "PROFIT [ Bank Settelement - Net Production Cost ]": "₹{:,.2f}"
        }

        st.dataframe(
            filtered_profit.style.format(profit_formatter),
            use_container_width=True,
            height=460
        )
        st.caption(f"Displaying **{len(filtered_profit):,}** of **{len(df_profit):,}** rows directly from sheet `{selected_sheet}`.")

    with tab_summary:
        s_filter1, _ = st.columns([3, 1])
        with s_filter1:
            query_summary = st.text_input("🔍 Search SKU Name", placeholder="Filter SKUs...", key="summary_search")

        filtered_summary = df_final.copy()
        if query_summary.strip():
            filtered_summary = filtered_summary[
                filtered_summary['SKU Name'].str.contains(query_summary.strip(), case=False, na=False)
            ]

        summary_formatter = {
            "Gross Units": "{:,.0f}",
            "RTO (Logistics Return)": "{:,.0f}",
            "RVP (Customer Return)": "{:,.0f}",
            "Cancelled Units": "{:,.0f}",
            "Net Units": "{:,.0f}",
            "Bank Settlement": "₹{:,.2f}"
        }
        if 'PAYOUT' in filtered_summary.columns:
            summary_formatter["PAYOUT"] = lambda v: f"₹{v:,.2f}" if pd.notna(v) and str(v) != "" else ""

        st.dataframe(
            filtered_summary.style.format(summary_formatter),
            use_container_width=True,
            height=460
        )
        st.caption(f"Displaying **{len(filtered_summary):,}** of **{len(df_final):,}** rows directly from sheet `{selected_sheet}`.")

    with tab_charts:
        st.markdown("#### 📦 Order Fulfillment & Return Breakdown")
        render_returns_funnel_chart(kpis)

        st.markdown("---")
        st.markdown("#### 🏆 SKU Profitability Leaders & Laggards")
        render_top_skus_chart(df_profit, n=8)

        st.markdown("---")
        render_profit_distribution_chart(df_profit)

    # Download & Export Section
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    render_download_section(df_final, df_profit)


def is_running_in_streamlit():
    """Detects whether script is running inside Streamlit server."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_context
        if get_script_run_context() is not None:
            return True
    except Exception:
        pass
    if any("streamlit" in a.lower() for a in sys.argv):
        return True
    return False


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--server.") and not a.startswith("--browser.")]

    if len(args) == 3 and not any(a.startswith("-") for a in args):
        run_cli_enriched(args[0], args[1], args[2])
    elif len(args) == 2 and not any(a.startswith("-") for a in args):
        run_cli_standalone(args[0], args[1])
    elif len(args) >= 1 and args[0] in ["-h", "--help"]:
        print("Usage:")
        print("  Enriched CLI:   python app.py report.xlsx master.csv output.xlsx")
        print("  P&L Only CLI:   python app.py report.xlsx output.xlsx")
        print("  Streamlit Mode: streamlit run app.py")
        sys.exit(0)
    elif not is_running_in_streamlit() and len(args) > 0:
        print("Error: Invalid arguments.")
        print("Usage:")
        print("  Enriched CLI:   python app.py report.xlsx master.csv output.xlsx")
        print("  P&L Only CLI:   python app.py report.xlsx output.xlsx")
        print("  Streamlit Mode: streamlit run app.py")
        sys.exit(1)
    else:
        run_streamlit_app()
