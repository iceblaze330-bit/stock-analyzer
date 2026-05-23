# 📈 股票分析儀

美股個股深度分析報告，支援技術面、基本面、新聞摘要、Watchlist 自選股與 Gemini AI 綜合分析。

## 這版新增

- iPhone / Safari 手機版排版修正
- 關鍵數值改成手機穩定卡片顯示
- yfinance cache，加快重複查詢速度
- 技術分數 0–100 與偏多 / 中性 / 偏空判斷
- 20 日支撐位與壓力位
- 資料更新時間提示
- Watchlist 自選股
- Gemini API Key 未設定時不會讓整個 app 壞掉
- 基本面資料 fallback：`stock.info` 抓不到時，會再嘗試用 income statement / balance sheet / cash flow 自動補 P/E、EPS、毛利率、營業利益率、ROE、負債權益比、總營收、自由現金流

## 檔案結構

```text
stock_analyzer/
├── app.py
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

## 部署到 Streamlit Cloud

1. 建立 GitHub repository，例如 `stock-analyzer`
2. 上傳：
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
3. 不要上傳真正的 `.streamlit/secrets.toml`
4. 到 Streamlit Cloud 建立 New app
5. Main file path 填：`app.py`
6. Advanced settings → Secrets 貼上：

```toml
GOOGLE_API_KEY = "你的 Gemini API Key"
```

## 本機測試

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 取得 Gemini API Key

到 Google AI Studio 申請 Gemini API Key，然後放到 Streamlit Cloud Secrets。

⚠️ 本工具僅供參考，不構成投資建議。Yahoo Finance 資料可能延遲或缺漏，請以券商或官方財報資料為準。
