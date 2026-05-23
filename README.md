# 📈 股票分析儀

美股個股深度分析報告，支援技術面、基本面、新聞摘要與 Gemini AI 綜合分析。

## 檔案結構

```
stock_analyzer/
├── app.py                  ← 主程式
├── requirements.txt        ← 套件清單
├── .gitignore              ← 保護 API Key 不上傳
└── .streamlit/
    └── secrets.toml        ← 本機測試用（不要上傳 GitHub）
```

## 部署到 Streamlit Cloud（手機也能用）

### 第一步：安裝 Git
下載 https://git-scm.com/download/win 並安裝

### 第二步：申請 GitHub 帳號
去 https://github.com 註冊免費帳號

### 第三步：建立 GitHub Repository
1. 登入 GitHub → 右上角「+」→「New repository」
2. 名稱填 `stock-analyzer`
3. 選 Private（私人，保護你的程式碼）
4. 點「Create repository」

### 第四步：上傳程式碼（Windows 命令提示字元）
```
cd 你存放檔案的資料夾路徑
git init
git add app.py requirements.txt .gitignore
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/你的帳號/stock-analyzer.git
git push -u origin main
```
注意：.streamlit/secrets.toml 不要上傳（已被 .gitignore 保護）

### 第五步：部署到 Streamlit Cloud
1. 去 https://share.streamlit.io 用 GitHub 帳號登入
2. 點「New app」
3. 選你的 repo「stock-analyzer」
4. Main file path 填 `app.py`
5. 點「Advanced settings」→「Secrets」，貼上：
   ```
   GOOGLE_API_KEY = "你的Gemini API Key"
   ```
6. 點「Deploy!」等約 2 分鐘

### 完成！
會得到一個網址（例如 https://yourname-stock-analyzer.streamlit.app）
手機、電腦都能直接開啟使用 ✅

## 取得 Gemini API Key
1. 去 https://aistudio.google.com
2. 點「Get API Key」→「Create API key」
3. 免費，每天 50 次請求

## 使用方式
輸入美股代號（如 AAPL、TSLA、NVDA）→ 點「分析」→ 等約 15 秒

⚠️ 本工具僅供參考，不構成投資建議。
