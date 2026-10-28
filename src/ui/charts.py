"""
Interactive charts and visualizations using Altair and Streamlit.
Provides executive visual summaries of unit loss breakdown,
top profitable SKUs, and profit vs cost relationships.
"""
import streamlit as st
import pandas as pd
import altair as alt


def render_returns_funnel_chart(kpis):
    """
    Renders an interactive unit breakdown chart showing Net Fulfilled,
    RTO Logistics Returns, RVP Customer Returns, and Cancelled Units.
    """
    breakdown_data = pd.DataFrame({
        'Category': [
            'Net Fulfilled Units',
            'RTO (Logistics Return)',
            'RVP (Customer Return)',
            'Cancelled Units'
        ],
        'Units': [
            kpis['net_units'],
            kpis['rto_units'],
            kpis['rvp_units'],
            kpis['cancelled_units']
        ],
        'Type': ['Fulfilled', 'Lost / Return', 'Lost / Return', 'Lost / Return']
    })

    color_scale = alt.Scale(
        domain=[
            'Net Fulfilled Units',
            'RTO (Logistics Return)',
            'RVP (Customer Return)',
            'Cancelled Units'
        ],
        range=['#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    )

    chart = alt.Chart(breakdown_data).mark_bar(cornerRadiusTopRight=6, cornerRadiusBottomRight=6).encode(
        y=alt.Y('Category:N', sort=None, title=None, axis=alt.Axis(labelFontSize=12, labelFontWeight='bold')),
        x=alt.X('Units:Q', title="Total Units", axis=alt.Axis(grid=True)),
        color=alt.Color('Category:N', scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip('Category:N', title='Category'),
            alt.Tooltip('Units:Q', format=',.0f', title='Units')
        ]
    ).properties(
        height=180,
        title=alt.TitleParams(
            text="Unit Volume Distribution (Gross Dispatched Breakdown)",
            fontSize=13,
            color="#475569"
        )
    )

    st.altair_chart(chart, use_container_width=True)


def render_top_skus_chart(df_profit, n=10):
    """
    Renders Top N Most Profitable and Top N Loss-making SKUs.
    """
    if len(df_profit) == 0:
        return

    profit_col = 'PROFIT [ Bank Settelement - Net Production Cost ]'
    sorted_df = df_profit.sort_values(by=profit_col, ascending=False)

    top_profitable = sorted_df[sorted_df[profit_col] > 0].head(n).copy()
    top_loss = sorted_df[sorted_df[profit_col] < 0].tail(n).copy()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"##### 🏆 Top {len(top_profitable)} Profitable SKUs")
        if not top_profitable.empty:
            top_profitable['Display SKU'] = top_profitable['SKU Name'].apply(
                lambda x: x[:22] + "..." if len(x) > 22 else x
            )
            chart_profit = alt.Chart(top_profitable).mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#10b981").encode(
                y=alt.Y('Display SKU:N', sort='-x', title=None),
                x=alt.X(f'{profit_col}:Q', title="Net Profit (₹)"),
                tooltip=[
                    alt.Tooltip('SKU Name:N', title='SKU'),
                    alt.Tooltip('Style name:N', title='Style'),
                    alt.Tooltip(f'{profit_col}:Q', format='₹,.2f', title='Profit')
                ]
            ).properties(height=260)
            st.altair_chart(chart_profit, use_container_width=True)
        else:
            st.info("No profitable SKUs identified in this dataset.")

    with col2:
        st.markdown(f"##### ⚠️ Top {len(top_loss)} Loss-Making SKUs")
        if not top_loss.empty:
            top_loss['Display SKU'] = top_loss['SKU Name'].apply(
                lambda x: x[:22] + "..." if len(x) > 22 else x
            )
            # sort ascending so largest negative is prominent
            chart_loss = alt.Chart(top_loss).mark_bar(cornerRadiusTopLeft=4, cornerRadiusBottomLeft=4, color="#ef4444").encode(
                y=alt.Y('Display SKU:N', sort='x', title=None),
                x=alt.X(f'{profit_col}:Q', title="Net Loss (₹)"),
                tooltip=[
                    alt.Tooltip('SKU Name:N', title='SKU'),
                    alt.Tooltip('Style name:N', title='Style'),
                    alt.Tooltip(f'{profit_col}:Q', format='₹,.2f', title='Profit')
                ]
            ).properties(height=260)
            st.altair_chart(chart_loss, use_container_width=True)
        else:
            st.success("🎉 No loss-making SKUs in this report! All items positive or break-even.")


def render_profit_distribution_chart(df_profit):
    """
    Renders scatter / comparative chart between Bank Settlement and Net Production Cost.
    """
    if len(df_profit) == 0:
        return

    sample_size = min(len(df_profit), 250)
    sample_df = df_profit.sample(sample_size, random_state=42) if len(df_profit) > sample_size else df_profit.copy()

    profit_col = 'PROFIT [ Bank Settelement - Net Production Cost ]'
    sample_df['Status'] = sample_df[profit_col].apply(
        lambda x: 'Profitable' if x > 0 else ('Loss' if x < 0 else 'Break-even')
    )

    chart = alt.Chart(sample_df).mark_circle(size=70, opacity=0.7).encode(
        x=alt.X('Net Production Cost [ Unit * ]:Q', title="Net Production Cost (₹)"),
        y=alt.Y('Bank Settlement [Projected] (INR):Q', title="Bank Settlement (₹)"),
        color=alt.Color('Status:N', scale=alt.Scale(
            domain=['Profitable', 'Loss', 'Break-even'],
            range=['#10b981', '#ef4444', '#94a3b8']
        )),
        tooltip=[
            alt.Tooltip('SKU Name:N', title='SKU'),
            alt.Tooltip('Style name:N', title='Style'),
            alt.Tooltip('Bank Settlement [Projected] (INR):Q', format='₹,.2f', title='Settlement'),
            alt.Tooltip('Net Production Cost [ Unit * ]:Q', format='₹,.2f', title='Cost'),
            alt.Tooltip(f'{profit_col}:Q', format='₹,.2f', title='Profit')
        ]
    ).properties(
        height=280,
        title=alt.TitleParams(
            text=f"Settlement vs Production Cost Correlation (Sample of {sample_size} SKUs)",
            fontSize=13,
            color="#475569"
        )
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
