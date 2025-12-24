# PDF 文字優化工具

使用 Gemini AI 優化 PDF 檔案中的文字品質，提升清晰度和可讀性。

<img width="1906" height="695" alt="image" src="https://github.com/user-attachments/assets/fb24d906-ef02-4f31-ac82-7cca0f653225" />


## 功能特點

- 📄 上傳 PDF 檔案
- 🖼️ 將 PDF 轉換為高解析度圖片 (最高 600 DPI)
- 🤖 使用 Gemini AI 優化每一頁的文字
- 📑 將優化後的圖片重組為新的 PDF
- 📊 即時顯示處理進度和狀態
- 📥 下載優化後的 PDF 檔案

## 系統需求

### 必要軟體

- Python 3.8+
- poppler (pdf2image 的依賴)

### 安裝 poppler

#### macOS
```bash
brew install poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils
```

#### Windows
下載並安裝 [poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases)

## 安裝步驟

1. 複製專案
```bash
git clone <repository-url>
cd nano-nblm-pdf
```

2. 建立虛擬環境 (建議)
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

3. 安裝依賴套件
```bash
pip install -r requirements.txt
```

4. 設定環境變數
```bash
cp .env.example .env
# 編輯 .env 檔案，填入您的 Google Cloud API Key
```

或者，您也可以直接在應用程式的側邊欄輸入 API Key。

## 使用方法

1. 啟動 Streamlit 應用程式
```bash
streamlit run app.py
```

2. 在瀏覽器中開啟應用程式 (通常是 http://localhost:8501)

3. 在側邊欄輸入您的 Google Cloud API Key

4. 調整圖片解析度 (DPI)
   - 150 DPI: 快速處理，適合測試
   - 300 DPI: 標準品質 (預設)
   - 600 DPI: 最高品質，處理時間較長

5. 上傳 PDF 檔案

6. 點擊「開始處理」按鈕

7. 等待處理完成，查看即時進度

8. 下載優化後的 PDF

## API Key 取得

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立或選擇專案
3. 啟用 Vertex AI API
4. 建立服務帳號並下載 JSON 金鑰
5. 將 API Key 設定為環境變數或在應用程式中輸入

## 處理流程

1. **PDF 轉圖片**: 將 PDF 的每一頁轉換為高解析度 PNG 圖片
2. **AI 優化**: 使用 Gemini AI 優化每張圖片的文字品質
3. **圖片轉 PDF**: 將所有優化後的圖片重組為一個新的 PDF
4. **下載檔案**: 提供下載按鈕，取得優化後的 PDF

## 注意事項

- 處理時間取決於 PDF 頁數、解析度和網路速度
- 建議從較低的 DPI (150) 開始測試
- 確保有足夠的磁碟空間儲存暫時檔案
- API 使用可能會產生費用，請注意 Google Cloud 的計費政策

## 技術架構

- **Streamlit**: Web 應用程式框架
- **pdf2image**: PDF 轉圖片
- **Pillow**: 圖片處理
- **img2pdf**: 圖片轉 PDF
- **Google Gemini AI**: 文字優化

## 疑難排解

### 錯誤: "Unable to get page count"
- 確認已安裝 poppler
- 檢查 PDF 檔案是否損壞

### 錯誤: "API Key invalid"
- 確認 API Key 正確
- 檢查 Vertex AI API 是否已啟用

### 處理速度慢
- 降低 DPI 設定
- 減少 PDF 頁數
- 檢查網路連線

## 授權

MIT License

## 貢獻

歡迎提交 Issue 和 Pull Request！
