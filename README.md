# kindle2markdown

Windows11上でKindle for PCのページを自動でめくり、スクリーンショットを取得してOCRでMarkdown化するツール。

## 概要

- Kindle for PCのウィンドウを自動操作し、ページをめくりながらスクリーンショットを取得します。
- 取得した画像をOCRでテキスト抽出し、Markdownファイルに変換します。

## 想定技術

- Python（pyautogui, pillow, pytesseract など）
- Windows11

## セットアップ

1. Python 3.8以降をインストール（推奨: 3.10以降）
2. 必要パッケージのインストール

```pwsh
pip install -r requirements.txt
```

3. Tesseract OCRのインストール（OCR機能を使う場合）
   - [公式インストーラー](https://github.com/tesseract-ocr/tesseract) からWindows用Tesseractをインストール
   - 例: `C:\Program Files\Tesseract-OCR\tesseract.exe` にインストールされます
   - 環境変数PATHにTesseractのパスを追加（推奨）
   - 日本語OCRを使う場合は「Additional language data」から`jpn`を追加

4. Streamlitアプリの起動

```pwsh
streamlit run app.py
```

- ブラウザでアプリが開きます
- Kindle→OCR→Markdown化機能をUIから利用できます

---

今後、セットアップ手順やサンプルコードを追加予定です。
