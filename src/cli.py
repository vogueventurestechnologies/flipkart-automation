"""
Command Line Interface (CLI) for headless execution and batch processing.
Supports both Master SKU enriched and P&L standalone runs.
"""
import sys
import os
from src.core.extractor import extract_pnl_data_direct
from src.core.matcher import load_master_sku_sheet, enrich_pnl_data
from src.core.calculator import compute_profit_analysis_df, calculate_kpis
from src.exporters.excel_styler import save_styled_excel_file


def _reconfigure_utf8():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ['utf-8', 'utf8']:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass


def run_cli_enriched(report_path, master_path, output_path):
    """Executes enriched workflow with master SKU lookup."""
    _reconfigure_utf8()

    print("=" * 75)
    print(" FLIPKART AUTOMATION - SKU Extractor & Profit Analysis (CLI)")
    print("=" * 75)

    if not os.path.exists(report_path):
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)

    if not os.path.exists(master_path):
        print(f"Error: Master SKU file not found: {master_path}")
        sys.exit(1)

    print(f"1. Reading P&L Report: {report_path}")
    try:
        df_pnl, pnl_meta = extract_pnl_data_direct(report_path)
    except Exception as e:
        print(f"P&L Extraction Failed: {e}")
        sys.exit(1)

    print(f"   - Target Sheet:  {pnl_meta['sheet_name']}")
    print(f"   - Extracted Rows: {pnl_meta['total_rows']:,}")
    print(f"   - Gross Units:   {pnl_meta['total_gross']:,.0f}")
    print(f"   - RTO Units:     {pnl_meta['total_rto']:,.0f}")
    print(f"   - RVP Units:     {pnl_meta['total_rvp']:,.0f}")
    print(f"   - Cancelled:     {pnl_meta['total_cancelled']:,.0f}")
    print(f"   - Net Units:     {pnl_meta['total_net']:,.0f}")
    try:
        print(f"   - Bank Settlement: ₹{pnl_meta['total_bank_settlement']:,.2f}")
    except UnicodeEncodeError:
        print(f"   - Bank Settlement: INR {pnl_meta['total_bank_settlement']:,.2f}")

    if pnl_meta['balance_equation_holds']:
        print("   [VALIDATION PASSED] Gross - RTO - RVP - Cancelled = Net Units holds for EVERY row!")

    print(f"\n2. Loading Master SKU Sheet: {master_path}")
    try:
        master_lookup, master_conflicts = load_master_sku_sheet(master_path, filename=master_path)
    except Exception as e:
        print(f"Master Sheet Loading Failed: {e}")
        sys.exit(1)

    print(f"   - Master Unique SKUs Indexed: {len(master_lookup):,}")

    print("\n3. Enriching P&L Data and Computing Profit & Cost Analysis...")
    df_final, info = enrich_pnl_data(df_pnl, master_lookup, master_conflicts)
    df_profit = compute_profit_analysis_df(df_final)

    tot_cost = df_profit['Net Production Cost [ Unit * ]'].sum()
    tot_profit = df_profit['PROFIT [ Bank Settelement - Net Production Cost ]'].sum()

    print(f"   - Matched Rows:            {info['matched_count']} of {info['total_rows']}")
    print(f"   - Unmatched Rows:          {info['unmatched_count']}")
    if info['unmatched_skus']:
        print(f"     Unmatched List:          {', '.join(info['unmatched_skus'])}")

    print(f"   - Conflicting Master SKUs: {info['conflicts_count']}")
    for norm_k, records in info['conflicts_in_report'].items():
        print(f"     * SKU: {records[0]['raw_sku']} (used 1st entry: {records[0]['STYLE NAME']} / {records[0]['PAYOUT']})")

    try:
        print(f"   - Total Net Production Cost: ₹{tot_cost:,.2f}")
        print(f"   - Total Net PROFIT:          ₹{tot_profit:,.2f}")
    except UnicodeEncodeError:
        print(f"   - Total Net Production Cost: INR {tot_cost:,.2f}")
        print(f"   - Total Net PROFIT:          INR {tot_profit:,.2f}")

    print(f"\n4. Saving Multi-Sheet Output Excel: {output_path}")
    try:
        save_styled_excel_file(df_final, output_path, df_profit=df_profit)
        print(f"   Successfully wrote Excel to: {output_path}")
        print("   - Sheet 1: 'Profit & Cost Analysis' (2-row header: RTO/RVP/Cancelled, Net Production Cost, PROFIT)")
        print("   - Sheet 2: 'SKU Summary'")
    except Exception as e:
        print(f"Failed to save Excel: {e}")
        sys.exit(1)

    print("=" * 75)


def run_cli_standalone(report_path, output_path):
    """Executes P&L extraction standalone without master SKU sheet."""
    _reconfigure_utf8()

    print("=" * 75)
    print(" FLIPKART AUTOMATION - SKU Extractor Direct Rows (CLI)")
    print("=" * 75)

    if not os.path.exists(report_path):
        print(f"Error: Report file not found: {report_path}")
        sys.exit(1)

    print(f"1. Reading P&L Report: {report_path}")
    try:
        df_pnl, pnl_meta = extract_pnl_data_direct(report_path)
    except Exception as e:
        print(f"P&L Extraction Failed: {e}")
        sys.exit(1)

    print(f"   - Target Sheet:  {pnl_meta['sheet_name']}")
    print(f"   - Extracted Rows: {pnl_meta['total_rows']:,}")
    print(f"   - Gross Units:   {pnl_meta['total_gross']:,.0f}")
    print(f"   - RTO Units:     {pnl_meta['total_rto']:,.0f}")
    print(f"   - RVP Units:     {pnl_meta['total_rvp']:,.0f}")
    print(f"   - Cancelled:     {pnl_meta['total_cancelled']:,.0f}")
    print(f"   - Net Units:     {pnl_meta['total_net']:,.0f}")
    try:
        print(f"   - Bank Settlement: ₹{pnl_meta['total_bank_settlement']:,.2f}")
    except UnicodeEncodeError:
        print(f"   - Bank Settlement: INR {pnl_meta['total_bank_settlement']:,.2f}")

    if pnl_meta['balance_equation_holds']:
        print("   [VALIDATION PASSED] Gross - RTO - RVP - Cancelled = Net Units holds for EVERY row!")

    df_profit = compute_profit_analysis_df(df_pnl)

    print(f"\n2. Saving Multi-Sheet Output Excel: {output_path}")
    try:
        save_styled_excel_file(df_pnl, output_path, df_profit=df_profit)
        print(f"   Successfully wrote Excel to: {output_path}")
        print("   - Sheet 1: 'Profit & Cost Analysis'")
        print("   - Sheet 2: 'SKU Summary'")
    except Exception as e:
        print(f"Failed to save Excel: {e}")
        sys.exit(1)

    print("=" * 75)


def cli_entry_point():
    """Main CLI entry point for console commands."""
    args = [a for a in sys.argv[1:] if not a.startswith("--server.") and not a.startswith("--browser.")]

    if len(args) == 3 and not any(a.startswith("-") for a in args):
        run_cli_enriched(args[0], args[1], args[2])
    elif len(args) == 2 and not any(a.startswith("-") for a in args):
        run_cli_standalone(args[0], args[1])
    else:
        print("Usage:")
        print("  Enriched:   python run_cli.py report.xlsx master.csv output.xlsx")
        print("  P&L Only:   python run_cli.py report.xlsx output.xlsx")
        sys.exit(0)


if __name__ == '__main__':
    cli_entry_point()
