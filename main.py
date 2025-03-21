import streamlit as st
import pandas as pd
import ast
import time
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
    sheet_url = "https://docs.google.com/spreadsheets/d/1TGcuiSP_ZKN8ijk42v01tM9ZS05jQYlhPTOrv6b1zF0/edit#gid=0"
    sheet = client.open_by_url(sheet_url).sheet1
    return sheet

def load_data():
    sheet = connect_gsheet()
    data = pd.DataFrame(sheet.get_all_records())
    return data

def save_data(data):
    sheet = connect_gsheet()
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# --- UI 스타일 적용 ---
st.markdown(
    """
    <style>
    /* Google Fonts: Orbitron */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* 배경화면 */
    .stApp {
        background: url('https://global-assets.benzinga.com/kr/2025/02/16222019/1739712018-Cryptocurrency-Photo-by-SvetlanaParnikov.jpeg') repeat !important;
        background-size: 150px 150px !important;
    }

    /* 텍스트 스타일 */
    html, body, [class*="css"] {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }

    /* GIF 스타일 */
    .header-img {
        width: 100%;
        max-height: 300px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* 타이틀 스타일 */
    .title {
        text-align: center;
        color: #ffffff !important;
        font-weight: bold;
        margin-bottom: 10px;
    }

    /* 버튼 스타일 */
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

    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
         background-color: #00cc66 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
         background-color: #00e673 !important;
         transform: scale(1.05);
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
         background-color: #cc3300 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
         background-color: #ff1a1a !important;
         transform: scale(1.05);
    }

    .stCheckbox label {
         font-size: 16px;
         font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 🏆 헤더 GIF 추가 ---
st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
    '</div>',
    unsafe_allow_html=True
)

# --- 🎯 타이틀 ---
st.markdown('<h1 class="title">세진코인 관리 시스템</h1>', unsafe_allow_html=True)

# --- 데이터 불러오기 ---
data = load_data()

# --- 📌 반 선택 ---
selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
filtered_data = data[data["반"] == selected_class]

# --- 📌 학생 선택 ---
selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

# --- 🔑 관리자 비밀번호 입력 ---
password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")

# --- ✅ 관리자 인증 성공 시 ---
if password == ADMIN_PASSWORD:
    # --- 🔢 코인 부여/회수 개수 설정 ---
    coin_amount = st.number_input("부여 또는 회수할 코인 수를 입력하세요 (음수 입력 시 회수)", min_value=-100, max_value=100, value=1)

    if st.button("세진코인 변경하기"):
        if coin_amount != 0:
            data.at[student_index, "세진코인"] += coin_amount
            record_list = ast.literal_eval(data.at[student_index, "기록"])
            record_list.append(coin_amount)
            data.at[student_index, "기록"] = str(record_list)
            save_data(data)

            if coin_amount > 0:
                st.success(f"{selected_student}에게 세진코인 {coin_amount}개를 부여했습니다!")
            else:
                st.warning(f"{selected_student}에게서 세진코인 {-coin_amount}개를 회수했습니다!")

            time.sleep(1.5)  # 🔄 Google Sheets 동기화 대기
            st.experimental_rerun()
        else:
            st.error("변경할 코인 수를 입력하세요.")

    # --- 🚨 초기화 버튼 ---
    if st.button("⚠️ 세진코인 초기화"):
        data.at[student_index, "세진코인"] = 0
        data.at[student_index, "기록"] = "[]"
        save_data(data)

        st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        time.sleep(1.5)  # 🔄 Google Sheets 동기화 대기
        st.experimental_rerun()

    # --- 📊 선택한 학생의 최신 데이터 표시 ---
    updated_student_data = data.loc[[student_index]]
    st.subheader(f"{selected_student}의 업데이트된 세진코인")
    st.dataframe(updated_student_data)

# --- 📌 전체 학생 현황 보기 ---
if st.checkbox("전체 학생 세진코인 현황 보기"):
    st.subheader("전체 학생 세진코인 현황")
    st.dataframe(data)
