import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import os
from datetime import datetime, timedelta
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="股票分析儀",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --border: #1e1e2e;
    --accent: #00ff9d;
    --accent2: #ff6b35;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --danger: #ff4466;
    --safe: #00cc7a;
}

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

h1, h2, h3 { font-family: 'Syne', sans-serif; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, var(--accent), #00b8d9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}

.metric-label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.3rem;
}

.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
}

.metric-value.positive { color: var(--safe); }
.metric-value.negative { color: var(--danger); }

.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

.indicator-badge {
    display: inline-block;
    padding: 0.25rem 0.7rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    margin: 0.2rem;
}

.badge-bull { background: rgba(0,204,122,0.15); color: var(--safe); border: 1px solid rgba(0,204,122,0.3); }
.badge-bear { background: rgba(255,68,102,0.15); color: var(--danger); border: 1px solid rgba(255,68,102,0.3); }
.badge-neutral { background: rgba(107,107,128,0.15); color: var(--muted); border: 1px solid rgba(107,107,128,0.3); }

.news-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}

.news-title { font-size: 0.9rem; color: var(--text); margin-bottom: 0.3rem; }
.news-meta { font-size: 0.7rem; color: var(--muted); }

.ai-block {
    background: linear-gradient(135deg, rgba(0,255,157,0.05), rgba(0,184,217,0.05));
    border: 1px solid rgba(0,255,157,0.2);
    border-radius: 12px;
    padding: 1.5rem;
    line-height: 1.8;
    font-size: 0.9rem;
}

.stButton > button {
    background: var(--accent) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    background: #00cc7a !important;
    transform: translateY(-1px);
}

.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,255,157,0.15) !important;
}

div[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif; }

.fund-table {
    background: var(--surface);
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid var(--border);
}

.fund-row {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 1.2rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.85rem;
}
.fund-row:last-child { border-bottom: none; }
.fund-key { color: var(--muted); }
.fund-val { color: var(--text); font-weight: 500; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_large(n):
    if n is None or (isinstance(n, float) and pd.isna(n)):
        return "N/A"
    try:
        n = float(n)
        if abs(n) >= 1e12: return f"${n/1e12:.2f}T"
        if abs(n) >= 1e9:  return f"${n/1e9:.2f}B"
        if abs(n) >= 1e6:  return f"${n/1e6:.2f}M"
        return f"${n:,.0f}"
    except: return "N/A"

def fmt_pct(n):
    try: return f"{float(n)*100:.1f}%"
    except: return "N/A"

def fmt_num(n, decimals=2):
    try: return f"{float(n):,.{decimals}f}"
    except: return "N/A"


def get_signal(value, low, high, reverse=False):
    """Return bull/bear/neutral badge class."""
    try:
        v = float(value)
        if reverse:
            if v < low:   return "badge-bull"
            if v > high:  return "badge-bear"
        else:
            if v > high:  return "badge-bull"
            if v < low:   return "badge-bear"
        return "badge-neutral"
    except:
        return "badge-neutral"


# ── Chart ─────────────────────────────────────────────────────────────────────

def build_chart(df):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.55, 0.22, 0.23],
        subplot_titles=("", "MACD", "RSI"),
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color="#00ff9d", decreasing_line_color="#ff4466",
        name="價格",
    ), row=1, col=1)

    # MAs
    for col, color, name in [("MA20","#ffd166","MA20"), ("MA50","#00b8d9","MA50")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=1.2), name=name), row=1, col=1)

    # Bollinger
    for col, color in [("BBU_20_2.0","rgba(107,107,128,0.5)"), ("BBL_20_2.0","rgba(107,107,128,0.5)")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=0.8, dash="dot"), showlegend=False), row=1, col=1)

    # MACD
    if "MACD_12_26_9" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_12_26_9"], line=dict(color="#00ff9d", width=1.2), name="MACD"), row=2, col=1)
    if "MACDs_12_26_9" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACDs_12_26_9"], line=dict(color="#ff6b35", width=1.2), name="Signal"), row=2, col=1)
    if "MACDh_12_26_9" in df.columns:
        colors = ["#00cc7a" if v >= 0 else "#ff4466" for v in df["MACDh_12_26_9"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index, y=df["MACDh_12_26_9"], marker_color=colors, name="Histogram", showlegend=False), row=2, col=1)

    # RSI
    if "RSI_14" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI_14"], line=dict(color="#ffd166", width=1.2), name="RSI"), row=3, col=1)
        for level, color in [(70,"rgba(255,68,102,0.3)"), (30,"rgba(0,204,122,0.3)")]:
            fig.add_hline(y=level, line_dash="dash", line_color=color, row=3, col=1)

    fig.update_layout(
        height=650,
        plot_bgcolor="#12121a",
        paper_bgcolor="#0a0a0f",
        font=dict(family="DM Mono", color="#6b6b80", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    for i in range(1, 4):
        fig.update_xaxes(gridcolor="#1e1e2e", row=i, col=1)
        fig.update_yaxes(gridcolor="#1e1e2e", row=i, col=1)

    return fig


# ── AI Analysis ───────────────────────────────────────────────────────────────

def ai_analysis(ticker, info, tech, news_titles):
    api_key = os.environ.get("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    if not api_key:
        raise ValueError("找不到 GOOGLE_API_KEY，請確認 Streamlit Cloud Secrets 設定")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""你是一位專業的美股分析師。請根據以下資料，用繁體中文撰寫一份簡潔的個股分析摘要（約300字）。

股票：{ticker} — {info.get('longName','')}

【技術面】
- 現價：{tech.get('price')}  52週高/低：{tech.get('week52')}
- RSI(14)：{tech.get('rsi')}
- MACD：{tech.get('macd')}  Signal：{tech.get('signal')}
- MA20：{tech.get('ma20')}  MA50：{tech.get('ma50')}
- 布林通道上軌：{tech.get('bbu')}  下軌：{tech.get('bbl')}

【基本面】
- 本益比(P/E)：{info.get('trailingPE','N/A')}
- EPS(TTM)：{info.get('trailingEps','N/A')}
- 市值：{fmt_large(info.get('marketCap'))}
- 毛利率：{fmt_pct(info.get('grossMargins'))}
- 營業利益率：{fmt_pct(info.get('operatingMargins'))}
- 負債權益比：{fmt_num(info.get('debtToEquity'))}
- ROE：{fmt_pct(info.get('returnOnEquity'))}

【近期新聞標題】
{chr(10).join(f'- {t}' for t in news_titles[:5])}

請分析：
1. 技術面趨勢判斷（多/空/中性）
2. 基本面健康度評估
3. 近期新聞可能的影響
4. 綜合建議（注意：這不是投資建議，僅供參考）

請直接開始分析，不需要前言。"""

    response = model.generate_content(prompt)
    return response.text


# ── Main App ──────────────────────────────────────────────────────────────────

st.markdown('<div class="main-title">股票分析儀</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">美股個股深度分析報告</div>', unsafe_allow_html=True)

col_input, col_btn, _ = st.columns([2, 1, 4])
with col_input:
    ticker = st.text_input("", placeholder="輸入股票代號，例如 AAPL", label_visibility="collapsed").upper().strip()
with col_btn:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    analyze = st.button("分析", use_container_width=True)

if analyze and ticker:
    with st.spinner(f"正在分析 {ticker}，請稍候…"):

        # ── Fetch Data ────────────────────────────────────────────────────────
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            st.error(f"找不到股票代號 **{ticker}**，請確認後重試。")
            st.stop()

        hist = stock.history(period="6mo")
        if hist.empty:
            st.error("無法取得歷史價格資料。")
            st.stop()

        # ── Technical Indicators ──────────────────────────────────────────────
        df = hist[["Open","High","Low","Close","Volume"]].copy()

        # RSI
        df["RSI_14"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()

        # MACD
        macd = ta.trend.MACD(df["Close"])
        df["MACD_12_26_9"]  = macd.macd()
        df["MACDs_12_26_9"] = macd.macd_signal()
        df["MACDh_12_26_9"] = macd.macd_diff()

        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df["Close"], window=20, window_dev=2)
        df["BBU_20_2.0"] = bb.bollinger_hband()
        df["BBL_20_2.0"] = bb.bollinger_lband()

        # Moving Averages
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()

        latest = df.iloc[-1]
        price = info.get("currentPrice") or info.get("regularMarketPrice") or float(latest["Close"])
        prev_close = info.get("previousClose") or float(df.iloc[-2]["Close"])
        change = price - prev_close
        change_pct = change / prev_close * 100

        tech = {
            "price": f"${price:.2f}",
            "rsi": fmt_num(latest.get("RSI_14"), 1),
            "macd": fmt_num(latest.get("MACD_12_26_9"), 3),
            "signal": fmt_num(latest.get("MACDs_12_26_9"), 3),
            "ma20": fmt_num(latest.get("MA20"), 2),
            "ma50": fmt_num(latest.get("MA50"), 2),
            "bbu": fmt_num(latest.get("BBU_20_2.0"), 2),
            "bbl": fmt_num(latest.get("BBL_20_2.0"), 2),
            "week52": f"${info.get('fiftyTwoWeekHigh','?')} / ${info.get('fiftyTwoWeekLow','?')}",
        }

        # ── News ──────────────────────────────────────────────────────────────
        news = stock.news or []
        news_titles = [n.get("content",{}).get("title","") for n in news if n.get("content",{}).get("title")]

        # ═══════════════════════════════════════════════════════════════════════
        # Layout
        # ═══════════════════════════════════════════════════════════════════════

        # Header
        company = info.get("longName", ticker)
        st.markdown(f"### {company} &nbsp;<span style='color:#6b6b80;font-size:1rem'>{ticker}</span>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        sign_cls = "positive" if change >= 0 else "negative"
        sign = "+" if change >= 0 else ""

        for col, label, val, cls in [
            (m1, "現價", f"${price:.2f}", ""),
            (m2, "漲跌", f"{sign}{change:.2f} ({sign}{change_pct:.2f}%)", sign_cls),
            (m3, "市值", fmt_large(info.get("marketCap")), ""),
            (m4, "52週高/低", tech["week52"], ""),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {cls}">{val}</div>
                </div>""", unsafe_allow_html=True)

        # ── Chart ─────────────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📊 走勢圖</div>', unsafe_allow_html=True)
        st.plotly_chart(build_chart(df), use_container_width=True)

        # ── Technical Signals ─────────────────────────────────────────────────
        st.markdown('<div class="section-title">⚡ 技術指標</div>', unsafe_allow_html=True)

        tc1, tc2 = st.columns(2)
        with tc1:
            rsi_val = latest.get("RSI_14")
            rsi_cls = get_signal(rsi_val, 30, 70, reverse=True)
            rsi_lbl = "超買" if (rsi_val and float(rsi_val) > 70) else ("超賣" if (rsi_val and float(rsi_val) < 30) else "中性")

            macd_v = latest.get("MACD_12_26_9")
            sig_v  = latest.get("MACDs_12_26_9")
            macd_cross = "badge-bull" if (macd_v and sig_v and float(macd_v) > float(sig_v)) else "badge-bear"
            macd_lbl = "黃金交叉" if macd_cross == "badge-bull" else "死亡交叉"

            ma20 = latest.get("MA20"); ma50 = latest.get("MA50")
            ma_cross = "badge-bull" if (ma20 and ma50 and float(ma20) > float(ma50)) else "badge-bear"
            ma_lbl = "MA20 > MA50" if ma_cross == "badge-bull" else "MA20 < MA50"

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">技術訊號</div>
                <div style="margin-top:0.6rem">
                    <span class="indicator-badge {rsi_cls}">RSI {fmt_num(rsi_val,1)} — {rsi_lbl}</span>
                    <span class="indicator-badge {macd_cross}">MACD {macd_lbl}</span>
                    <span class="indicator-badge {ma_cross}">{ma_lbl}</span>
                </div>
            </div>""", unsafe_allow_html=True)

        with tc2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">關鍵數值</div>
                <div style="margin-top:0.5rem;font-size:0.85rem;line-height:2">
                    RSI(14)：<b>{tech['rsi']}</b> &nbsp;|&nbsp;
                    MACD：<b>{tech['macd']}</b><br>
                    MA20：<b>{tech['ma20']}</b> &nbsp;|&nbsp;
                    MA50：<b>{tech['ma50']}</b><br>
                    布林上軌：<b>{tech['bbu']}</b> &nbsp;|&nbsp;
                    下軌：<b>{tech['bbl']}</b>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Fundamentals ──────────────────────────────────────────────────────
        st.markdown('<div class="section-title">📋 基本面</div>', unsafe_allow_html=True)

        fc1, fc2 = st.columns(2)
        fund_left = [
            ("本益比 (P/E)", fmt_num(info.get("trailingPE"),1)),
            ("EPS (TTM)", f"${fmt_num(info.get('trailingEps'),2)}"),
            ("毛利率", fmt_pct(info.get("grossMargins"))),
            ("營業利益率", fmt_pct(info.get("operatingMargins"))),
        ]
        fund_right = [
            ("ROE", fmt_pct(info.get("returnOnEquity"))),
            ("負債權益比", fmt_num(info.get("debtToEquity"),1)),
            ("總營收 (TTM)", fmt_large(info.get("totalRevenue"))),
            ("自由現金流", fmt_large(info.get("freeCashflow"))),
        ]

        for col, rows in [(fc1, fund_left), (fc2, fund_right)]:
            with col:
                rows_html = "".join(f'<div class="fund-row"><span class="fund-key">{k}</span><span class="fund-val">{v}</span></div>' for k,v in rows)
                st.markdown(f'<div class="fund-table">{rows_html}</div>', unsafe_allow_html=True)

        # ── News ──────────────────────────────────────────────────────────────
        if news_titles:
            st.markdown('<div class="section-title">📰 近期新聞</div>', unsafe_allow_html=True)
            for title in news_titles[:6]:
                st.markdown(f'<div class="news-item"><div class="news-title">{title}</div></div>', unsafe_allow_html=True)

        # ── AI Analysis ───────────────────────────────────────────────────────
        st.markdown('<div class="section-title">🤖 AI 綜合分析</div>', unsafe_allow_html=True)
        with st.spinner("Gemini 正在分析中…"):
            try:
                analysis = ai_analysis(ticker, info, tech, news_titles)
                st.markdown(f'<div class="ai-block">{analysis.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI 分析失敗：{e}")
        st.markdown("<br><span style='color:#3a3a4a;font-size:0.7rem'>⚠️ 本報告僅供參考，不構成投資建議。投資有風險，請自行判斷。</span>", unsafe_allow_html=True)

elif analyze and not ticker:
    st.warning("請輸入股票代號。")
