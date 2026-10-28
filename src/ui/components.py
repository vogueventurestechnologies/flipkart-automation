"""
Reusable UI layout components for Streamlit.
"""
import streamlit as st
import pandas as pd
from src.exporters.excel_styler import export_to_styled_excel


def render_header():
    """Renders modern Hero header banner with brand badge and details."""
    st.markdown("""
        <div class="hero-banner">
            <div class="hero-title-row">
                <div class="hero-title-group">
                    <div class="hero-icon-badge">📦</div>
                    <div>
                        <h1 class="hero-title">FLIPKART AUTOMATION</h1>
                        <p class="hero-subtitle">
                            Flipkart P&L SKU Extractor & Profit Analysis — Automated column extraction,
                            Master SKU catalog enrichment, and exact profitability analysis with zero row grouping.
                        </p>
                    </div>
                </div>
                <div>
                    <span class="badge-pill">⚡ Direct 1-to-1 Extraction</span>
                    <span class="badge-pill" style="margin-left: 6px;">v2.0 Modular</span>
                </div>
            </div>
        </div>
        <div class="feature-ribbon">
            <span>🛡️</span>
            <div>
                <strong>Pure Direct Row Extraction:</strong> Preserves every order/SKU line item directly from your report without summing or grouping across identical SKU names.
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(kpis):
    """Renders high-visibility financial and volumetric KPI metric cards."""
    # Row 1: Volume & Revenue
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
            <div class="metric-card-pro card-accent-blue">
                <div class="metric-top">
                    <span class="metric-label-pro">Total SKUs / Rows</span>
                    <span class="metric-icon-small">📄</span>
                </div>
                <div class="metric-value-pro">{kpis['total_rows']:,}</div>
                <div class="metric-sub-pro">
                    <span>Direct extracted rows</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
            <div class="metric-card-pro card-accent-cyan">
                <div class="metric-top">
                    <span class="metric-label-pro">Gross Dispatched</span>
                    <span class="metric-icon-small">📤</span>
                </div>
                <div class="metric-value-pro">{kpis['gross_units']:,.0f}</div>
                <div class="metric-sub-pro">
                    <span>Total units shipped</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
            <div class="metric-card-pro card-accent-green">
                <div class="metric-top">
                    <span class="metric-label-pro">Net Fulfilled Units</span>
                    <span class="metric-icon-small">📥</span>
                </div>
                <div class="metric-value-pro">{kpis['net_units']:,.0f}</div>
                <div class="metric-sub-pro">
                    <span class="sub-pill-positive">{kpis['fulfillment_rate']:.1f}% fulfilled</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
            <div class="metric-card-pro card-accent-purple">
                <div class="metric-top">
                    <span class="metric-label-pro">Bank Settlement</span>
                    <span class="metric-icon-small">🏦</span>
                </div>
                <div class="metric-value-pro">₹{kpis['total_bank_settlement']:,.2f}</div>
                <div class="metric-sub-pro">
                    <span>Projected Flipkart payout</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Row 2: Production Cost, Net Profit, Margin & Lost Units
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        cost_sub = "Based on Master Payout" if kpis['has_master'] else "Upload Master SKU sheet"
        st.markdown(f"""
            <div class="metric-card-pro card-accent-amber">
                <div class="metric-top">
                    <span class="metric-label-pro">Net Production Cost</span>
                    <span class="metric-icon-small">🏷️</span>
                </div>
                <div class="metric-value-pro">₹{kpis['total_cost']:,.2f}</div>
                <div class="metric-sub-pro">
                    <span>{cost_sub}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with p2:
        profit_color = "#15803d" if kpis['total_profit'] >= 0 else "#dc2626"
        pill_cls = "sub-pill-positive" if kpis['total_profit'] >= 0 else "sub-pill-negative"
        pill_txt = "Net Gain" if kpis['total_profit'] >= 0 else "Net Loss"

        st.markdown(f"""
            <div class="metric-card-pro card-accent-green">
                <div class="metric-top">
                    <span class="metric-label-pro">Net PROFIT</span>
                    <span class="metric-icon-small">💰</span>
                </div>
                <div class="metric-value-pro" style="color: {profit_color};">₹{kpis['total_profit']:,.2f}</div>
                <div class="metric-sub-pro">
                    <span class="{pill_cls}">{pill_txt}</span>
                    <span>Bank - Net Cost</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with p3:
        margin_color = "#15803d" if kpis['profit_margin'] >= 0 else "#dc2626"
        st.markdown(f"""
            <div class="metric-card-pro card-accent-purple">
                <div class="metric-top">
                    <span class="metric-label-pro">Net Profit Margin</span>
                    <span class="metric-icon-small">📈</span>
                </div>
                <div class="metric-value-pro" style="color: {margin_color};">{kpis['profit_margin']:.1f}%</div>
                <div class="metric-sub-pro">
                    <span>% of Bank Settlement</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with p4:
        st.markdown(f"""
            <div class="metric-card-pro card-accent-rose">
                <div class="metric-top">
                    <span class="metric-label-pro">Returns & Cancelled</span>
                    <span class="metric-icon-small">↩️</span>
                </div>
                <div class="metric-value-pro">{kpis['lost_units']:,.0f}</div>
                <div class="metric-sub-pro">
                    <span class="sub-pill-negative">{kpis['loss_rate']:.1f}% loss rate</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_validation_banner(kpis):
    """Renders the mathematical balance verification indicator."""
    if kpis['equation_holds']:
        st.markdown(f"""
            <div class="validation-card">
                <div class="validation-card-icon">✅</div>
                <div>
                    <div class="validation-card-title">Mathematical Balance Verification Passed (100% of Rows)</div>
                    <div>
                        <span class="validation-card-formula">
                            Gross Units ({kpis['gross_units']:,.0f}) - RTO ({kpis['rto_units']:,.0f}) - RVP ({kpis['rvp_units']:,.0f}) - Cancelled ({kpis['cancelled_units']:,.0f}) = Net Units ({kpis['net_units']:,.0f})
                        </span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error(f"❌ Balance verification failed on {kpis['invalid_rows_count']} rows! Check input data format.")


def render_match_status(info):
    """Renders catalog matching diagnosis, warnings, and conflict drawers."""
    if not info:
        return

    unmatched_count = info.get('unmatched_count', 0)
    conflicts_count = info.get('conflicts_count', 0)

    if unmatched_count == 0 and conflicts_count == 0:
        st.success("✅ **Perfect Match:** All SKUs in the report matched cleanly with the Master SKU catalog!")
        return

    c_col1, c_col2 = st.columns(2)

    with c_col1:
        if unmatched_count > 0:
            st.warning(f"⚠️ **{unmatched_count} SKU(s) in report not found in Master SKU sheet** (Payout default to 0.00)")
            with st.expander(f"🔍 Inspect {unmatched_count} Unmatched SKU(s)", expanded=False):
                st.write(info['unmatched_skus'])
        else:
            st.success("✅ All report SKUs found in Master sheet.")

    with c_col2:
        if conflicts_count > 0:
            st.warning(f"⚠️ **{conflicts_count} SKU(s) have multiple entries in Master sheet** (1st entry applied)")
            with st.expander(f"🔍 Inspect {conflicts_count} Conflicting SKU Details", expanded=False):
                for norm_k, records in info['conflicts_in_report'].items():
                    first_rec = records[0]
                    st.markdown(f"**SKU:** `{first_rec['raw_sku']}` — *Using 1st entry: STYLE NAME=`{first_rec['STYLE NAME']}`, PAYOUT=`{first_rec['PAYOUT']}`*")
                    df_conflict_view = pd.DataFrame(records)[['raw_sku', 'STYLE NAME', 'PAYOUT']].rename(columns={'raw_sku': 'SKU in Master'})
                    st.dataframe(df_conflict_view, use_container_width=True)
        else:
            st.success("✅ Zero conflicting SKUs detected in Master catalog.")


def render_download_section(df_final, df_profit):
    """Renders clean styled export action buttons."""
    st.markdown("""
        <div class="download-box">
            <div class="download-header">
                <span>📥</span> Export Processed Deliverables
            </div>
        </div>
    """, unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)

    with d1:
        excel_buffer = export_to_styled_excel(df_final, df_profit=df_profit)
        st.download_button(
            label="📊 Download Multi-Sheet Excel (.xlsx)",
            data=excel_buffer,
            file_name="Flipkart_Profit_and_SKU_Analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        st.caption("Sheet 1: 'Profit & Cost Analysis' (2-row header) | Sheet 2: 'SKU Summary'")

    with d2:
        profit_csv = df_profit.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Profit & Cost CSV (.csv)",
            data=profit_csv,
            file_name="Flipkart_Profit_and_Cost_Analysis.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption("All 11 columns with Net Production Cost and Profit.")

    with d3:
        summary_csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download SKU Summary CSV (.csv)",
            data=summary_csv,
            file_name="Flipkart_SKU_Summary.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption("Standard 9-column SKU Summary.")
