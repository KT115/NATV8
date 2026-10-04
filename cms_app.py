import json
import os
import subprocess
import streamlit as st

PROJECTS_DIR = "projects_config"
ASSETS_DIR = "assets"  # 存放圖片的本地資料夾
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

st.set_page_config(
    page_title="EasyAPP CMS", page_icon="⚙️", layout="centered"
)

st.title("⚙️ EasyAPP CMS - 專案管理後台")
st.markdown(
    "在這裡管理專案設定。修改並儲存後，可直接觸發自動 Git 部署至雲端。"
)

action = st.sidebar.selectbox(
    "選擇操作", ["新建專案 (New Project)", "編輯現有專案 (Edit Project)"]
)

if action == "新建專案 (New Project)":
  st.subheader("📁 建立新專案")
  project_id = st.text_input(
      "專案代號 (Project ID，例如: abc-company)", ""
  )
  template_type = st.selectbox("選擇 Template 類型", ["lucky_draw"])

  if st.button("建立專案"):
    if not project_id:
      st.error("請輸入專案代號！")
    else:
      file_path = os.path.join(PROJECTS_DIR, f"{project_id}.json")
      if os.path.exists(file_path):
        st.warning("該專案代號已存在！")
      else:
        default_config = {
            "project_id": project_id,
            "template_type": template_type,
            "theme": {
                "primary_color": "#FF4B4B",
                "background_image": "",
                "logo_image": "",
            },
            "content": {
                "title": "🎉 迎新春幸運大抽獎",
                "subtitle": "輸入你的名字參加抽獎！",
                "button_text": "立即抽獎",
                "win_message": "恭喜你中了大獎！",
                "lose_message": "真可惜，下次繼續努力！",
            },
            "config": {"win_probability": 20},  # 預設中獎機率 20%
        }
        with open(file_path, "w", encoding="utf-8") as f:
          json.dump(default_config, f, ensure_ascii=False, indent=4)
        st.success(
            f"專案 {project_id} 建立成功！請在左側切換至編輯模式進行設定。"
        )

else:
  st.subheader("✏️ 編輯專案內容")
  files = [
      f.replace(".json", "")
      for f in os.listdir(PROJECTS_DIR)
      if f.endswith(".json")
  ]

  if not files:
    st.info("目前沒有任何專案，請先建立新專案。")
  else:
    selected_project = st.selectbox("選擇要編輯的專案", files)
    file_path = os.path.join(PROJECTS_DIR, f"{selected_project}.json")

    with open(file_path, "r", encoding="utf-8") as f:
      config = json.load(f)

    st.markdown("---")
    st.markdown("### 🎨 1. 主題與外觀設定")
    primary_color = st.color_picker(
        "主色調 (Primary Color)", config["theme"].get("primary_color", "#FF4B4B")
    )

    # 圖片上傳與檔名對應
    st.info(
        "💡 提示：您可以直接上傳圖片，系統會自動存入 assets/"
        " 資料夾，並填入對應檔名。"
    )

    uploaded_logo = st.file_uploader(
        "上傳 Logo 圖片", type=["png", "jpg", "jpeg"], key="logo_up"
    )
    if uploaded_logo:
      logo_path = os.path.join(ASSETS_DIR, uploaded_logo.name)
      with open(logo_path, "wb") as f:
        f.write(uploaded_logo.getbuffer())
      config["theme"]["logo_image"] = uploaded_logo.name
      st.success(f"Logo 已上傳，檔名：{uploaded_logo.name}")

    logo_image = st.text_input(
        "Logo 圖片檔名 (檔名即可)", config["theme"].get("logo_image", "")
    )

    uploaded_bg = st.file_uploader(
        "上傳背景圖片", type=["png", "jpg", "jpeg"], key="bg_up"
    )
    if uploaded_bg:
      bg_path = os.path.join(ASSETS_DIR, uploaded_bg.name)
      with open(bg_path, "wb") as f:
        f.write(uploaded_bg.getbuffer())
      config["theme"]["background_image"] = uploaded_bg.name
      st.success(f"背景圖已上傳，檔名：{uploaded_bg.name}")

    background_image = st.text_input(
        "背景圖片檔名 (檔名即可)",
        config["theme"].get("background_image", ""),
    )

    st.markdown("### ✍️ 2. 文字與遊戲規則設定")
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

    # 中獎機率設定 (0% - 100%)
    current_prob = config.get("config", {}).get("win_probability", 20)
    win_probability = st.slider(
        "中獎機率 (%)", min_value=0, max_value=100, value=int(current_prob)
    )

    if st.button("儲存變更並自動 Deploy (Save & Auto-Deploy)"):
      # 更新 Config 字典
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

      # 寫回 JSON 檔
      with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

      st.success("🎉 Config 儲存成功！正在執行自動 Git 部署...")

      # 自動執行 Git Push 達到 Auto-Deploy 效果
      try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Auto-update config & assets for {selected_project}",
            ],
            check=True,
        )
        result = subprocess.run(
            ["git", "push"], capture_output=True, text=True, check=True
        )
        st.success("🚀 成功推送到 GitHub！Streamlit Cloud 將自動開始重新部署。")
      except subprocess.CalledProcessError as e:
        st.warning(
            "⚠️ 檔案已儲存到本地，但 Git 自動 Push 遇到狀況（可能需要手動授權或確認"
            " git remote），錯誤訊息："
        )
        st.code(e.stderr)
