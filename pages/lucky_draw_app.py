import json
import os
import random
import streamlit as st

PROJECTS_DIR = "projects_config"
ASSETS_DIR = "assets"

st.set_page_config(page_title="Lucky Draw Webapp", page_icon="🎁", layout="centered")

query_params = st.query_params
default_project = query_params.get("project", None)

files = [
    f.replace(".json", "")
    for f in os.listdir(PROJECTS_DIR)
    if f.endswith(".json")
] if os.path.exists(PROJECTS_DIR) else []

if not files:
  st.warning("目前系統中沒有任何專案 Config，請先透過 CMS 建立。")
  st.stop()

if default_project and default_project in files:
  selected_project = default_project
else:
  selected_project = st.sidebar.selectbox("切換預覽專案", files)

file_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")
with open(file_path, "r", encoding="utf-8") as f:
  config = json.load(f)

theme = config.get("theme", {})
content = config.get("content", {})
game_config = config.get("config", {})

primary_color = theme.get("primary_color", "#FF4B4B")
logo_image = theme.get("logo_image", "")
background_image = theme.get("background_image", "")
win_probability = game_config.get("win_probability", 20)

# 處理本地圖片路徑渲染
bg_style = ""
if background_image:
  bg_path = os.path.join(ASSETS_DIR, background_image)
  # 如果是本機或 Streamlit 可以透過相對路徑載入背景
  bg_style = f"background-image: url('app/static/{background_image}'); background-size: cover;"

st.markdown(
    f"""
    <style>
    .stApp {{
        {bg_style}
    }}
    .stButton>button {{
        background-color: {primary_color};
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 渲染 Logo (讀取 assets 資料夾)
if logo_image:
  logo_path = os.path.join(ASSETS_DIR, logo_image)
  if os.path.exists(logo_path):
    st.image(logo_path, width=120)

st.title(content.get("title", "幸運大抽獎"))
st.markdown(f"### {content.get('subtitle', '')}")

st.markdown("---")

user_name = st.text_input("請輸入您的姓名 / 員工編號：")

if st.button(content.get("button_text", "立即抽獎")):
  if not user_name:
    st.warning("請先輸入名字才能抽獎喔！")
  else:
    # 根據設定的中獎機率計算 (例如 20% 代表隨機 1-100 抽到 <= 20)
    roll = random.randint(1, 100)
    is_winner = roll <= win_probability

    if is_winner:
      st.balloons()
      st.success(
          f"🎉 恭喜 {user_name}！{content.get('win_message', '中獎啦！')}"
      )
    else:
      st.info(
          f"😢 很可惜 {user_name}，{content.get('lose_message', '下次再接再厲！')}"
      )
