# 📈 股票分析儀 — 升級版

美股個股深度分析報告，支援技術面、基本面、新聞摘要、Gemini AI 綜合分析、多股比較與自選股 Watchlist。

## 這版新增功能

- iPhone / Safari 手機版排版修正
- 關鍵數值改成手機穩定顯示的 grid 卡片
- Yahoo Finance 資料快取，加快重複查詢速度
- 技術分數 0–100
- 趨勢判斷：偏多 / 中性 / 偏空
- 20 日短線支撐與壓力
- 資料更新時間提示
- 自選股 Watchlist
- Gemini API Key 友善錯誤提示
- requirements 補上 plotly

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

1. 到 GitHub 建立 private repository。
2. 上傳：
   - app.py
   - requirements.txt
   - README.md
   - .gitignore
3. 不要上傳真正的 `.streamlit/secrets.toml`。
4. 到 Streamlit Cloud 建立 New app。
5. Main file path 填：

```text
app.py
```

6. 到 Advanced settings → Secrets 貼上：

```toml
GOOGLE_API_KEY = "你的 Gemini API Key"
```

7. Deploy。

## 本機測試

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 取得 Gemini API Key

到 Google AI Studio 建立 API Key，然後放到 Streamlit Cloud Secrets。

## 注意

本工具僅供參考，不構成投資建議。Yahoo Finance 資料可能延遲，請以券商即時報價為準。
