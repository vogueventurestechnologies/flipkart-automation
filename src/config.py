"""
Configuration, column aliases, constants, and formatting definitions
for FLIPKART AUTOMATION.
"""

# P&L Report Column Aliases (case-insensitive matching)
PNL_COLUMN_ALIASES = {
    'SKU Name': ['sku id', 'sku name', 'sku code', 'seller sku'],
    'Gross Units': ['gross units (#)', 'gross units'],
    'RTO (Logistics Return)': ['rto (logistics return)'],
    'RVP (Customer Return)': ['rvp (customer return)'],
    'Cancelled Units': ['cancellations', 'cancelled units'],
    'Net Units': ['net units (#)', 'net units', 'net units '],
    'Bank Settlement': ['bank settlement [projected] (inr)', 'bank settlement']
}

# Numeric columns in P&L report
NUMERIC_COLUMNS = [
    'Gross Units',
    'RTO (Logistics Return)',
    'RVP (Customer Return)',
    'Cancelled Units',
    'Net Units',
    'Bank Settlement'
]

# Master SKU Sheet Column Aliases
MASTER_SKU_ALIASES = [
    'seller sku on channel',
    'seller sku',
    'sku name',
    'sku id',
    'sku code',
    'sku'
]

MASTER_STYLE_ALIASES = [
    'style name',
    'style'
]

MASTER_PAYOUT_ALIASES = [
    'payout amount',
    'payout (inr)',
    'payout'
]

# Preferred sheets in P&L Excel in descending order of priority
# 'orders p&l' is prioritized to preserve individual order rows without adding/grouping gross units
CANDIDATE_PNL_SHEETS = [
    'orders p&l',
    'orders',
    'order level p&l',
    'sku-level p&l',
    'sku level p&l'
]

# Standard Column Layout for Profit & Cost Analysis
PROFIT_ANALYSIS_COLUMNS = [
    'SKU Name',
    'Style name',
    'Payout',
    'Gross Units',
    'RTO (Logistics Return)',
    'RVP (Customer Return)',
    'Cancelled Units',
    'Net Units',
    'Net Production Cost [ Unit * ]',
    'Bank Settlement [Projected] (INR)',
    'PROFIT [ Bank Settelement - Net Production Cost ]'
]

# Standard Column Layout for SKU Summary
SKU_SUMMARY_COLUMNS = [
    'SKU Name',
    'STYLE NAME',
    'PAYOUT',
    'Gross Units',
    'RTO (Logistics Return)',
    'RVP (Customer Return)',
    'Cancelled Units',
    'Net Units',
    'Bank Settlement'
]

# Excel formatting styles (Clean White Background)
EXCEL_STYLES = {
    'HEADER_FILL_PRIMARY': "FFFFFF",     # Clean White Header
    'HEADER_FILL_ACCENT': "F8FAFC",      # Crisp Off-White Sub-header
    'HEADER_FONT_COLOR': "0F172A",       # Sharp Dark Slate Text
    'HEADER_SUB_COLOR': "334155",        # Dark Slate Text
    'BORDER_COLOR': "CBD5E1",            # Crisp Clean Border
    'ZEBRA_FILL': "FFFFFF",              # Clean White Rows
    'DATA_BORDER': "E2E8F0"              # Subtle Row Lines
}
