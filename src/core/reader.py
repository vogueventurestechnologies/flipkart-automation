"""
File reader utilities for Excel and CSV files with fallback engines.
"""
import re
import os
from pathlib import Path
import pandas as pd


def normalize_text(text):
    """Normalize text: lower-case, trim, and collapse multiple whitespace characters."""
    if text is None or pd.isna(text):
        return ''
    return re.sub(r'\s+', ' ', str(text)).strip().lower()


def detect_is_csv(file_source, filename=None):
    """
    Robust detection of CSV vs Excel files.
    Checks explicit filename, file_source name attribute, or file_source string path.
    """
    candidate_names = []
    if filename:
        candidate_names.append(str(filename))
    if hasattr(file_source, 'name') and file_source.name:
        candidate_names.append(str(file_source.name))
    if isinstance(file_source, (str, Path)):
        candidate_names.append(str(file_source))

    for name in candidate_names:
        low = name.lower()
        if low.endswith('.csv'):
            return True
        if low.endswith('.xlsx') or low.endswith('.xls') or low.endswith('.xlsm'):
            return False

    return False


def read_excel_auto(file_source, sheet_name=0, header=None, nrows=None, usecols=None):
    """
    Reads an Excel file trying python-calamine engine first for speed,
    falling back to openpyxl if calamine fails or cannot detect format.
    """
    if hasattr(file_source, 'seek'):
        file_source.seek(0)

    try:
        return pd.read_excel(
            file_source,
            sheet_name=sheet_name,
            header=header,
            nrows=nrows,
            usecols=usecols,
            engine='calamine'
        )
    except Exception:
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
        return pd.read_excel(
            file_source,
            sheet_name=sheet_name,
            header=header,
            nrows=nrows,
            usecols=usecols,
            engine='openpyxl'
        )
