import os
import google.generativeai as genai
from datetime import datetime
import re

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    # 強制設定：永遠從 template.html 開始，不看舊的 index.html
    template_path = 'template.html'
    output_path = 'index.html'
    assets_dir = 'assets'
    
    # 1. 讀取模板 (母檔)
    if not os.path.exists(template_path):
        print("錯誤：找不到 template.html")
        return
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 2. 處理圖片
    html_snippets = ""
    imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'title-art.png']
    imgs.sort(reverse=True)

    for name in imgs:
        path = os.path.join(assets_dir, name)
        try:
            sample_file = genai.upload_file(path=path)
            response = model.generate_content(["你現在是藝術家林順雄，請對這張畫寫一段50字創作隨筆", sample_file])
            text = response.text.strip()
        except:
            text = "水痕在紙上靜靜流淌。"
        
        html_snippets += f'\n<div class="work-item"><img src="assets/{name}"><div class="ai-insight">{text}</div></div>'

    # 3. 執行替換 (使用最嚴謹的正則表達式)
    # 確保只替換一次，不重複疊加
    content = re.sub(r'.*?', 
                     f'{html_snippets}\n', 
                     content, flags=re.DOTALL)
    
    content = content.replace('', datetime.now().strftime("%Y-%m-%d"))

    # 4. 寫入新的 index.html (這會直接覆蓋掉舊的檔案)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"成功修復！產生的檔案大小約為: {len(content)/1024:.2f} KB")

if __name__ == "__main__":
    process()
