"""
Master SKU Catalog indexing, conflict resolution, and P&L enrichment.
"""
import io
import pandas as pd
import numpy as np
from src.config import (
    MASTER_SKU_ALIASES,
    MASTER_STYLE_ALIASES,
    MASTER_PAYOUT_ALIASES,
    SKU_SUMMARY_COLUMNS
)
from src.core.reader import normalize_text, read_excel_auto, detect_is_csv


def load_master_sku_sheet(file_source, filename=None):
    """
    Loads and indexes the Master SKU Catalog sheet (Excel or CSV).
    Auto-detects the header row by searching for SKU, Style Name, and Payout aliases.

    Returns:
        df_lookup (pd.DataFrame): Unique normalized SKU indexed DataFrame.
        master_conflicts (dict): SKUs having multiple conflicting style or payout entries.
    """
    is_csv = detect_is_csv(file_source, filename)

    if hasattr(file_source, 'seek'):
        file_source.seek(0)

    # Peek first 15 rows to locate header row
    if is_csv:
        df_peek = pd.read_csv(file_source, nrows=15, header=None)
    else:
        df_peek = read_excel_auto(file_source, sheet_name=0, nrows=15, header=None)

    header_row_idx = None
    sku_col_idx = None
    style_col_idx = None
    payout_col_idx = None

    for r_idx in range(len(df_peek)):
        row_vals = [normalize_text(v) for v in df_peek.iloc[r_idx]]
        s_col, st_col, p_col = None, None, None

        for alias in MASTER_SKU_ALIASES:
            for c_idx, val in enumerate(row_vals):
                if val == alias:
                    s_col = c_idx
                    break
            if s_col is not None:
                break

        for alias in MASTER_STYLE_ALIASES:
            for c_idx, val in enumerate(row_vals):
                if val == alias:
                    st_col = c_idx
                    break
            if st_col is not None:
                break

        for alias in MASTER_PAYOUT_ALIASES:
            for c_idx, val in enumerate(row_vals):
                if val == alias:
                    p_col = c_idx
                    break
            if p_col is not None:
                break

        if s_col is not None and st_col is not None and p_col is not None:
            header_row_idx = r_idx
            sku_col_idx, style_col_idx, payout_col_idx = s_col, st_col, p_col
            break

    missing = []
    if sku_col_idx is None:
        missing.append("SKU Name (aliases: 'sku', 'sku name', 'sku id', 'sku code', 'seller sku')")
    if style_col_idx is None:
        missing.append("STYLE NAME (aliases: 'style name', 'style')")
    if payout_col_idx is None:
        missing.append("PAYOUT (aliases: 'payout', 'payout (inr)', 'payout amount')")

    if missing:
        raise ValueError("Missing required column(s) in Master SKU sheet:\n- " + "\n- ".join(missing))

    # Read full file from detected header row
    if hasattr(file_source, 'seek'):
        file_source.seek(0)

    if is_csv:
        df_raw = pd.read_csv(file_source, skiprows=header_row_idx)
    else:
        df_raw = read_excel_auto(file_source, sheet_name=0, header=header_row_idx)

    df_master = pd.DataFrame({
        'raw_sku': df_raw.iloc[:, sku_col_idx],
        'STYLE NAME': df_raw.iloc[:, style_col_idx],
        'PAYOUT': df_raw.iloc[:, payout_col_idx]
    })

    df_master = df_master.dropna(subset=['raw_sku']).copy()
    df_master['norm_sku'] = df_master['raw_sku'].apply(normalize_text)
    df_master = df_master[df_master['norm_sku'] != '']
    df_master = df_master[~df_master['norm_sku'].isin(['nan', 'none', 'null'])]

    df_master['STYLE NAME'] = df_master['STYLE NAME'].fillna('').astype(str).str.strip()
    df_master['PAYOUT'] = pd.to_numeric(df_master['PAYOUT'], errors='coerce')

    # Detect conflicts (same SKU with different STYLE NAME or PAYOUT)
    df_distinct_pairs = df_master.drop_duplicates(subset=['norm_sku', 'STYLE NAME', 'PAYOUT'])
    conflict_skus_mask = df_distinct_pairs.duplicated(subset=['norm_sku'], keep=False)
    conflicting_norm_skus = set(df_distinct_pairs.loc[conflict_skus_mask, 'norm_sku'].unique())

    master_conflicts = {}
    if conflicting_norm_skus:
        df_conflicts_all = df_master[df_master['norm_sku'].isin(conflicting_norm_skus)]
        for norm_k, grp in df_conflicts_all.groupby('norm_sku'):
            master_conflicts[norm_k] = grp[['raw_sku', 'STYLE NAME', 'PAYOUT']].to_dict('records')

    df_lookup = df_master.drop_duplicates(subset=['norm_sku'], keep='first').set_index('norm_sku')
    return df_lookup, master_conflicts


def enrich_pnl_data(df_pnl, df_master_lookup, master_conflicts):
    """
    Enriches P&L rows with Style Name and Payout from the Master SKU lookup.

    Returns:
        df_final (pd.DataFrame): Enriched dataframe with standard 9 columns.
        enrichment_info (dict): Diagnostic match metrics and conflict records.
    """
    df_enriched = df_pnl.copy()
    df_enriched['norm_sku'] = df_enriched['SKU Name'].apply(normalize_text)

    style_names = []
    payouts = []
    matched_count = 0
    unmatched_skus = []

    for _, row in df_enriched.iterrows():
        n_sku = row['norm_sku']
        if n_sku in df_master_lookup.index:
            entry = df_master_lookup.loc[n_sku]
            st_val = entry['STYLE NAME']
            po_val = entry['PAYOUT']
            style_names.append(st_val if pd.notna(st_val) and str(st_val).strip() != '' else "")
            payouts.append(po_val if pd.notna(po_val) else np.nan)
            matched_count += 1
        else:
            style_names.append("")
            payouts.append(np.nan)
            unmatched_skus.append(row['SKU Name'])

    df_enriched['STYLE NAME'] = style_names
    df_enriched['PAYOUT'] = payouts

    df_final = df_enriched[SKU_SUMMARY_COLUMNS].copy()

    # Find conflicts relevant to this specific report
    report_sku_set = set(df_enriched['norm_sku'])
    conflicts_in_report = {}
    for norm_k, records in master_conflicts.items():
        if norm_k in report_sku_set:
            conflicts_in_report[norm_k] = records

    enrichment_info = {
        'total_rows': len(df_final),
        'matched_count': matched_count,
        'unmatched_count': len(unmatched_skus),
        'unmatched_skus': list(dict.fromkeys(unmatched_skus)),
        'conflicts_count': len(conflicts_in_report),
        'conflicts_in_report': conflicts_in_report
    }

    return df_final, enrichment_info
