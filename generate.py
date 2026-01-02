import os
import google.generativeai as genai
from datetime import datetime

# 設定 AI
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # 使用最新且快速的模型

PROMPT = """你現在是藝術家林順雄。請看著這幅你的水性媒材作品，
用內斂、富有禪意、淡然且充滿詩意的口吻，寫下一段 50 字左右的創作隨筆。
重點在於「觀看的經驗」、「水的滲透」或「留白的呼吸」。不要描述畫面內容，要描述心境。"""

def process():
    assets_dir = 'assets'
    html_snippets = ""
    
    # 抓取圖片檔案 (排除封面)
    imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'title-art.png']
    imgs.sort(reverse=True) # 新的排前面

    for name in imgs:
        path = os.path.join(assets_dir, name)
        print(f"AI 正在觀照作品: {name}")
        
        # 呼叫 Gemini
        try:
            sample_file = genai.upload_file(path=path)
            response = model.generate_content([PROMPT, sample_file])
            text = response.text.strip()
        except Exception as e:
            text = "（水痕在紙上靜靜流淌，無需多言。）"

        # 組合 HTML
        title = name.split('_')[0]
        html_snippets += f"""
        <figure>
            <img src="assets/{name}" alt="{title}" style="width:100%; height:auto; display:block;">
        </figure>
        <div class="ai-insight">{text}</div>
        """

    # 讀取模板並替換
    with open('template.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('', html_snippets)
    content = content.replace('', datetime.now().strftime("%Y-%m-%d"))

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    process()