"""
Profit, Production Cost, Margin, and KPI calculations.
"""
import pandas as pd
from src.config import PROFIT_ANALYSIS_COLUMNS


def compute_profit_analysis_df(df):
    """
    Computes Net Production Cost and Profit row-by-row:
      - Net Production Cost [ Unit * ] = Net Units * Payout
      - PROFIT [ Bank Settlement - Net Production Cost ] = Bank Settlement - Net Production Cost

    Returns:
        pd.DataFrame: 11-column DataFrame conforming to PROFIT_ANALYSIS_COLUMNS.
    """
    df_out = df.copy()

    payout = pd.to_numeric(df_out['PAYOUT'], errors='coerce').fillna(0.0) if 'PAYOUT' in df_out.columns else 0.0
    net_units = pd.to_numeric(df_out['Net Units'], errors='coerce').fillna(0.0)
    bank_settlement = pd.to_numeric(df_out['Bank Settlement'], errors='coerce').fillna(0.0)

    net_cost = net_units * payout
    profit = bank_settlement - net_cost

    df_out['Style name'] = df_out['STYLE NAME'] if 'STYLE NAME' in df_out.columns else ""
    df_out['Payout'] = df_out['PAYOUT'] if 'PAYOUT' in df_out.columns else 0.0
    df_out['Net Production Cost [ Unit * ]'] = net_cost
    df_out['Bank Settlement [Projected] (INR)'] = bank_settlement
    df_out['PROFIT [ Bank Settelement - Net Production Cost ]'] = profit

    return df_out[PROFIT_ANALYSIS_COLUMNS].copy()


def calculate_kpis(pnl_meta, df_profit, has_master=True):
    """
    Calculates executive business metrics and financial KPIs from extracted and profit DataFrames.

    Returns:
        dict: Structured KPI dictionary for dashboard cards and reporting.
    """
    total_bank = float(pnl_meta['total_bank_settlement'])
    total_cost = float(df_profit['Net Production Cost [ Unit * ]'].sum())
    total_profit = float(df_profit['PROFIT [ Bank Settelement - Net Production Cost ]'].sum())
    profit_margin = (total_profit / total_bank * 100.0) if total_bank > 0 else 0.0

    gross_units = float(pnl_meta['total_gross'])
    net_units = float(pnl_meta['total_net'])
    rto_units = float(pnl_meta['total_rto'])
    rvp_units = float(pnl_meta['total_rvp'])
    cancelled_units = float(pnl_meta['total_cancelled'])
    lost_units = rto_units + rvp_units + cancelled_units

    fulfillment_rate = (net_units / gross_units * 100.0) if gross_units > 0 else 0.0
    loss_rate = (lost_units / gross_units * 100.0) if gross_units > 0 else 0.0

    # Count profitable vs loss-making SKUs
    profit_series = df_profit['PROFIT [ Bank Settelement - Net Production Cost ]']
    profitable_count = int((profit_series > 0.01).sum())
    loss_count = int((profit_series < -0.01).sum())
    breakeven_count = int(len(df_profit) - profitable_count - loss_count)

    # Top performing SKU and Top loss SKU
    top_profit_sku = None
    top_loss_sku = None
    if len(df_profit) > 0:
        sorted_by_profit = df_profit.sort_values(
            by='PROFIT [ Bank Settelement - Net Production Cost ]',
            ascending=False
        )
        best_row = sorted_by_profit.iloc[0]
        top_profit_sku = {
            'sku': best_row['SKU Name'],
            'style': best_row['Style name'],
            'profit': float(best_row['PROFIT [ Bank Settelement - Net Production Cost ]'])
        }

        worst_row = sorted_by_profit.iloc[-1]
        top_loss_sku = {
            'sku': worst_row['SKU Name'],
            'style': worst_row['Style name'],
            'profit': float(worst_row['PROFIT [ Bank Settelement - Net Production Cost ]'])
        }

    return {
        'total_rows': int(pnl_meta['total_rows']),
        'gross_units': gross_units,
        'net_units': net_units,
        'rto_units': rto_units,
        'rvp_units': rvp_units,
        'cancelled_units': cancelled_units,
        'lost_units': lost_units,
        'fulfillment_rate': fulfillment_rate,
        'loss_rate': loss_rate,
        'total_bank_settlement': total_bank,
        'total_cost': total_cost,
        'total_profit': total_profit,
        'profit_margin': profit_margin,
        'profitable_count': profitable_count,
        'loss_count': loss_count,
        'breakeven_count': breakeven_count,
        'top_profit_sku': top_profit_sku,
        'top_loss_sku': top_loss_sku,
        'has_master': has_master,
        'equation_holds': pnl_meta['balance_equation_holds'],
        'invalid_rows_count': pnl_meta['invalid_rows_count']
    }
