import json
import os
import subprocess
import streamlit as st

PROJECTS_DIR = "projects_config"
PAGES_DIR = "pages"
ASSETS_DIR = "assets"

os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

st.set_page_config(
    page_title="EasyAPP CMS", page_icon="⚙️", layout="centered"
)

st.title("⚙️ EasyAPP CMS - 專案管理後台")
st.markdown("建立新專案會**自動生成獨立的專屬網頁**並同步至雲端。")

action = st.sidebar.selectbox(
    "選擇操作", ["新建專案 (New Project)", "編輯現有專案 (Edit Project)"]
)

if action == "新建專案 (New Project)":
  st.subheader("📁 建立新專案與獨立網址")
  project_id = st.text_input(
      "專案代號 (Project ID，例如: nike-lucky-2026)", ""
  )
  template_type = st.selectbox("選擇 Template 類型", ["lucky_draw"])

  if st.button("建立專案並自動生成網頁"):
    if not project_id:
      st.error("請輸入專案代號！")
    else:
      file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
      page_file_path = os.path.join(PAGES_DIR, f"{project_id}.py")

      if os.path.exists(file_path) or os.path.exists(page_file_path):
        st.warning("該專案代號已存在，請使用其他代號！")
      else:
        # 1. 建立預設 Config JSON
        default_config = {
            "project_id": project_id,
            "template_type": template_type,
            "theme": {
                "primary_color": "#FF4B4B",
                "background_image": "",
                "logo_image": "",
            },
            "content": {
                "title": "🎉 專屬幸運大抽獎",
                "subtitle": "輸入你的名字參加抽獎！",
                "button_text": "立即抽獎",
                "win_message": "恭喜你中了大獎！",
                "lose_message": "真可惜，下次繼續努力！",
            },
            "config": {"win_probability": 20},
        }
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump(default_config, f, ensure_ascii=False, indent=4)

        # 2. 自動動態生成該專案專屬的 Python 頁面檔案
        page_code = f'''import streamlit as st
import json
import os
import random

PROJECT_ID = "{project_id}"
FILE_PATH = os.path.join("projects_config", f"{{PROJECT_ID}}.json")
ASSETS_DIR = "assets"

st.set_page_config(page_title=f"{{PROJECT_ID}} 抽獎活動", page_icon="🎁", layout="centered")

if not os.path.exists(FILE_PATH):
    st.error("找不到此專案的設定檔。")
    st.stop()

with open(FILE_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

theme = config.get("theme", {{}})
content = config.get("content", {{}})
game_config = config.get("config", {{}})

primary_color = theme.get("primary_color", "#FF4B4B")
logo_image = theme.get("logo_image", "")
background_image = theme.get("background_image", "")
win_probability = game_config.get("win_probability", 20)

bg_style = ""
if background_image:
    bg_style = f"background-image: url('app/static/{{background_image}}'); background-size: cover;"

st.markdown(f"""
    <style>
    .stApp {{
        {{bg_style}}
    }}
    .stButton>button {{
        background-color: {{primary_color}};
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }}
    </style>
    """, unsafe_allow_html=True)

if logo_image:
    logo_path = os.path.join(ASSETS_DIR, logo_image)
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)

st.title(content.get("title", "幸運大抽獎"))
st.markdown(f"### {{content.get('subtitle', '')}}")
st.markdown("---")

user_name = st.text_input("請輸入您的姓名 / 員工編號：")

if st.button(content.get("button_text", "立即抽獎")):
    if not user_name:
        st.warning("請先輸入名字才能抽獎喔！")
    else:
        roll = random.randint(1, 100)
        is_winner = roll <= win_probability
        if is_winner:
            st.balloons()
            st.success(f"🎉 恭喜 {{user_name}}！{{content.get('win_message', '中獎啦！')}}")
        else:
            st.info(f"😢 很可惜 {{user_name}}，{{content.get('lose_message', '下次再接再厲！')}}")
'''
        with open(page_file_path, "w", encoding="utf-8") as pf:
          pf.write(page_code)

        st.success(
            f"🚀 專案 {project_id} 建立成功！已自動在 pages/ 生成專屬網頁檔案。"
        )

        # 3. 自動 Git Push 觸發 Streamlit Cloud 自動 Deploy
        try:
          subprocess.run(["git", "add", "."], check=True)
          subprocess.run(
              [
                  "git",
                  "commit",
                  "-m",
                  f"Auto-generate dedicated webapp page for {project_id}",
              ],
              check=True,
          )
          subprocess.run(["git", "push"], check=True)
          st.success(
              "🌐 已自動推送到 GitHub！約 1 分鐘後即可透過新網址訪問該專案。"
          )
        except subprocess.CalledProcessError as e:
          st.warning(
              "⚠️ 檔案已在本地生成，但 Git 自動 Push 失敗，請手動 Push 程式碼至 GitHub。"
          )

else:
  st.subheader("✏️ 編輯現有專案內容")
  files = [
      f.replace(".json", "")
      for f in os.listdir(PROJECTS_DIR)
      if f.endswith(".json")
  ]

  if not files:
    st.info("目前沒有任何專案。")
  else:
    selected_project = st.selectbox("選擇要編輯的專案", files)
    file_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")

    with open(file_path, "r", encoding="utf-8") as f:
      config = json.load(f)

    st.markdown("---")
    st.markdown("### 🎨 主題與外觀設定")
    primary_color = st.color_picker(
        "主色調 (Primary Color)", config["theme"].get("primary_color", "#FF4B4B")
    )

    uploaded_logo = st.file_uploader(
        "上傳 Logo 圖片", type=["png", "jpg", "jpeg"], key="logo_up"
    )
    if uploaded_logo:
      logo_path = os.path.join(ASSETS_DIR, uploaded_logo.name)
      with open(logo_path, "wb") as f:
        f.write(uploaded_logo.getbuffer())
      config["theme"]["logo_image"] = uploaded_logo.name

    logo_image = st.text_input(
        "Logo 圖片檔名", config["theme"].get("logo_image", "")
    )

    uploaded_bg = st.file_uploader(
        "上傳背景圖片", type=["png", "jpg", "jpeg"], key="bg_up"
    )
    if uploaded_bg:
      bg_path = os.path.join(ASSETS_DIR, uploaded_bg.name)
      with open(bg_path, "wb") as f:
        f.write(uploaded_bg.getbuffer())
      config["theme"]["background_image"] = uploaded_bg.name

    background_image = st.text_input(
        "背景圖片檔名", config["theme"].get("background_image", "")
    )

    st.markdown("### ✍️️ 文字與中獎機率設定")
    title = st.text_input("主標題 (Title)", config["content"].get("title", ""))
    subtitle = st.text_input(
        "副標題 (Subtitle)", config["content"].get("subtitle", "")
    )
    button_text = st.text_input(
        "按鈕文字 (Button Text)", config["content"].get("button_text", "")
    )
    win_message = st.text_input(
        "中獎訊息 (Win Message)", config["content"].get("win_message", ""))
    lose_message = st.text_input(
        "未中獎訊息 (Lose Message)", config["content"].get("lose_message", "")
    )

    current_prob = config.get("config", {}).get("win_probability", 20)
    win_probability = st.slider(
        "中獎機率 (%)", min_value=0, max_value=100, value=int(current_prob)
    )

    if st.button("儲存變更並更新網頁 (Save & Update)"):
      config["theme"]["primary_color"] = primary_color
      config["theme"]["logo_image"] = logo_image
      config["theme"]["background_image"] = background_image
      config["content"]["title"] = title
      config["content"]["subtitle"] = subtitle
      config["content"]["button_text"] = button_text
      config["content"]["win_message"] = win_message
      config["content"]["lose_message"] = lose_message
      if "config" not in config:
        config["config"] = {}
      config["config"]["win_probability"] = win_probability

      with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

      st.success("🎉 設定更新成功！正在同步至 GitHub...")

      try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Update config for {selected_project}"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)
        st.success(
            "🚀 成功推送！該專案網頁將在 Streamlit Cloud 自動完成更新。"
        )
      except subprocess.CalledProcessError as e:
        st.warning("⚠️ 本地儲存成功，但 Git Push 遇到問題，請手動確認。")
