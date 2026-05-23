import os
import time
import random
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import pandas as pd
import ta
import google.generativeai as genai

# Optional Plotly imports. TradingView is used as the main chart, but Plotly is kept
# available for future expansion and requirements compatibility.
try:
    import plotly.graph_objects as go  # noqa: F401
    from plotly.subplots import make_subplots  # noqa: F401
except Exception:
    go = None
    make_subplots = None

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="股票分析儀",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS: desktop + iPhone / mobile safe display
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');

:root {
    --bg: #f0f4f8;
    --surface: #ffffff;
    --surface2: #f8fafc;
    --border: #d0dce8;
    --accent: #2563eb;
    --accent2: #f97316;
    --text: #1e293b;
    --muted: #64748b;
    --danger: #dc2626;
    --safe: #16a34a;
    --warning: #d97706;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
    -webkit-text-size-adjust: 100%;
}

h1, h2, h3 { font-family: 'Manrope', sans-serif; color: var(--text); }

.main-title {
    font-family: 'Manrope', sans-serif;
    font-size: 2.55rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--accent);
    margin-bottom: 0.2rem;
}
.subtitle {
    color: var(--muted);
    font-size: 0.92rem;
    letter-spacing: 0.04em;
    margin-bottom: 1.4rem;
}

.metric-card, .panel-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    color: var(--text) !important;
}
.metric-label {
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted) !important;
    margin-bottom: 0.42rem;
}
.metric-value {
    font-family: 'Manrope', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}
.metric-value.positive { color: var(--safe) !important; -webkit-text-fill-color: var(--safe) !important; }
.metric-value.negative { color: var(--danger) !important; -webkit-text-fill-color: var(--danger) !important; }

.section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 0.82rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 1.65rem 0 0.9rem;
    padding-bottom: 0.45rem;
    border-bottom: 2px solid var(--border);
}

.indicator-badge {
    display: inline-block;
    padding: 0.34rem 0.75rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    margin: 0.22rem 0.18rem 0.22rem 0;
    white-space: nowrap;
}
.badge-bull { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.badge-bear { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.badge-neutral { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.badge-warning { background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }

.key-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.65rem;
    margin-top: 0.65rem;
}
.key-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.8rem;
    min-width: 0;
}
.key-name {
    font-size: 0.74rem;
    font-weight: 700;
    color: #64748b !important;
    margin-bottom: 0.28rem;
}
.key-value {
    font-family: 'Manrope', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #1e293b !important;
    -webkit-text-fill-color: #1e293b !important;
    opacity: 1 !important;
    visibility: visible !important;
    word-break: break-word;
}

.score-wrap {
    display: flex;
    gap: 0.9rem;
    align-items: center;
    flex-wrap: wrap;
}
.score-circle {
    width: 96px;
    height: 96px;
    border-radius: 999px;
    background: #eff6ff;
    border: 8px solid #bfdbfe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Manrope', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: #1d4ed8;
}
.score-text { flex: 1; min-width: 180px; color: var(--text); line-height: 1.75; }

.fund-table, .data-table {
    background: var(--surface);
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.fund-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.82rem 1.15rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
}
.fund-row:last-child { border-bottom: none; }
.fund-key { color: var(--muted); font-weight: 600; }
.fund-val { color: var(--text); font-weight: 800; text-align:right; }

.news-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent2);
    border-radius: 12px;
    padding: 0.95rem 1.1rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.news-title { font-size: 0.92rem; color: var(--text); font-weight: 600; line-height: 1.5; }

.ai-block {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 16px;
    padding: 1.35rem;
    line-height: 1.85;
    font-size: 0.95rem;
    color: #1e293b !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.08);
}

.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.62rem 1.6rem !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
}
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: 0.65rem 1rem !important;
}

.small-note { color:#64748b; font-size:0.76rem; line-height:1.5; }

@media (max-width: 768px) {
    .main-title { font-size: 2rem; }
    .subtitle { font-size: 0.86rem; margin-bottom: 1rem; }
    .metric-card, .panel-card { padding: 0.95rem; border-radius: 14px; }
    .metric-value { font-size: 1.22rem; }
    .key-grid { grid-template-columns: 1fr !important; gap: 0.5rem; }
    .key-value { font-size: 1.12rem !important; }
    .fund-row { padding: 0.75rem 0.9rem; font-size: 0.86rem; }
    .score-circle { width: 82px; height: 82px; font-size: 1.25rem; border-width: 7px; }
    div[data-testid="stHorizontalBlock"] { gap: 0.35rem; }
    iframe { max-width: 100% !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def fmt_large(n):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "N/A"
    try:
        n = float(n)
        if abs(n) >= 1e12:
            return f"${n/1e12:.2f}T"
        if abs(n) >= 1e9:
            return f"${n/1e9:.2f}B"
        if abs(n) >= 1e6:
            return f"${n/1e6:.2f}M"
        return f"${n:,.0f}"
    except Exception:
        return "N/A"


def fmt_pct(n):
    try:
        return f"{float(n)*100:.1f}%"
    except Exception:
        return "N/A"


def fmt_num(n, decimals=2):
    try:
        if n is None or pd.isna(n):
            return "N/A"
        return f"{float(n):,.{decimals}f}"
    except Exception:
        return "N/A"


def safe_float(x, default=None):
    try:
        if x is None or pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def get_signal(value, low, high, reverse=False):
    v = safe_float(value)
    if v is None:
        return "badge-neutral"
    if reverse:
        if v < low:
            return "badge-bull"
        if v > high:
            return "badge-bear"
    else:
        if v > high:
            return "badge-bull"
        if v < low:
            return "badge-bear"
    return "badge-neutral"


def normalize_hist(hist):
    if hist is None or hist.empty:
        return pd.DataFrame()
    if isinstance(hist.columns, pd.MultiIndex):
        hist.columns = hist.columns.get_level_values(0)
    needed = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in needed if c not in hist.columns]
    if missing:
        return pd.DataFrame()
    return hist[needed].dropna().copy()


@st.cache_data(ttl=300, show_spinner=False)
def get_history(ticker, period="6mo"):
    return yf.download(ticker, period=period, progress=False, auto_adjust=True)


@st.cache_data(ttl=600, show_spinner=False)
def get_stock_info(ticker):
    s = yf.Ticker(ticker)
    info = {}
    for _ in range(2):
        try:
            info = s.info or {}
            if info.get("marketCap") or info.get("trailingPE") or info.get("longName"):
                break
        except Exception:
            time.sleep(1 + random.uniform(0.2, 0.8))
    try:
        fi = s.fast_info
        fallback_map = {
            "currentPrice": getattr(fi, "last_price", None),
            "previousClose": getattr(fi, "previous_close", None),
            "marketCap": getattr(fi, "market_cap", None),
            "fiftyTwoWeekHigh": getattr(fi, "year_high", None),
            "fiftyTwoWeekLow": getattr(fi, "year_low", None),
        }
        for k, v in fallback_map.items():
            if not info.get(k) and v is not None:
                info[k] = v
    except Exception:
        pass
    return info


@st.cache_data(ttl=900, show_spinner=False)
def get_news_titles(ticker):
    try:
        news = yf.Ticker(ticker).news or []
        titles = []
        for n in news:
            title = n.get("content", {}).get("title") or n.get("title")
            if title:
                titles.append(title)
        return titles[:8]
    except Exception:
        return []


def add_indicators(df):
    df = df.copy()
    if len(df) < 55:
        return df
    df["RSI_14"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    macd = ta.trend.MACD(df["Close"])
    df["MACD_12_26_9"] = macd.macd()
    df["MACDs_12_26_9"] = macd.macd_signal()
    df["MACDh_12_26_9"] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(df["Close"], window=20, window_dev=2)
    df["BBU_20_2.0"] = bb.bollinger_hband()
    df["BBL_20_2.0"] = bb.bollinger_lband()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()
    return df


def build_tech(ticker):
    raw = get_history(ticker)
    df = normalize_hist(raw)
    if df.empty or len(df) < 55:
        return None, {}, {}, []
    info = get_stock_info(ticker)
    news_titles = get_news_titles(ticker)
    df = add_indicators(df)
    latest = df.iloc[-1]
    price = safe_float(info.get("currentPrice") or info.get("regularMarketPrice") or latest.get("Close"), safe_float(latest.get("Close"), 0))
    prev_close = safe_float(info.get("previousClose") or df.iloc[-2].get("Close"), safe_float(df.iloc[-2].get("Close"), price))
    change = price - prev_close if prev_close else 0
    change_pct = (change / prev_close * 100) if prev_close else 0
    support = safe_float(df["Low"].tail(20).min())
    resistance = safe_float(df["High"].tail(20).max())
    week_high = info.get("fiftyTwoWeekHigh") or "?"
    week_low = info.get("fiftyTwoWeekLow") or "?"
    tech = {
        "ticker": ticker,
        "price_float": price,
        "price": f"${price:.2f}",
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "rsi_float": safe_float(latest.get("RSI_14")),
        "rsi": fmt_num(latest.get("RSI_14"), 1),
        "macd_float": safe_float(latest.get("MACD_12_26_9")),
        "macd": fmt_num(latest.get("MACD_12_26_9"), 3),
        "signal_float": safe_float(latest.get("MACDs_12_26_9")),
        "signal": fmt_num(latest.get("MACDs_12_26_9"), 3),
        "ma20_float": safe_float(latest.get("MA20")),
        "ma20": fmt_num(latest.get("MA20"), 2),
        "ma50_float": safe_float(latest.get("MA50")),
        "ma50": fmt_num(latest.get("MA50"), 2),
        "bbu": fmt_num(latest.get("BBU_20_2.0"), 2),
        "bbl": fmt_num(latest.get("BBL_20_2.0"), 2),
        "support": support,
        "resistance": resistance,
        "support_fmt": f"${support:.2f}" if support else "N/A",
        "resistance_fmt": f"${resistance:.2f}" if resistance else "N/A",
        "week52": f"${week_high} / ${week_low}",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return df, info, tech, news_titles


def technical_score(tech):
    score = 50
    reasons = []
    rsi = tech.get("rsi_float")
    macd = tech.get("macd_float")
    signal = tech.get("signal_float")
    ma20 = tech.get("ma20_float")
    ma50 = tech.get("ma50_float")
    price = tech.get("price_float")
    support = tech.get("support")
    resistance = tech.get("resistance")

    if rsi is not None:
        if 45 <= rsi <= 60:
            score += 8; reasons.append("RSI 健康")
        elif 60 < rsi <= 70:
            score += 5; reasons.append("RSI 偏強")
        elif rsi < 30:
            score += 3; reasons.append("RSI 超賣反彈機會")
        elif rsi > 75:
            score -= 10; reasons.append("RSI 過熱")
        elif rsi < 40:
            score -= 5; reasons.append("RSI 偏弱")

    if macd is not None and signal is not None:
        if macd > signal:
            score += 14; reasons.append("MACD 偏多")
        else:
            score -= 12; reasons.append("MACD 偏空")

    if ma20 is not None and ma50 is not None:
        if ma20 > ma50:
            score += 14; reasons.append("短期均線強於中期")
        else:
            score -= 10; reasons.append("短期均線弱於中期")

    if price and ma20:
        if price > ma20:
            score += 8; reasons.append("股價站上 MA20")
        else:
            score -= 7; reasons.append("股價低於 MA20")

    if price and support and resistance and resistance > support:
        position = (price - support) / (resistance - support)
        if position > 0.88:
            score -= 5; reasons.append("接近短線壓力")
        elif position < 0.2:
            score += 4; reasons.append("接近短線支撐")

    score = max(0, min(100, int(round(score))))
    if score >= 70:
        label = "偏多"
        badge = "badge-bull"
    elif score <= 40:
        label = "偏空"
        badge = "badge-bear"
    else:
        label = "中性"
        badge = "badge-neutral"
    return score, label, badge, reasons[:5]


def ai_analysis(ticker, info, tech, score, score_label, news_titles):
    api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key or api_key.strip() == "your-api-key-here":
        return "AI 分析尚未啟用。請到 Streamlit Cloud 的 Secrets 設定 GOOGLE_API_KEY，或在本機 .streamlit/secrets.toml 加入你的 Gemini API Key。"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""你是一位專業的美股分析師。請根據以下資料，用繁體中文撰寫簡潔、清楚、可讀性高的個股分析摘要。

股票：{ticker} — {info.get('longName','')}

【技術面】
- 現價：{tech.get('price')}，今日漲跌：{tech.get('change_pct'):.2f}%
- 技術分數：{score}/100，趨勢：{score_label}
- RSI(14)：{tech.get('rsi')}
- MACD：{tech.get('macd')}，Signal：{tech.get('signal')}
- MA20：{tech.get('ma20')}，MA50：{tech.get('ma50')}
- 短線支撐：{tech.get('support_fmt')}，短線壓力：{tech.get('resistance_fmt')}
- 52週高/低：{tech.get('week52')}

【基本面】
- 本益比(P/E)：{fmt_num(info.get('trailingPE'),1)}
- EPS(TTM)：{fmt_num(info.get('trailingEps'),2)}
- 市值：{fmt_large(info.get('marketCap'))}
- 毛利率：{fmt_pct(info.get('grossMargins'))}
- 營業利益率：{fmt_pct(info.get('operatingMargins'))}
- 負債權益比：{fmt_num(info.get('debtToEquity'),1)}
- ROE：{fmt_pct(info.get('returnOnEquity'))}

【近期新聞標題】
{chr(10).join(f'- {t}' for t in news_titles[:5]) if news_titles else '- 無可用新聞'}

請分成四段：
1. 技術面趨勢
2. 基本面健康度
3. 新聞/情緒影響
4. 綜合觀察
最後提醒：僅供參考，不構成投資建議。
"""
    response = model.generate_content(prompt)
    return response.text


def render_tradingview_advanced(ticker, height=650):
    components.html(f"""
    <div style="border-radius:14px;overflow:hidden;border:1px solid #d0dce8;background:#fff">
      <div class="tradingview-widget-container" style="height:{height}px;width:100%">
        <div class="tradingview-widget-container__widget" style="height:{height}px;width:100%"></div>
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
        {{
          "autosize": true,
          "symbol": "{ticker}",
          "interval": "D",
          "timezone": "America/New_York",
          "theme": "light",
          "style": "1",
          "locale": "zh_TW",
          "allow_symbol_change": false,
          "calendar": false,
          "height": {height},
          "studies": ["STD;MACD", "STD;RSI", "STD;Bollinger_Bands"],
          "support_host": "https://www.tradingview.com"
        }}
        </script>
      </div>
    </div>
    """, height=height + 20)


def render_header():
    st.markdown('<div class="main-title">股票分析儀</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">美股技術面、基本面、新聞與 Gemini AI 綜合分析</div>', unsafe_allow_html=True)


def render_single_stock(ticker):
    with st.spinner(f"正在分析 {ticker}，請稍候…"):
        df, info, tech, news_titles = build_tech(ticker)
    if df is None:
        st.error(f"找不到股票代號 **{ticker}**，或資料不足。請確認後重試。")
        return

    company = info.get("longName", ticker)
    st.markdown(f"### {company} &nbsp;<span style='color:#64748b;font-size:1rem'>{ticker}</span>", unsafe_allow_html=True)
    sign_cls = "positive" if tech["change"] >= 0 else "negative"
    sign = "+" if tech["change"] >= 0 else ""

    m1, m2, m3, m4 = st.columns(4)
    metrics = [
        (m1, "現價", tech["price"], ""),
        (m2, "漲跌", f"{sign}{tech['change']:.2f} ({sign}{tech['change_pct']:.2f}%)", sign_cls),
        (m3, "市值", fmt_large(info.get("marketCap")), ""),
        (m4, "52週高/低", tech["week52"], ""),
    ]
    for col, label, val, cls in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {cls}">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.caption(f"資料更新時間：{tech['updated_at']}｜Yahoo Finance 資料可能延遲，請以券商即時報價為準。")

    score, score_label, score_badge, reasons = technical_score(tech)
    st.markdown('<div class="section-title">🎯 技術分數與關鍵區間</div>', unsafe_allow_html=True)
    s1, s2 = st.columns([1.1, 1])
    with s1:
        reason_html = "、".join(reasons) if reasons else "資料不足，暫無完整判斷"
        st.markdown(f"""
        <div class="panel-card">
            <div class="score-wrap">
                <div class="score-circle">{score}</div>
                <div class="score-text">
                    <span class="indicator-badge {score_badge}">趨勢：{score_label}</span><br>
                    <b>主要原因：</b>{reason_html}<br>
                    <span class="small-note">分數是依 RSI、MACD、均線、股價位置與支撐壓力估算。</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="panel-card">
            <div class="metric-label">短線支撐 / 壓力</div>
            <div class="key-grid">
                <div class="key-box"><div class="key-name">20日支撐</div><div class="key-value">{tech['support_fmt']}</div></div>
                <div class="key-box"><div class="key-name">20日壓力</div><div class="key-value">{tech['resistance_fmt']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 走勢圖</div>', unsafe_allow_html=True)
    render_tradingview_advanced(ticker, height=650)

    st.markdown('<div class="section-title">⚡ 技術指標</div>', unsafe_allow_html=True)
    tc1, tc2 = st.columns(2)
    with tc1:
        rsi_val = tech.get("rsi_float")
        rsi_cls = get_signal(rsi_val, 30, 70, reverse=True)
        rsi_lbl = "超買" if rsi_val and rsi_val > 70 else ("超賣" if rsi_val and rsi_val < 30 else "中性")
        macd_cross = "badge-bull" if tech.get("macd_float") is not None and tech.get("signal_float") is not None and tech["macd_float"] > tech["signal_float"] else "badge-bear"
        macd_lbl = "黃金交叉" if macd_cross == "badge-bull" else "死亡交叉"
        ma_cross = "badge-bull" if tech.get("ma20_float") is not None and tech.get("ma50_float") is not None and tech["ma20_float"] > tech["ma50_float"] else "badge-bear"
        ma_lbl = "MA20 > MA50" if ma_cross == "badge-bull" else "MA20 < MA50"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">技術訊號</div>
            <span class="indicator-badge {rsi_cls}">RSI {tech['rsi']} — {rsi_lbl}</span>
            <span class="indicator-badge {macd_cross}">MACD {macd_lbl}</span>
            <span class="indicator-badge {ma_cross}">{ma_lbl}</span>
        </div>
        """, unsafe_allow_html=True)
    with tc2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">關鍵數值</div>
            <div class="key-grid">
                <div class="key-box"><div class="key-name">RSI(14)</div><div class="key-value">{tech['rsi']}</div></div>
                <div class="key-box"><div class="key-name">MACD</div><div class="key-value">{tech['macd']}</div></div>
                <div class="key-box"><div class="key-name">MA20</div><div class="key-value">{tech['ma20']}</div></div>
                <div class="key-box"><div class="key-name">MA50</div><div class="key-value">{tech['ma50']}</div></div>
                <div class="key-box"><div class="key-name">布林上軌</div><div class="key-value">{tech['bbu']}</div></div>
                <div class="key-box"><div class="key-name">布林下軌</div><div class="key-value">{tech['bbl']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📋 基本面</div>', unsafe_allow_html=True)
    fund_items = [
        ("本益比 (P/E)", fmt_num(info.get("trailingPE"), 1)),
        ("EPS (TTM)", f"${fmt_num(info.get('trailingEps'), 2)}"),
        ("毛利率", fmt_pct(info.get("grossMargins"))),
        ("營業利益率", fmt_pct(info.get("operatingMargins"))),
        ("ROE", fmt_pct(info.get("returnOnEquity"))),
        ("負債權益比", fmt_num(info.get("debtToEquity"), 1)),
        ("總營收 (TTM)", fmt_large(info.get("totalRevenue"))),
        ("自由現金流", fmt_large(info.get("freeCashflow"))),
    ]
    rows_html = "".join(f'<div class="fund-row"><span class="fund-key">{k}</span><span class="fund-val">{v}</span></div>' for k, v in fund_items)
    st.markdown(f'<div class="fund-table">{rows_html}</div>', unsafe_allow_html=True)

    if news_titles:
        st.markdown('<div class="section-title">📰 近期新聞</div>', unsafe_allow_html=True)
        for title in news_titles[:6]:
            st.markdown(f'<div class="news-item"><div class="news-title">{title}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🤖 AI 綜合分析</div>', unsafe_allow_html=True)
    with st.spinner("Gemini 正在分析中…"):
        try:
            analysis = ai_analysis(ticker, info, tech, score, score_label, news_titles)
            st.markdown(f'<div class="ai-block">{analysis.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"AI 分析暫時無法使用：{e}")
    st.markdown("<br><span class='small-note'>⚠️ 本報告僅供參考，不構成投資建議。投資有風險，請自行判斷。</span>", unsafe_allow_html=True)


def render_compare():
    st.markdown('<div class="main-title">多股比較</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">最多同時比較 5 支股票</div>', unsafe_allow_html=True)
    ticker_input = st.text_input("", placeholder="輸入股票代號，用逗號分隔，例如 AAPL, TSLA, NVDA", label_visibility="collapsed")
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        compare_btn = st.button("開始比較", use_container_width=True)
    if not compare_btn:
        return
    if not ticker_input:
        st.warning("請輸入股票代號。")
        return
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()][:5]
    if len(tickers) < 2:
        st.warning("請至少輸入 2 個股票代號。")
        return

    rows = []
    with st.spinner(f"正在載入 {', '.join(tickers)} 的資料…"):
        for t in tickers:
            df, info, tech, _ = build_tech(t)
            if df is None:
                st.warning(f"{t} 無法取得足夠資料，已略過。")
                continue
            score, label, _, _ = technical_score(tech)
            rows.append({
                "股票": t,
                "公司": info.get("shortName") or info.get("longName") or t,
                "現價": tech["price"],
                "漲跌%": f"{tech['change_pct']:.2f}%",
                "RSI": tech["rsi"],
                "MACD": "多" if tech.get("macd_float") and tech.get("signal_float") and tech["macd_float"] > tech["signal_float"] else "空",
                "均線": "多" if tech.get("ma20_float") and tech.get("ma50_float") and tech["ma20_float"] > tech["ma50_float"] else "空",
                "技術分數": score,
                "趨勢": label,
                "市值": fmt_large(info.get("marketCap")),
                "P/E": fmt_num(info.get("trailingPE"), 1),
                "EPS": fmt_num(info.get("trailingEps"), 2),
            })
    if len(rows) < 2:
        st.error("有效股票不足，請重新輸入。")
        return
    st.markdown('<div class="section-title">⚖️ 比較表</div>', unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">📊 股價走勢比較</div>', unsafe_allow_html=True)
    valid = [r["股票"] for r in rows]
    symbols_json = ",".join([f'{{"proName":"NASDAQ:{t}","title":"{t}"}}' for t in valid])
    components.html(f"""
    <div style="border-radius:14px;overflow:hidden;border:1px solid #d0dce8;background:#fff">
    <div class="tradingview-widget-container" style="height:460px;width:100%">
      <div class="tradingview-widget-container__widget" style="height:460px;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
      {{
        "symbols": [{symbols_json}],
        "chartOnly": false,
        "width": "100%",
        "height": "460",
        "locale": "zh_TW",
        "colorTheme": "light",
        "autosize": true,
        "showVolume": true,
        "showMA": true,
        "hideDateRanges": false,
        "scalePosition": "right",
        "scaleMode": "Normal",
        "fontFamily": "Inter, sans-serif",
        "fontSize": "10",
        "changeMode": "price-and-percent",
        "chartType": "area",
        "lineWidth": 2
      }}
      </script>
    </div>
    </div>
    """, height=480)


def render_watchlist():
    st.markdown('<div class="main-title">自選股 Watchlist</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">一次快速檢查常看的股票</div>', unsafe_allow_html=True)
    default_list = "AAPL, MSFT, NVDA, TSLA, AMD"
    ticker_input = st.text_input("", value=default_list, placeholder="例如 AAPL, TSLA, NVDA", label_visibility="collapsed")
    col_btn, _ = st.columns([1, 5])
    with col_btn:
        run_btn = st.button("更新自選股", use_container_width=True)
    if not run_btn:
        st.info("輸入股票代號後按『更新自選股』。")
        return
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()][:12]
    rows = []
    progress = st.progress(0)
    for idx, t in enumerate(tickers):
        df, info, tech, _ = build_tech(t)
        progress.progress((idx + 1) / max(len(tickers), 1))
        if df is None:
            rows.append({"股票": t, "狀態": "資料不足"})
            continue
        score, label, _, _ = technical_score(tech)
        rows.append({
            "股票": t,
            "公司": info.get("shortName") or info.get("longName") or t,
            "現價": tech["price"],
            "漲跌%": f"{tech['change_pct']:.2f}%",
            "RSI": tech["rsi"],
            "支撐": tech["support_fmt"],
            "壓力": tech["resistance_fmt"],
            "技術分數": score,
            "趨勢": label,
        })
    progress.empty()
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("自選股最多一次顯示 12 支，避免 yfinance 請求過多導致變慢。")


# ─────────────────────────────────────────────────────────────────────────────
# Navigation
# ─────────────────────────────────────────────────────────────────────────────
page = st.sidebar.radio("", ["📈 個股分析", "⚖️ 多股比較", "⭐ 自選股"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#64748b'>手機、電腦都可使用。資料來源：Yahoo Finance / TradingView widget</small>", unsafe_allow_html=True)

if page == "📈 個股分析":
    render_header()
    col_input, col_btn, _ = st.columns([2, 1, 4])
    with col_input:
        ticker = st.text_input("", placeholder="輸入股票代號，例如 AAPL", label_visibility="collapsed").upper().strip()
    with col_btn:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        analyze = st.button("分析", use_container_width=True)
    if analyze and ticker:
        render_single_stock(ticker)
    elif analyze and not ticker:
        st.warning("請輸入股票代號。")
elif page == "⚖️ 多股比較":
    render_compare()
else:
    render_watchlist()
