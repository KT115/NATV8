import json
import os
import random
import streamlit as st

PROJECTS_DIR = "projects_config"

st.set_page_config(page_title="Lucky Draw Webapp", page_icon="🎁", layout="centered")

# 1. 抓取網址列的專案代碼，或者讓使用者選擇
query_params = st.query_params
default_project = query_params.get("project", None)

files = [f.replace(".json", "") for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")] if os.path.exists(PROJECTS_DIR) else []

if not files:
  st.warning("目前系統中沒有任何專案 Config，請先透過 CMS 建立。")
  st.stop()

# 選擇專案（如果在網址指定了就優先採用，否則下拉選擇）
if default_project and default_project in files:
  selected_project = default_project
else:
  selected_project = st.sidebar.selectbox("切換預覽專案", files)

# 載入該專案的 Config
file_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")
with open(file_path, "r", encoding="utf-8") as f:
  config = json.load(f)

theme = config.get("theme", {})
content = config.get("content", {})

# 2. 動態套用主題顏色與背景
primary_color = theme.get("primary_color", "#FF4B4B")
background_url = theme.get("background_url", "")
logo_url = theme.get("logo_url", "")

# 注入自定義 CSS 來改變主題色與背景
bg_style = f"background-image: url('{background_url}'); background-size: cover;" if background_url else ""
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

# 3. 渲染動態 UI
if logo_url:
  st.image(logo_url, width=120)

st.title(content.get("title", "幸運大抽獎"))
st.markdown(f"### {content.get('subtitle', '')}")

st.markdown("---")

# 抽獎表單互動邏輯
user_name = st.text_input("請輸入您的姓名 / 員工編號：")

if st.button(content.get("button_text", "立即抽獎")):
  if not user_name:
    st.warning("請先輸入名字才能抽獎喔！")
  else:
    # 簡單的抽獎模擬邏輯 (50% 機率中獎)
    is_winner = random.choice([True, False])

    if is_winner:
      st.balloons()
      st.success(f"🎉 恭喜 {user_name}！{content.get('win_message', '中獎啦！')}")
    else:
      st.info(f"😢 很可惜 {user_name}，{content.get('lose_message', '下次再接再厲！')}")
