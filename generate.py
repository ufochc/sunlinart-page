import os
import google.generativeai as genai
from datetime import datetime

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    assets_dir = 'assets'
    html_snippets = ""
    imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'title-art.png']
    imgs.sort()

    for name in imgs:
        path = os.path.join(assets_dir, name)
        try:
            sample_file = genai.upload_file(path=path)
            response = model.generate_content(["你現在是藝術家林順雄，請對這張畫寫一段50字創作感悟", sample_file])
            text = response.text.strip()
        except:
            text = "水痕在紙上靜靜流淌。"

        html_snippets += f'<div><img src="assets/{name}"><div class="ai-insight">{text}</div></div>'

    with open('template.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 精確替換內容
    import re
    content = re.sub(r'.*?', f'{html_snippets}', content, flags=re.DOTALL)
    content = content.replace('', datetime.now().strftime("%Y-%m-%d"))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    process()
