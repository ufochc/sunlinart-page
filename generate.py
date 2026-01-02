import os
import google.generativeai as genai
from datetime import datetime
import re

# 配置 AI
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    assets_dir = 'assets'
    html_snippets = ""
    
    # 獲取圖片清單 (排除封面圖)
    imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'title-art.png']
    imgs.sort(reverse=True) # 新的作品排在上面

    print(f"找到 {len(imgs)} 張作品，準備啟動 AI 藝評模式...")

    for name in imgs:
        path = os.path.join(assets_dir, name)
        print(f"正在分析作品: {name}")
        try:
            # AI 分析圖片
            sample_file = genai.upload_file(path=path)
            response = model.generate_content(["你現在是藝術家林順雄。請看著這張你的畫作，用內斂、富有禪意且淡然的口吻，寫一段約 60 字的創作感悟。重點在於心境而非畫面描述。", sample_file])
            text = response.text.strip()
        except Exception as e:
            print(f"AI 生成失敗: {e}")
            text = "水墨在紙上緩緩暈開，留下的不僅是顏色，更是時間停頓的痕跡。"

        # 組合作品區塊
        title = name.split('_')[0]
        html_snippets += f'''
      <div class="work-item">
        <img src="assets/{name}" alt="{title}">
        <div class="ai-insight">{text}</div>
      </div>'''

    # 讀取模板
    with open('template.html', 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 執行精準替換
    # 使用 re.DOTALL 確保可以跨行匹配
    final_content = re.sub(
        r'.*?', 
        f'{html_snippets}\n      ', 
        template_content, 
        flags=re.DOTALL
    )
    
    # 替換日期
    final_content = final_content.replace('', datetime.now().strftime("%Y-%m-%d"))

    # 寫入 index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("網頁更新完成！")

if __name__ == "__main__":
    process()
