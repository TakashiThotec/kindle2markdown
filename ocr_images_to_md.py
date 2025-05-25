import os
import sys
import pytesseract
import json

# Windows用Tesseractのパス（必要に応じて変更）
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 画像リストからOCR→Markdown

def ocr_images_to_markdown(image_paths, output_md_path, lang='jpn+eng', progress_callback=None):
    md_lines = []
    total = len(image_paths)
    for idx, img_path in enumerate(image_paths):
        if not os.path.isfile(img_path):
            md_lines.append(f"## Page {idx+1}\n画像ファイルが見つかりません: {img_path}\n---\n")
            if progress_callback:
                progress_callback(idx+1, total)
            continue
        from PIL import Image
        img = Image.open(img_path)
        text = pytesseract.image_to_string(img, lang=lang)
        md_lines.append(f"## Page {idx+1}\n")
        md_lines.append(text)
        md_lines.append("\n---\n")
        if progress_callback:
            progress_callback(idx+1, total)
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))

# フォルダ内画像をOCR→Markdown

def ocr_images_in_folder_to_markdown(folder_path, output_md_path, lang='jpn+eng', progress_callback=None):
    exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(exts)]
    files.sort()
    image_paths = [os.path.join(folder_path, f) for f in files]
    ocr_images_to_markdown(image_paths, output_md_path, lang, progress_callback)

# サブプロセス用: 進捗ファイルで監視

def ocr_images_in_folder_to_markdown_with_status(folder_path, output_md_path, lang='jpn+eng', status_path=None):
    exts = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(exts)]
    files.sort()
    image_paths = [os.path.join(folder_path, f) for f in files]
    md_lines = []
    total = len(image_paths)
    for idx, img_path in enumerate(image_paths):
        page = idx + 1
        status = {"page": page, "total": total, "status": "running"}
        if status_path:
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(status, f)
        if not os.path.isfile(img_path):
            md_lines.append(f"## Page {page}\n画像ファイルが見つかりません: {img_path}\n---\n")
            continue
        from PIL import Image
        img = Image.open(img_path)
        text = pytesseract.image_to_string(img, lang=lang)
        md_lines.append(f"## Page {page}\n")
        md_lines.append(text)
        md_lines.append("\n---\n")
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    if status_path:
        with open(status_path, 'w', encoding='utf-8') as f:
            json.dump({"page": total, "total": total, "status": "done"}, f)

if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == '--folder':
        folder = sys.argv[2]
        output_md = sys.argv[3]
        lang = sys.argv[4] if len(sys.argv) > 4 else 'jpn+eng'
        status_path = sys.argv[5] if len(sys.argv) > 5 else None
        ocr_images_in_folder_to_markdown_with_status(folder, output_md, lang, status_path)
        print(f'OCR 結果を Markdown に保存: {output_md}')
        sys.exit(0)
