"""
Direct 1-to-1 Flipkart P&L report row extraction and mathematical validation.
Preserves every individual row without aggregation, grouping, or pivot tables.
"""
import pandas as pd
from src.config import PNL_COLUMN_ALIASES, NUMERIC_COLUMNS, CANDIDATE_PNL_SHEETS
from src.core.reader import normalize_text, read_excel_auto


def extract_pnl_data_direct(file_source, sheet_name_override=None):
    """
    Direct 1-to-1 row extraction (NO PIVOT / NO GROUPBY).
    Copies each row from row index 2 (row 3 in Excel) directly without summing units across SKUs.

    Returns:
        df (pd.DataFrame): Extracted columns with preserved rows.
        metadata (dict): Summary numbers and equation verification status.
    """
    if hasattr(file_source, 'seek'):
        file_source.seek(0)

    try:
        excel_file = pd.ExcelFile(file_source, engine='openpyxl')
        sheet_names = excel_file.sheet_names
    except Exception as e:
        raise ValueError(f"Unable to read Excel file: {e}")

    target_sheet = None
    if sheet_name_override and sheet_name_override in sheet_names:
        target_sheet = sheet_name_override
    else:
        # Check candidate sheets according to priority order
        for candidate in CANDIDATE_PNL_SHEETS:
            for s in sheet_names:
                if normalize_text(s) == candidate:
                    target_sheet = s
                    break
            if target_sheet:
                break

    if target_sheet is None:
        avail = ", ".join([f"'{s}'" for s in sheet_names])
        raise ValueError(f"Target sheet not found in report. Available sheets: {avail}")

    df_raw = read_excel_auto(file_source, sheet_name=target_sheet, header=None)

    if df_raw.shape[0] < 2:
        raise ValueError(f"Sheet '{target_sheet}' has less than 2 rows for headers.")

    row0 = df_raw.iloc[0].tolist()
    row1 = df_raw.iloc[1].tolist()
    total_cols = df_raw.shape[1]

    col_indices = {}
    missing_cols = []

    # Map columns using first occurrence from left to right
    for out_name, target_aliases in PNL_COLUMN_ALIASES.items():
        found = None
        for c in range(total_cols):
            v0 = normalize_text(row0[c])
            v1 = normalize_text(row1[c])
            if any(v0 == normalize_text(alias) or v1 == normalize_text(alias) for alias in target_aliases):
                found = c
                break

        if found is not None:
            col_indices[out_name] = found
        else:
            missing_cols.append(f"{out_name} (expected one of: {target_aliases})")

    if missing_cols:
        raise ValueError(f"Missing required column(s) in '{target_sheet}' sheet:\n- " + "\n- ".join(missing_cols))

    # Direct 1-to-1 extraction from row index 2 (row 3 in Excel)
    extracted = {out_name: df_raw.iloc[2:, c_idx] for out_name, c_idx in col_indices.items()}
    df = pd.DataFrame(extracted)

    # Cleaning: drop empty SKU, strip whitespace
    df = df.dropna(subset=['SKU Name']).copy()
    df['SKU Name'] = df['SKU Name'].astype(str).str.strip()
    df = df[df['SKU Name'] != '']
    df = df[~df['SKU Name'].str.lower().isin(['nan', 'none', 'null', 'total'])]

    # Numeric conversion: blanks to 0
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    # Reset index (Row-by-Row untouched, absolutely no groupby / pivot)
    df = df.reset_index(drop=True)

    # Validation: Gross Units - RTO - RVP - Cancelled = Net Units
    calc_net = (
        df['Gross Units']
        - df['RTO (Logistics Return)']
        - df['RVP (Customer Return)']
        - df['Cancelled Units']
    )
    diff = (calc_net - df['Net Units']).abs()
    equation_holds = bool((diff < 1e-5).all())
    invalid_rows = int((diff >= 1e-5).sum())

    metadata = {
        'sheet_name': target_sheet,
        'available_sheets': sheet_names,
        'total_rows': len(df),
        'total_gross': float(df['Gross Units'].sum()),
        'total_rto': float(df['RTO (Logistics Return)'].sum()),
        'total_rvp': float(df['RVP (Customer Return)'].sum()),
        'total_cancelled': float(df['Cancelled Units'].sum()),
        'total_net': float(df['Net Units'].sum()),
        'total_bank_settlement': float(df['Bank Settlement'].sum()),
        'balance_equation_holds': equation_holds,
        'invalid_rows_count': invalid_rows
    }

    return df, metadata


# Backward compatibility alias
extract_pnl_data = extract_pnl_data_direct
