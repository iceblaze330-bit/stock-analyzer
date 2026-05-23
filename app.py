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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');

:root {
    --bg: #f0f4f8;
    --surface: #ffffff;
    --surface2: #e8eef4;
    --border: #d0dce8;
    --accent: #2563eb;
    --accent2: #f97316;
    --text: #1e293b;
    --muted: #64748b;
    --danger: #dc2626;
    --safe: #16a34a;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
    font-size: 15px;
}

.stApp { background-color: var(--bg); }

h1, h2, h3 { font-family: 'Manrope', sans-serif; color: var(--text); }

.main-title {
    font-family: 'Manrope', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: var(--accent);
    margin-bottom: 0.2rem;
}

.subtitle {
    color: var(--muted);
    font-size: 0.9rem;
    letter-spacing: 0.05em;
    margin-bottom: 2rem;
}

.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}

.metric-value {
    font-family: 'Manrope', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
}

.metric-value.positive { color: var(--safe); }
.metric-value.negative { color: var(--danger); }

.section-title {
    font-family: 'Manrope', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 2rem 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border);
}

.indicator-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.25rem;
}

.badge-bull { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.badge-bear { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }
.badge-neutral { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }

.news-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent2);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.news-title { font-size: 0.92rem; color: var(--text); margin-bottom: 0.3rem; font-weight: 500; line-height: 1.5; }
.news-meta { font-size: 0.75rem; color: var(--muted); }

.ai-block {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 14px;
    padding: 1.6rem;
    line-height: 1.9;
    font-size: 0.95rem;
    color: #1e293b !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.08);
}

.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.25) !important;
}

.stButton > button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37,99,235,0.35) !important;
}

.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}

div[data-testid="stMetricValue"] { font-family: 'Manrope', sans-serif; }

.fund-table {
    background: var(--surface);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.fund-row {
    display: flex;
    justify-content: space-between;
    padding: 0.8rem 1.2rem;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.fund-row:last-child { border-bottom: none; }
.fund-key { color: var(--muted); font-weight: 500; }
.fund-val { color: var(--text); font-weight: 600; }
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
        increasing_line_color="#16a34a", decreasing_line_color="#dc2626",
        name="價格",
    ), row=1, col=1)

    # MAs
    for col, color, name in [("MA20","#f97316","MA20"), ("MA50","#2563eb","MA50")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=1.2), name=name), row=1, col=1)

    # Bollinger
    for col, color in [("BBU_20_2.0","rgba(100,116,139,0.5)"), ("BBL_20_2.0","rgba(100,116,139,0.5)")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], line=dict(color=color, width=0.8, dash="dot"), showlegend=False), row=1, col=1)

    # MACD
    if "MACD_12_26_9" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD_12_26_9"], line=dict(color="#2563eb", width=1.2), name="MACD"), row=2, col=1)
    if "MACDs_12_26_9" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["MACDs_12_26_9"], line=dict(color="#f97316", width=1.2), name="Signal"), row=2, col=1)
    if "MACDh_12_26_9" in df.columns:
        colors = ["#16a34a" if v >= 0 else "#dc2626" for v in df["MACDh_12_26_9"].fillna(0)]
        fig.add_trace(go.Bar(x=df.index, y=df["MACDh_12_26_9"], marker_color=colors, name="Histogram", showlegend=False), row=2, col=1)

    # RSI
    if "RSI_14" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI_14"], line=dict(color="#7c3aed", width=1.5), name="RSI"), row=3, col=1)
        for level, color in [(70,"rgba(220,38,38,0.3)"), (30,"rgba(22,163,74,0.3)")]:
            fig.add_hline(y=level, line_dash="dash", line_color=color, row=3, col=1)

    fig.update_layout(
        height=650,
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#f0f4f8",
        font=dict(family="Inter", color="#64748b", size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(bgcolor="rgba(255,255,255,0.8)", font=dict(size=10), bordercolor="#d0dce8", borderwidth=1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    for i in range(1, 4):
        fig.update_xaxes(gridcolor="#e2e8f0", row=i, col=1)
        fig.update_yaxes(gridcolor="#e2e8f0", row=i, col=1)

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

# ── Navigation ───────────────────────────────────────────────────────────────
page = st.sidebar.radio("", ["📈 個股分析", "⚖️ 多股比較"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#64748b'>輸入股票代號開始分析</small>", unsafe_allow_html=True)

if page == "📈 個股分析":
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

        sign_cls = "positive" if change >= 0 else "negative"
        sign = "+" if change >= 0 else ""

        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)

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

        fund_items = [
            ("本益比 (P/E)", fmt_num(info.get("trailingPE"),1)),
            ("EPS (TTM)", f"${fmt_num(info.get('trailingEps'),2)}"),
            ("毛利率", fmt_pct(info.get("grossMargins"))),
            ("營業利益率", fmt_pct(info.get("operatingMargins"))),
            ("ROE", fmt_pct(info.get("returnOnEquity"))),
            ("負債權益比", fmt_num(info.get("debtToEquity"),1)),
            ("總營收 (TTM)", fmt_large(info.get("totalRevenue"))),
            ("自由現金流", fmt_large(info.get("freeCashflow"))),
        ]
        rows_html = "".join(f'<div class="fund-row"><span class="fund-key">{k}</span><span class="fund-val">{v}</span></div>' for k,v in fund_items)
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

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2: 多股票比較
# ═══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="main-title">多股比較</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">最多同時比較 5 支股票</div>', unsafe_allow_html=True)

    ticker_input = st.text_input("", placeholder="輸入股票代號，用逗號分隔，例如 AAPL, TSLA, NVDA", label_visibility="collapsed")
    col_btn2, _ = st.columns([1, 5])
    with col_btn2:
        compare_btn = st.button("開始比較", use_container_width=True)

    if compare_btn and ticker_input:
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()][:5]

        if len(tickers) < 2:
            st.warning("請至少輸入 2 個股票代號。")
            st.stop()

        with st.spinner(f"正在載入 {', '.join(tickers)} 的資料…"):

            all_info = {}
            all_hist = {}
            all_tech = {}

            for t in tickers:
                try:
                    s = yf.Ticker(t)
                    info = s.info
                    hist = s.history(period="6mo")
                    if hist.empty:
                        st.warning(f"{t} 無法取得資料，已略過。")
                        continue

                    df = hist[["Open","High","Low","Close","Volume"]].copy()
                    df["RSI_14"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
                    macd = ta.trend.MACD(df["Close"])
                    df["MACD_12_26_9"]  = macd.macd()
                    df["MACDs_12_26_9"] = macd.macd_signal()
                    df["MA20"] = df["Close"].rolling(20).mean()
                    df["MA50"] = df["Close"].rolling(50).mean()

                    latest = df.iloc[-1]
                    price = info.get("currentPrice") or info.get("regularMarketPrice") or float(latest["Close"])
                    prev  = info.get("previousClose") or float(df.iloc[-2]["Close"])

                    all_info[t] = info
                    all_hist[t] = df
                    all_tech[t] = {
                        "price": price,
                        "change_pct": (price - prev) / prev * 100,
                        "rsi": latest.get("RSI_14"),
                        "macd": latest.get("MACD_12_26_9"),
                        "signal": latest.get("MACDs_12_26_9"),
                        "ma20": latest.get("MA20"),
                        "ma50": latest.get("MA50"),
                    }
                except Exception as e:
                    st.warning(f"{t} 載入失敗：{e}")

            valid = list(all_tech.keys())
            if len(valid) < 2:
                st.error("有效股票不足，請重新輸入。")
                st.stop()

            # ── 股價走勢圖（正規化 %）────────────────────────────────────────
            st.markdown('<div class="section-title">📊 股價走勢比較（以起始日為基準 %）</div>', unsafe_allow_html=True)

            colors = ["#2563eb","#dc2626","#16a34a","#f97316","#7c3aed"]
            fig_price = go.Figure()
            for i, t in enumerate(valid):
                close = all_hist[t]["Close"]
                normalized = (close / close.iloc[0] - 1) * 100
                fig_price.add_trace(go.Scatter(
                    x=all_hist[t].index, y=normalized,
                    name=t, line=dict(color=colors[i % len(colors)], width=2)
                ))
            fig_price.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
            fig_price.update_layout(
                height=400, plot_bgcolor="#f8fafc", paper_bgcolor="#f0f4f8",
                font=dict(family="Inter", color="#64748b", size=11),
                legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#d0dce8", borderwidth=1),
                yaxis_title="報酬率 %", margin=dict(l=10, r=10, t=20, b=10),
                hovermode="x unified",
            )
            fig_price.update_xaxes(gridcolor="#e2e8f0")
            fig_price.update_yaxes(gridcolor="#e2e8f0")
            st.plotly_chart(fig_price, use_container_width=True)

            # ── 技術指標比較 ─────────────────────────────────────────────────
            st.markdown('<div class="section-title">⚡ 技術指標比較</div>', unsafe_allow_html=True)

            tech_rows = ""
            for t in valid:
                tk = all_tech[t]
                chg = tk["change_pct"]
                chg_cls = "color:#16a34a" if chg >= 0 else "color:#dc2626"
                chg_sign = "+" if chg >= 0 else ""
                rsi = tk["rsi"]
                rsi_color = "#dc2626" if rsi and float(rsi) > 70 else ("#16a34a" if rsi and float(rsi) < 30 else "#1e293b")
                macd_bull = tk["macd"] and tk["signal"] and float(tk["macd"]) > float(tk["signal"])
                ma_bull = tk["ma20"] and tk["ma50"] and float(tk["ma20"]) > float(tk["ma50"])

                tech_rows += f"""
                <tr style="border-bottom:1px solid #e2e8f0">
                    <td style="padding:0.8rem 1rem;font-weight:700;color:#1e293b">{t}</td>
                    <td style="padding:0.8rem 1rem;font-weight:600">${tk['price']:.2f}</td>
                    <td style="padding:0.8rem 1rem;font-weight:600;{chg_cls}">{chg_sign}{chg:.2f}%</td>
                    <td style="padding:0.8rem 1rem;font-weight:600;color:{rsi_color}">{fmt_num(rsi,1)}</td>
                    <td style="padding:0.8rem 1rem">{'<span style="background:#dcfce7;color:#15803d;padding:0.2rem 0.6rem;border-radius:6px;font-size:0.8rem;font-weight:600">多</span>' if macd_bull else '<span style="background:#fee2e2;color:#b91c1c;padding:0.2rem 0.6rem;border-radius:6px;font-size:0.8rem;font-weight:600">空</span>'}</td>
                    <td style="padding:0.8rem 1rem">{'<span style="background:#dcfce7;color:#15803d;padding:0.2rem 0.6rem;border-radius:6px;font-size:0.8rem;font-weight:600">多</span>' if ma_bull else '<span style="background:#fee2e2;color:#b91c1c;padding:0.2rem 0.6rem;border-radius:6px;font-size:0.8rem;font-weight:600">空</span>'}</td>
                </tr>"""

            st.markdown(f"""
            <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #d0dce8;font-size:0.88rem">
                <thead>
                    <tr style="background:#f1f5f9;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748b">
                        <th style="padding:0.8rem 1rem;text-align:left">股票</th>
                        <th style="padding:0.8rem 1rem;text-align:left">現價</th>
                        <th style="padding:0.8rem 1rem;text-align:left">漲跌</th>
                        <th style="padding:0.8rem 1rem;text-align:left">RSI</th>
                        <th style="padding:0.8rem 1rem;text-align:left">MACD</th>
                        <th style="padding:0.8rem 1rem;text-align:left">均線</th>
                    </tr>
                </thead>
                <tbody>{tech_rows}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)

            # ── 基本面比較 ───────────────────────────────────────────────────
            st.markdown('<div class="section-title">📋 基本面比較</div>', unsafe_allow_html=True)

            fund_keys = [
                ("市值", lambda i: fmt_large(i.get("marketCap"))),
                ("本益比 P/E", lambda i: fmt_num(i.get("trailingPE"),1)),
                ("EPS (TTM)", lambda i: f"${fmt_num(i.get('trailingEps'),2)}"),
                ("毛利率", lambda i: fmt_pct(i.get("grossMargins"))),
                ("營業利益率", lambda i: fmt_pct(i.get("operatingMargins"))),
                ("ROE", lambda i: fmt_pct(i.get("returnOnEquity"))),
                ("負債權益比", lambda i: fmt_num(i.get("debtToEquity"),1)),
                ("總營收 (TTM)", lambda i: fmt_large(i.get("totalRevenue"))),
            ]

            header = "".join(f'<th style="padding:0.8rem 1rem;text-align:left">{t}</th>' for t in valid)
            fund_rows_html = ""
            for label, fn in fund_keys:
                cells = "".join(f'<td style="padding:0.8rem 1rem;font-weight:600;color:#1e293b">{fn(all_info[t])}</td>' for t in valid)
                fund_rows_html += f'<tr style="border-bottom:1px solid #e2e8f0"><td style="padding:0.8rem 1rem;color:#64748b;font-weight:500">{label}</td>{cells}</tr>'

            st.markdown(f"""
            <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #d0dce8;font-size:0.88rem">
                <thead>
                    <tr style="background:#f1f5f9;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;color:#64748b">
                        <th style="padding:0.8rem 1rem;text-align:left">指標</th>{header}
                    </tr>
                </thead>
                <tbody>{fund_rows_html}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)

            # ── RSI 比較圖 ───────────────────────────────────────────────────
            st.markdown('<div class="section-title">📉 RSI 走勢比較</div>', unsafe_allow_html=True)
            fig_rsi = go.Figure()
            for i, t in enumerate(valid):
                if "RSI_14" in all_hist[t].columns:
                    fig_rsi.add_trace(go.Scatter(
                        x=all_hist[t].index, y=all_hist[t]["RSI_14"],
                        name=t, line=dict(color=colors[i % len(colors)], width=2)
                    ))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="rgba(220,38,38,0.4)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="rgba(22,163,74,0.4)")
            fig_rsi.update_layout(
                height=300, plot_bgcolor="#f8fafc", paper_bgcolor="#f0f4f8",
                font=dict(family="Inter", color="#64748b", size=11),
                legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#d0dce8", borderwidth=1),
                yaxis=dict(range=[0,100]), margin=dict(l=10, r=10, t=20, b=10),
                hovermode="x unified",
            )
            fig_rsi.update_xaxes(gridcolor="#e2e8f0")
            fig_rsi.update_yaxes(gridcolor="#e2e8f0")
            st.plotly_chart(fig_rsi, use_container_width=True)

            st.markdown("<br><span style='color:#94a3b8;font-size:0.75rem'>⚠️ 本報告僅供參考，不構成投資建議。</span>", unsafe_allow_html=True)

    elif compare_btn and not ticker_input:
        st.warning("請輸入股票代號。")
