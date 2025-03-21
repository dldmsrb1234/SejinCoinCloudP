import streamlit as st
import pandas as pd
import ast
import gspread
from google.oauth2.service_account import Credentials

ADMIN_PASSWORD = "rlagorhkdWkd"

# --- Google Sheets API 연결 ---
def connect_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["Drive"],  
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)

    sheet_url = "https://docs.google.com/spreadsheets/d/1TGcuiSP_ZKN8ijk42v01tM9ZS05jQYlhPTOrv6b1zF0/edit?gid=0#gid=0/edit"
    sheet = client.open_by_url(sheet_url).sheet1  
    return sheet

# Google Sheets 데이터 로드 및 저장
def load_data():
    sheet = connect_gsheet()
    return pd.DataFrame(sheet.get_all_records())

def save_data(data):
    sheet = connect_gsheet()
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# --- UI 스타일 ---
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://global-assets.benzinga.com/kr/2025/02/16222019/1739712018-Cryptocurrency-Photo-by-SvetlanaParnikov.jpeg') repeat !important;
        background-size: 150px 150px !important;
    }
    
    html, body, [class*="css"] {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }

    .stButton>button {
         color: #fff;
         font-weight: bold;
         border: none;
         border-radius: 8px;
         padding: 10px 20px;
         font-size: 16px;
         transition: transform 0.2s ease-in-out;
         box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    }

    /* 세진코인 텍스트 박스 스타일 */
    .coin-display {
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        font-size: 24px;
        font-weight: bold;
        margin-top: 20px;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 🎰 GIF 추가 ---
st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Lotto Scratch GIF">'
    '</div>',
    unsafe_allow_html=True
)

# --- 🌟 학생/교사 선택 ---
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용"])

# --- 🎒 학생용 UI ---
if user_type == "학생용":
    data = load_data()

    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())

    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())

    student_data = filtered_data[filtered_data["학생"] == selected_student]

    if not student_data.empty:
        student_name = student_data.iloc[0]["학생"]
        student_coins = student_data.iloc[0]["세진코인"]

        # --- 💡 세진코인 개수에 따른 스타일 설정 ---
        if student_coins < 0:
            bg_color = "#FF4C4C"  # 빨간색
            emoji = "😭"
        elif student_coins == 0:
            bg_color = "#808080"  # 회색
            emoji = "😐"
        elif student_coins >= 10:
            bg_color = "#FFD700"  # 금색
            emoji = "🎉"
        elif student_coins >= 5:
            bg_color = "#32CD32"  # 초록색
            emoji = "😆"
        else:
            bg_color = "#FFFFFF"  # 흰색
            emoji = "🙂"

        # --- HTML을 이용한 텍스트 출력 ---
        st.markdown(
            f"""
            <div class="coin-display" style="background-color: {bg_color}; color: black;">
                {student_name}님의 세진코인은 <b>{student_coins}개</b>입니다! {emoji}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("학생 정보를 찾을 수 없습니다.")
