# FLIPKART AUTOMATION

### Flipkart P&L SKU Extractor & Profit Analysis

A modular Python & Streamlit application that extracts SKU-level data directly from Flipkart Profit & Loss Excel reports, enriches line items with **STYLE NAME** and **PAYOUT** from Master SKU catalogs, and computes **Net Production Cost** and **PROFIT** with zero row aggregation.

---

## 📂 Project Architecture

The codebase is organized into clean, single-responsibility modules:

```text
flipkart-pnl-extractor/
├── src/
│   ├── config.py             # Column aliases, numeric configurations, Excel color tokens
│   ├── core/                 # Business logic & computation engine
│   │   ├── reader.py         # Fast Calamine / OpenPyXL resilient reader & file detection
│   │   ├── extractor.py      # Direct 1-to-1 P&L extraction & mathematical equation validation
│   │   ├── matcher.py        # Master SKU catalog indexing, conflict resolution & enrichment
│   │   └── calculator.py     # Production cost, Net profit, margin %, and KPI aggregations
│   ├── exporters/            # Formatting & Export engines
│   │   └── excel_styler.py   # OpenPyXL 2-row merged header styling, number formats & zebra striping
│   ├── ui/                   # Elevated Streamlit UI
│   │   ├── styles.py         # Custom design system (Inter/Outfit fonts, cards, glassmorphism)
│   │   ├── components.py     # Hero banner, KPI cards, equation badge, download buttons
│   │   └── charts.py         # Interactive Altair charts (fulfillment funnel, top profitable SKUs)
│   └── cli.py                # Dedicated headless CLI batch processor
├── app.py                    # Streamlit web entrypoint (+ CLI proxy)
├── run_cli.py                # Standalone CLI entrypoint
├── extractor.py              # Backward-compatible facade module
├── Flipkart_PnL_Sample.xlsx  # Sample Flipkart P&L report
├── Flipkart_Master_SKU_Sample.csv # Sample Master SKU catalog
├── requirements.txt
└── README.md
```

---

## 🌟 Output Sheets in Excel Workbook

### Sheet 1: `Profit & Cost Analysis` (2-Row Header Layout)

| Row 1 Header | Row 2 Header | Description & Formula | Format |
| :--- | :--- | :--- | :--- |
| **SKU Name** | *(merged)* | SKU Name from report | Text |
| **Style name** | *(merged)* | Style Name from Master sheet | Text |
| **Payout** | *(merged)* | Payout from Master sheet | `#,##0.00` |
| **Gross Units** | *(merged)* | Gross Units dispatched | `#,##0` |
| **Returned & Cancelled Units (Breakup)** | **RTO (Logistics Return)** | Logistics return units | `#,##0` |
| *(merged with above)* | **RVP (Customer Return)** | Customer return units | `#,##0` |
| *(merged with above)* | **Cancelled Units** | Pre-delivery cancellations | `#,##0` |
| **Net Units** | *(merged)* | Net fulfilled units | `#,##0` |
| **Net Production Cost [ Unit * ]** | *(merged)* | `= Net Units * Payout` | `#,##0.00` |
| **Bank Settlement [Projected] (INR)** | *(merged)* | Projected payout from Flipkart | `#,##0.00` |
| **PROFIT [ Bank Settelement - Net Production Cost ]** | *(merged)* | `= Bank Settlement - Net Production Cost` | `#,##0.00` |

- **Frozen Top Rows**: Rows 1 & 2 remain frozen (`freeze_panes = 'A3'`).
- **Direct 1-to-1 Row Extraction**: Preserves all rows directly from the report without any pivot tables or grouping across identical SKU names.

### Sheet 2: `SKU Summary`
- Standard 1-row header summary sheet with frozen header row and SKU column (`freeze_panes = 'B2'`).

---

## 📊 Summary Verification on Sample Data

- **Total SKUs / Rows**: 783
- **Gross Dispatched Units**: 1,728
- **RTO (Logistics Return)**: 537
- **RVP (Customer Return)**: 161
- **Cancelled Units**: 209
- **Net Fulfilled Units**: 821
- **Bank Settlement**: ₹145,295.82
- **Net Production Cost**: ₹135,502.00
- **Net PROFIT**: **₹9,793.82** (7.2% Net Profit Margin)
- **Mathematical Balance**: Holds true for **783 / 783 rows (100%)**:
  $$\text{Gross Units} - \text{RTO} - \text{RVP} - \text{Cancelled} = \text{Net Units}$$

---

## 🚀 Execution Instructions

### 1. Launch Streamlit Web UI
```bash
streamlit run app.py
```
*(Or `python -m streamlit run app.py`)*

### 2. Headless CLI Mode
```bash
# Enriched mode (with Master catalog):
python run_cli.py Flipkart_PnL_Sample.xlsx Flipkart_Master_SKU_Sample.csv output_profit_analysis.xlsx

# Standalone mode (P&L only):
python run_cli.py Flipkart_PnL_Sample.xlsx output_profit_analysis.xlsx
```
