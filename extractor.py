"""
FLIPKART AUTOMATION - Backward Compatibility Facade
Re-exports modular functions from `src.core` and `src.exporters`.
"""
from src.config import (
    PNL_COLUMN_ALIASES,
    NUMERIC_COLUMNS,
    MASTER_SKU_ALIASES,
    MASTER_STYLE_ALIASES,
    MASTER_PAYOUT_ALIASES
)
from src.core.reader import normalize_text, read_excel_auto, detect_is_csv
from src.core.extractor import extract_pnl_data_direct, extract_pnl_data
from src.core.matcher import load_master_sku_sheet, enrich_pnl_data
from src.core.calculator import compute_profit_analysis_df, calculate_kpis
from src.exporters.excel_styler import (
    style_profit_analysis_sheet,
    style_sku_summary_sheet,
    export_to_styled_excel,
    save_styled_excel_file
)

__all__ = [
    'PNL_COLUMN_ALIASES',
    'NUMERIC_COLUMNS',
    'MASTER_SKU_ALIASES',
    'MASTER_STYLE_ALIASES',
    'MASTER_PAYOUT_ALIASES',
    'normalize_text',
    'read_excel_auto',
    'detect_is_csv',
    'extract_pnl_data_direct',
    'extract_pnl_data',
    'load_master_sku_sheet',
    'enrich_pnl_data',
    'compute_profit_analysis_df',
    'calculate_kpis',
    'style_profit_analysis_sheet',
    'style_sku_summary_sheet',
    'export_to_styled_excel',
    'save_styled_excel_file'
]
