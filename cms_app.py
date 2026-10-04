import json
import os
import streamlit as st

# 專案儲存資料夾
PROJECTS_DIR = "projects_config"
os.makedirs(PROJECTS_DIR, exist_ok=True)

st.set_page_config(
    page_title="EasyAPP CMS", page_icon="⚙️", layout="centered"
)

st.title("⚙️ EasyAPP CMS - 專案管理後台")
st.markdown("在這裡管理你的 Webapp 範本與客戶專案設定。")

# 1. 選擇專案動作
action = st.sidebar.selectbox(
    "選擇操作", ["新建專案 (New Project)", "編輯現有專案 (Edit Project)"]
)

if action == "新建專案 (New Project)":
  st.subheader("📁 建立新專案")
  project_id = st.text_input(
      "專案代號 (Project ID，例如: abc-company-lucky)", ""
  )
  template_type = st.selectbox(
      "選擇 Template 類型", ["lucky_draw"]
  )  #暫時只有抽獎

  if st.button("建立專案"):
    if not project_id:
      st.error("請輸入專案代號！")
    else:
      file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
      if os.path.exists(file_path):
        st.warning("該專案代號已存在！")
      else:
        # 預設 Config
        default_config = {
            "project_id": project_id,
            "template_type": template_type,
            "theme": {
                "primary_color": "#FF4B4B",
                "background_url": "",
                "logo_url": "",
            },
            "content": {
                "title": "🎉 迎新春幸運大抽獎",
                "subtitle": "輸入你的名字參加抽獎！",
                "button_text": "立即抽獎",
                "win_message": "恭喜你中了大獎！",
                "lose_message": "真可惜，下次繼續努力！",
            },
        }
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump(default_config, f, ensure_ascii=False, indent=4)
        st.success(f"專案 {project_id} 建立成功！請在左側切換至編輯模式。")

else:
  st.subheader("✏️ 編輯專案內容")
  # 列出所有現有專案
  files = [f.replace(".json", "") for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]

  if not files:
    st.info("目前沒有任何專案，請先建立新專案。")
  else:
    selected_project = st.selectbox("選擇要編輯的專案", files)
    file_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")

    # 讀取現有 Config
    with open(file_path, "r", encoding="utf-8") as f:
      config = json.load(f)

    st.markdown("---")
    st.markdown("### 🎨 1. 主題與外觀設定")
    primary_color = st.color_picker(
        "主色調 (Primary Color)", config["theme"].get("primary_color", "#FF4B4B")
    )
    logo_url = st.text_input(
        "Logo 圖片網址 (URL)", config["theme"].get("logo_url", "")
    )
    background_url = st.text_input(
        "背景圖片網址 (URL)", config["theme"].get("background_url", "")
    )

    st.markdown("### ✍️ 2. 文字內容設定")
    title = st.text_input("主標題 (Title)", config["content"].get("title", ""))
    subtitle = st.text_input(
        "副標題 (Subtitle)", config["content"].get("subtitle", "")
    )
    button_text = st.text_input(
        "按鈕文字 (Button Text)", config["content"].get("button_text", "")
    )
    win_message = st.text_input(
        "中獎訊息 (Win Message)", config["content"].get("win_message", "")
    )
    lose_message = st.text_input(
        "未中獎訊息 (Lose Message)", config["content"].get("lose_message", "")
    )

    if st.button("儲存變更 (Save Config)"):
      # 更新 Config 字典
      config["theme"]["primary_color"] = primary_color
      config["theme"]["logo_url"] = logo_url
      config["theme"]["background_url"] = background_url
      config["content"]["title"] = title
      config["content"]["subtitle"] = subtitle
      config["content"]["button_text"] = button_text
      config["content"]["win_message"] = win_message
      config["content"]["lose_message"] = lose_message

      # 寫回檔案
      with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

      st.success("🎉 專案設定儲存成功！你可以直接打開 Lucky Draw Template 預覽。")
