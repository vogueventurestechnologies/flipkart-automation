"""
Core extraction, matching, and calculation modules.
"""
from src.core.reader import normalize_text, read_excel_auto, detect_is_csv
from src.core.extractor import extract_pnl_data_direct, extract_pnl_data
from src.core.matcher import load_master_sku_sheet, enrich_pnl_data
from src.core.calculator import compute_profit_analysis_df, calculate_kpis

__all__ = [
    'normalize_text',
    'read_excel_auto',
    'detect_is_csv',
    'extract_pnl_data_direct',
    'extract_pnl_data',
    'load_master_sku_sheet',
    'enrich_pnl_data',
    'compute_profit_analysis_df',
    'calculate_kpis'
]
