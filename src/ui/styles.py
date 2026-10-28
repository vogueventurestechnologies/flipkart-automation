"""
Modern White Background CSS styling system for Flipkart P&L Extractor.
Clean white aesthetic with subtle borders, elevated cards, and crisp contrast.
"""


def get_custom_css():
    """Returns the CSS styling injected into the Streamlit application."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap');

        /* Force Pure White Background Across All Streamlit Containers */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container {
            background-color: #ffffff !important;
            background: #ffffff !important;
            color: #0f172a !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            letter-spacing: -0.01em;
        }

        /* Top Bar & Sidebar Clean Backgrounds */
        [data-testid="stHeader"] {
            background-color: #ffffff !important;
            background: #ffffff !important;
            border-bottom: 1px solid #f1f5f9;
        }

        /* Hide Sidebar Completely */
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
            letter-spacing: -0.02em;
            color: #0f172a !important;
        }

        /* Streamlit main block padding refinement */
        .block-container {
            padding-top: 1.25rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1400px;
        }

        /* Clean White Hero Header */
        .hero-banner {
            background: #ffffff !important;
            border-radius: 16px;
            padding: 1.75rem 2rem;
            color: #0f172a !important;
            margin-bottom: 1.25rem;
            position: relative;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
            border: 1px solid #e2e8f0;
        }

        .hero-title-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .hero-title-group {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .hero-icon-badge {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.7rem;
        }

        .hero-title {
            margin: 0 !important;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: #0f172a !important;
        }

        .hero-subtitle {
            margin: 0.35rem 0 0 0;
            color: #475569 !important;
            font-size: 0.95rem;
            font-weight: 400;
            max-width: 800px;
            line-height: 1.5;
        }

        .badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.78rem;
            font-weight: 600;
            background: #f8fafc;
            color: #1e3a8a;
            border: 1px solid #cbd5e1;
        }

        /* Notice & Feature Highlight Cards */
        .feature-ribbon {
            background: #f0fdf4 !important;
            border: 1px solid #bbf7d0 !important;
            border-left: 4px solid #16a34a !important;
            border-radius: 0 10px 10px 0;
            padding: 0.85rem 1.25rem;
            color: #14532d;
            font-size: 0.9rem;
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }

        /* KPI Metric Cards - Clean White */
        .metric-card-pro {
            background: #ffffff !important;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 2px 6px -1px rgba(15, 23, 42, 0.05);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 115px;
        }

        .metric-card-pro:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px -4px rgba(15, 23, 42, 0.08);
            border-color: #cbd5e1;
        }

        .metric-card-pro::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
        }

        .card-accent-blue::before { background: #2563eb; }
        .card-accent-green::before { background: #16a34a; }
        .card-accent-purple::before { background: #7c3aed; }
        .card-accent-amber::before { background: #d97706; }
        .card-accent-rose::before { background: #e11d48; }
        .card-accent-cyan::before { background: #0891b2; }

        .metric-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .metric-label-pro {
            font-size: 0.76rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
        }

        .metric-icon-small {
            font-size: 1.15rem;
            opacity: 0.85;
        }

        .metric-value-pro {
            font-family: 'Outfit', sans-serif;
            font-size: 1.65rem;
            font-weight: 700;
            color: #0f172a !important;
            margin: 0.4rem 0 0.2rem 0;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }

        .metric-sub-pro {
            font-size: 0.78rem;
            color: #64748b;
            display: flex;
            align-items: center;
            gap: 0.35rem;
        }

        .sub-pill-positive {
            color: #15803d;
            background: #dcfce7;
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            font-weight: 600;
        }

        .sub-pill-negative {
            color: #b91c1c;
            background: #fee2e2;
            padding: 0.15rem 0.45rem;
            border-radius: 6px;
            font-weight: 600;
        }

        /* Validation Box */
        .validation-card {
            background: #f0fdf4 !important;
            border: 1px solid #86efac;
            border-radius: 12px;
            padding: 1rem 1.4rem;
            margin: 1.2rem 0;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 1px 4px rgba(34, 197, 94, 0.06);
        }

        .validation-card-icon {
            font-size: 1.8rem;
            color: #16a34a;
        }

        .validation-card-title {
            font-weight: 700;
            color: #14532d;
            font-size: 0.95rem;
            margin-bottom: 0.2rem;
        }

        .validation-card-formula {
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-size: 0.84rem;
            color: #166534;
            background: #ffffff;
            padding: 0.25rem 0.65rem;
            border-radius: 6px;
            border: 1px solid #bbf7d0;
            display: inline-block;
        }

        /* Custom Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background-color: #f8fafc !important;
            padding: 0.35rem;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 9px;
            padding: 0.5rem 1.2rem;
            font-weight: 600;
            color: #64748b;
            border: none;
            background: transparent;
            transition: all 0.15s ease;
        }

        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            color: #1e3a8a !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
        }

        /* Upload Zone White Styling */
        [data-testid="stFileUploader"] {
            background: #ffffff !important;
            border: 1px dashed #cbd5e1;
            border-radius: 12px;
            padding: 0.75rem 1rem;
            transition: border-color 0.2s ease;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: #2563eb;
        }

        /* Download Card Section */
        .download-box {
            background: #ffffff !important;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.25rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03);
            margin-top: 1rem;
        }

        .download-header {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
    </style>
    """
