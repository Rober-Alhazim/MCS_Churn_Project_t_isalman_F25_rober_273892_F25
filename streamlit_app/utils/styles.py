# streamlit_app/utils/styles.py
"""
CSS Styles موحد لجميع صفحات التطبيق
"""

def get_base_styles() -> str:
    """الأنماط الأساسية المشتركة"""
    return """
    <style>
    /* ============================================ */
    /* 🎨 الألوان الأساسية */
    /* ============================================ */
    :root {
        --primary-color: #00d4ff;
        --secondary-color: #00ffb3;
        --bg-dark: #1a1a2e;
        --bg-card: rgba(10, 25, 41, 0.6);
        --text-primary: #e8f1f5;
        --text-secondary: #b8d4e3;
        --border-color: rgba(0, 212, 255, 0.3);
    }
    
    /* ============================================ */
    /* 🏷️ العناوين */
    /* ============================================ */
    h1 {
        background: linear-gradient(90deg, #00d4ff, #00ffb3, #00d4ff);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        text-align: center;
        padding: 1.5rem 0;
        font-size: 2rem !important;
        animation: shine 3s linear infinite;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    h2, h3 {
        color: #00d4ff !important;
        font-weight: 700 !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
        border-bottom: 1px solid rgba(0, 212, 255, 0.3);
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }
    
    h3 {
        font-size: 1.3rem !important;
    }
    
    /* ============================================ */
    /*  Metrics */
    /* ============================================ */
    [data-testid="stMetric"] {
        background: rgba(0, 212, 255, 0.05);
        border: 1px solid rgba(0, 212, 255, 0.25);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        margin: 0.5rem 0;
        min-width: 100%;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        background: rgba(0, 212, 255, 0.1);
        border-color: #00ffb3;
        transform: translateY(-2px);
    }
    
    [data-testid="stMetricLabel"] {
        color: #b8d4e3 !important;
        font-weight: 600;
        font-size: 1rem !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
        line-height: 1.4 !important;
        text-align: center !important;
        width: 100% !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #00ffb3 !important;
        font-weight: 900 !important;
        font-size: 1.6rem !important;
        text-align: center !important;
        margin-top: 0.3rem !important;
        white-space: nowrap !important;
    }
    
    /* ============================================ */
    /*  الأزرار */
    /* ============================================ */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff, #00ffb3) !important;
        color: #1a1a2e !important;
        font-weight: 900 !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-size: 1rem !important;
        font-family: 'Cairo', sans-serif !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.5) !important;
    }
    
    /* ============================================ */
    /* 📦 Expander */
    /* ============================================ */
    .streamlit-expanderHeader {
        background: rgba(0, 212, 255, 0.1) !important;
        color: #00d4ff !important;
        font-weight: 700 !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 0.8rem 1.2rem !important;
        font-size: 1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(0, 212, 255, 0.2) !important;
        border-color: #00ffb3 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(10, 25, 41, 0.5);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-top: none;
        border-radius: 0 0 10px 10px;
        padding: 1.2rem;
        font-size: 0.95rem !important;
    }
    
    /* ============================================ */
    /* 💬 Alerts */
    /* ============================================ */
    .stAlert {
        border-radius: 10px !important;
        font-size: 0.95rem !important;
        padding: 1rem 1.2rem !important;
        border: 1px solid !important;
    }
    
    .stAlert-info {
        background: rgba(0, 212, 255, 0.1) !important;
        border-color: rgba(0, 212, 255, 0.4) !important;
        color: #b8e8ff !important;
    }
    
    .stAlert-success {
        background: rgba(0, 255, 179, 0.1) !important;
        border-color: rgba(0, 255, 179, 0.4) !important;
        color: #b8ffd9 !important;
    }
    
    .stAlert-error {
        background: rgba(255, 82, 82, 0.15) !important;
        border-color: rgba(255, 82, 82, 0.4) !important;
        color: #ffb3b3 !important;
    }
    
    .stAlert-warning {
        background: rgba(255, 215, 0, 0.1) !important;
        border-color: rgba(255, 215, 0, 0.4) !important;
        color: #ffe8a0 !important;
    }
    
    /* ============================================ */
    /* 📊 DataFrames */
    /* ============================================ */
    .stDataFrame {
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* ============================================ */
    /* 🎨 Sidebar Navigation */
    /* ============================================ */
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
        color: #ffffff !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        padding: 1rem 1.5rem !important;
        margin: 0 !important;
        border-radius: 10px !important;
        background: rgba(0, 212, 255, 0.08) !important;
        border: 1px solid rgba(0, 212, 255, 0.25) !important;
        transition: all 0.3s ease !important;
        direction: rtl !important;
        text-align: right !important;
        display: block !important;
        text-decoration: none !important;
        letter-spacing: 0.5px !important;
        line-height: 1.4 !important;
    }
    
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 255, 179, 0.1)) !important;
        border-color: #00d4ff !important;
        color: #00d4ff !important;
        transform: translateY(-2px) !important;
    }
    
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.25), rgba(0, 255, 179, 0.15)) !important;
        border: 2px solid #00ffb3 !important;
        color: #00ffb3 !important;
        font-weight: 900 !important;
        box-shadow: 0 4px 15px rgba(0, 255, 179, 0.3) !important;
    }
    
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] span,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] p,
    section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] div {
        color: #00ffb3 !important;
        font-weight: 900 !important;
    }
    
    /* ============================================ */
    /* 📜 Scrollbar */
    /* ============================================ */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d4ff, #00ffb3);
        border-radius: 10px;
    }
    
    /* ============================================ */
    /* 🖼️ Sidebar Image */
    /* ============================================ */
    section[data-testid="stSidebar"] img {
        display: block;
        margin: 2rem auto 1rem auto;
        padding: 0.6rem;
        background: rgba(0, 212, 255, 0.1);
        border-radius: 16px;
        border: 2px solid rgba(0, 212, 255, 0.3);
        width: clamp(60px, 15vw, 100px) !important;
        height: auto !important;
        max-width: 100% !important;
        object-fit: contain;
    }
    
    /* ============================================ */
    /* 📝 General Text */
    /* ============================================ */
    .stMarkdown {
        color: #e8f1f5;
        line-height: 1.8;
        font-size: 1rem !important;
    }
    
    .stMarkdown strong {
        color: #00ffb3;
    }
    
    .stCaption {
        color: #b8d4e3 !important;
        font-size: 0.9rem !important;
    }
    
    /* RTL */
    .stMarkdown, .stText, .stDataFrame, .stMetric,
    .stSidebar, .stButton, input, textarea, label,
    div[data-testid="stMarkdownContainer"], p, span, li {
        direction: rtl;
        text-align: right;
    }
    
    /* Sidebar titles */
    section[data-testid="stSidebar"] h2 {
        color: #00d4ff;
        font-weight: 700;
        text-align: center;
        font-size: 1.4rem !important;
        margin: 1rem 0;
    }
    
    section[data-testid="stSidebar"] h3 {
        color: #00ffb3;
        font-weight: 700;
        font-size: 1.1rem !important;
        margin: 1rem 0 0.5rem 0;
    }
    
    section[data-testid="stSidebar"] .stCaption {
        color: #ffd700 !important;
        font-weight: 600;
        text-align: center;
        padding: 0.5rem 0.8rem;
        background: rgba(255, 215, 0, 0.1);
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.95rem !important;
    }
    
    /* ============================================ */
    /* 📱 Responsive */
    /* ============================================ */
    @media (max-width: 768px) {
        h1 { font-size: 1.5rem !important; }
        .main .block-container { padding: 1rem !important; }
    }
    </style>
    """


def get_page_specific_styles(page_type: str = "default") -> str:
    """أنماط خاصة بكل صفحة"""
    styles = {
        "default": "",
        "charts": """
        <style>
        .stPlotlyChart {
            border: 1px solid rgba(0, 212, 255, 0.3) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            background: rgba(10, 25, 41, 0.4) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
            margin: 1rem 0 !important;
        }
        </style>
        """,
        "forms": """
        <style>
        .stNumberInput input, .stTextInput input, .stTextArea textarea {
            background: rgba(10, 25, 41, 0.6) !important;
            border: 1px solid rgba(0, 212, 255, 0.3) !important;
            border-radius: 8px !important;
            color: #e8f1f5 !important;
            padding: 0.6rem 1rem !important;
            font-size: 1rem !important;
            font-family: 'Cairo', sans-serif !important;
            transition: all 0.3s ease !important;
        }
        
        .stNumberInput input:focus, .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #00ffb3 !important;
            box-shadow: 0 0 10px rgba(0, 255, 179, 0.3) !important;
            outline: none !important;
        }
        
        .stNumberInput label, .stTextInput label, .stTextArea label {
            color: #00d4ff !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        </style>
        """
    }
    
    return styles.get(page_type, "")


def inject_styles(page_type: str = "default"):
    """حقن الأنماط في الصفحة"""
    import streamlit as st
    st.markdown(get_base_styles(), unsafe_allow_html=True)
    st.markdown(get_page_specific_styles(page_type), unsafe_allow_html=True)