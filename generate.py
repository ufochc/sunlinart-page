import os
import google.generativeai as genai
from datetime import datetime
import re

# 1. 配置 AI 金鑰
# 這些金鑰會從 GitHub Secrets 自動抓取，請確保名稱為 GOOGLE_API_KEY
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    assets_dir = 'assets'
    html_snippets = ""
    
    # 2. 抓取 assets 資料夾中的圖片 (排除封面圖)
    if not os.path.exists(assets_dir):
        print("錯誤：找不到 assets 資料夾")
        return

    imgs = [f for f in os.listdir(assets_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png')) and f != 'title-art.png']
    imgs.sort(reverse=True) # 讓最新的作品排在最上面

    print(f"找到 {len(imgs)} 件作品，開始 AI 藝評生成...")

    for name in imgs:
        path = os.path.join(assets_dir, name)
        print(f"正在分析作品: {name}")
        
        try:
            # 呼叫 Gemini AI 看圖說話
            sample_file = genai.upload_file(path=path)
            prompt = "你現在是藝術家林順雄。請看著這張你的畫作，以第一人稱寫一段約 60 字的創作隨筆。語氣要淡然、內斂、充滿禪意與水的流動感。不要描述畫面內容，要描述創作時的心境。"
            response = model.generate_content([prompt, sample_file])
            text = response.text.strip()
        except Exception as e:
            print(f"AI 生成出錯 ({name}): {e}")
            text = "水墨在紙上靜靜流淌，留下的不僅是顏色，更是時間停頓的痕跡。"

        # 3. 建立作品的 HTML 區塊
        title = name.split('_')[0]
        html_snippets += f'''
      <div class="work-item">
        <img src="assets/{name}" alt="{title}">
        <div class="ai-insight">{text}</div>
      </div>'''

    # 4. 讀取模板並執行精準替換
    try:
        with open('template.html', 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 使用 re.DOTALL 確保能跨行替換兩個標記之間的內容
        # 這樣就不會動到網頁的其他部分，徹底解決亂碼問題
        final_content = re.sub(
            r'.*?', 
            f'{html_snippets}\n      ', 
            template_content, 
            flags=re.DOTALL
        )
        
        # 替換更新日期
        update_time = datetime.now().strftime("%Y-%m-%d")
        final_content = final_content.replace('', update_time)

        # 5. 寫入 index.html
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"成功！index.html 已更新，日期：{update_time}")

    except FileNotFoundError:
        print("錯誤：找不到 template.html，請確認檔案是否存在。")

if __name__ == "__main__":
    process()
