import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Company, FinancialStatement, DATABASE_URL
import json

# Database Connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

st.set_page_config(page_title="WindBorne Finance", layout="wide")

# --- CSS & Aesthetics ---
# --- CSS & Aesthetics ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #ffffff;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important; /* Force white text for metric values */
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] {
        color: #b0b0b0 !important; /* Lighter gray for labels */
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); /* Stronger shadow */
        border: 1px solid #3d3d3d; /* Subtle border */
        transition: transform 0.2s ease, box-shadow 0.2s ease; /* Hover transition */
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.4);
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Smooth Scroll */
    html {
        scroll-behavior: smooth;
    }
    
    /* Fade In Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .block-container {
        animation: fadeIn 0.5s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def get_data(ticker):
    session = SessionLocal()
    company = session.query(Company).filter_by(ticker=ticker).first()
    if not company:
        session.close()
        return None, None
    
    statements = session.query(FinancialStatement).filter_by(company_id=company.id).all()
    session.close()
    
    data = []
    for stmt in statements:
        row = stmt.data
        row['statement_type'] = stmt.statement_type
        row['fiscalDateEnding'] = str(stmt.fiscal_date_ending)
        data.append(row)
        
    return company, pd.DataFrame(data)

def calculate_metrics(df):
    # Filter by statement type
    income = df[df['statement_type'] == 'INCOME_STATEMENT'].copy()
    balance = df[df['statement_type'] == 'BALANCE_SHEET'].copy()
    
    # Convert columns to numeric
    # We define which columns belong to which statement to avoid unnecessary zero-filling
    income_cols = ['totalRevenue', 'grossProfit', 'operatingIncome', 'netIncome']
    balance_cols = ['totalCurrentAssets', 'totalCurrentLiabilities', 'totalAssets', 'inventory']
    
    # Process Income Statement
    for col in income_cols:
        if col not in income.columns:
            income[col] = 0
        income[col] = pd.to_numeric(income[col], errors='coerce').fillna(0)

    # Process Balance Sheet
    for col in balance_cols:
        if col not in balance.columns:
            balance[col] = 0
        balance[col] = pd.to_numeric(balance[col], errors='coerce').fillna(0)
    
    # Merge on fiscalDateEnding
    # We don't need to force all columns in both, so suffixes shouldn't happen for unique columns
    # But just in case, we handle it.
    merged = pd.merge(income, balance, on='fiscalDateEnding', suffixes=('_inc', '_bal'), how='inner')
    
    metrics = []
    for _, row in merged.iterrows():
        # Helper to get column value even if suffixed
        def get_val(col, suffix):
            if col in row: return row[col]
            if f"{col}{suffix}" in row: return row[f"{col}{suffix}"]
            return 0

        rev = get_val('totalRevenue', '_inc')
        gp = get_val('grossProfit', '_inc')
        op_inc = get_val('operatingIncome', '_inc')
        net_inc = get_val('netIncome', '_inc')
        
        curr_assets = get_val('totalCurrentAssets', '_bal')
        curr_liab = get_val('totalCurrentLiabilities', '_bal')
        assets = get_val('totalAssets', '_bal')
        
        # Profitability
        gross_margin = (gp / rev) * 100 if rev else 0
        op_margin = (op_inc / rev) * 100 if rev else 0
        net_margin = (net_inc / rev) * 100 if rev else 0
        
        # Liquidity
        current_ratio = curr_assets / curr_liab if curr_liab else 0
        
        # Efficiency (Asset Turnover)
        asset_turnover = rev / assets if assets else 0
        
        metrics.append({
            'Year': row['fiscalDateEnding'],
            'Gross Margin %': round(gross_margin, 2),
            'Operating Margin %': round(op_margin, 2),
            'Net Margin %': round(net_margin, 2),
            'Current Ratio': round(current_ratio, 2),
            'Asset Turnover': round(asset_turnover, 2),
            'Revenue': rev,
            'Net Income': net_inc
        })
        
    return pd.DataFrame(metrics).sort_values('Year')

# --- Main App ---
st.title("WindBorne Finance Automation")
st.caption("Developed by Sergio Fernando Gonázalez Aguirre")

# Sidebar
st.sidebar.header("Configuration")
selected_ticker = st.sidebar.selectbox("Select Company", ["TEL", "ST", "DD"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Developed by:**  
Sergio Fernando Gonázalez Aguirre  
**Email:**  
sergino.8746@gmail.com
""")

# Data Loading
company, raw_df = get_data(selected_ticker)

if company and not raw_df.empty:
    metrics_df = calculate_metrics(raw_df)
    
    # Header
    st.header(f"{company.name} ({company.ticker})")
    
    # Key Metrics (Latest Year)
    latest = metrics_df.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Revenue", f"${latest['Revenue']:,.0f}")
    col2.metric("Gross Margin", f"{latest['Gross Margin %']}%")
    col3.metric("Net Margin", f"{latest['Net Margin %']}%")
    col4.metric("Current Ratio", f"{latest['Current Ratio']}")
    
    # Charts
    st.subheader("Profitability Trends")
    fig_margin = px.line(metrics_df, x='Year', y=['Gross Margin %', 'Operating Margin %', 'Net Margin %'], 
                         markers=True, title="Margin Analysis")
    st.plotly_chart(fig_margin, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Revenue Growth")
        fig_rev = px.bar(metrics_df, x='Year', y='Revenue', title="Annual Revenue")
        st.plotly_chart(fig_rev, use_container_width=True)
        
    with col_b:
        st.subheader("Liquidity & Efficiency")
        fig_liq = go.Figure()
        fig_liq.add_trace(go.Bar(x=metrics_df['Year'], y=metrics_df['Current Ratio'], name='Current Ratio'))
        fig_liq.add_trace(go.Scatter(x=metrics_df['Year'], y=metrics_df['Asset Turnover'], name='Asset Turnover', yaxis='y2'))
        fig_liq.update_layout(title="Current Ratio vs Asset Turnover", 
                              yaxis=dict(title="Ratio"),
                              yaxis2=dict(title="Turnover", overlaying='y', side='right'))
        st.plotly_chart(fig_liq, use_container_width=True)

    # Raw Data Expander
    with st.expander("View Calculated Metrics Data"):
        st.dataframe(metrics_df)

else:
    st.warning("No data found. Please run the ETL pipeline first.")

# --- Part 4: Explainers ---
st.markdown("---")
st.header("Part 4: Production Strategy")

with st.expander("1. Scheduling (n8n)"):
    st.markdown("""
    **Strategy:** Use n8n's `Cron` node to trigger the workflow monthly.
    
    **Workflow:**
    1. **Trigger:** Cron (Monthly, 1st day).
    2. **Get Tickers:** Query `companies` table.
    3. **Split In Batches:** Process 3-5 companies at a time to respect API limits (or use a queue).
    4. **HTTP Request:** Call Alpha Vantage API.
    5. **Postgres:** Upsert data into `financial_statements`.
    6. **Slack:** Send success/failure notification.
    """)

with st.expander("2. Handling 100 Companies (Rate Limits)"):
    st.markdown("""
    **Challenge:** 100 companies * 3 reports = 300 calls. Limit is 25/day.
    
    **Solution:**
    - **Batching:** Process ~8 companies per day (24 calls). It will take ~12 days to update all 100.
    - **Queue System:** Use a `job_queue` table. A worker script runs daily via Cron, picks top 8 'stale' companies, updates them, and marks them as updated.
    - **Upgrade:** For a real production system, upgrading the API plan is the logical choice ($49/mo for 75 calls/min).
    """)

with st.expander("3. Google Sheets Sync"):
    st.markdown("""
    **Approach:** Sync *calculated metrics* (not raw JSON) to Google Sheets.
    
    **Why?** Execs need clean, analyzed numbers, not raw API dumps.
    
    **Implementation:**
    - **n8n Google Sheets Node:** After the ETL step, append the new metrics to a Master Sheet.
    - **Pros:** Easy access, familiar UI for execs.
    - **Cons:** Manual sync can break if sheet structure changes.
    """)

with st.expander("4. Monitoring & Alerts"):
    st.markdown("""
    **What breaks first?** API Rate limits or API schema changes.
    
    **Monitoring:**
    - **Data Validation:** If `Revenue == 0` or `TotalAssets` is missing -> Alert.
    - **API Status:** Check for "Information" or "Note" keys in API response (Alpha Vantage error messages).
    - **Alerts:** n8n Slack/Email node on workflow failure.
    """)
