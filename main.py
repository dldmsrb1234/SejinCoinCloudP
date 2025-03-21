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

# --- 🌟 사이드바에서 학생/교사 선택 ---
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용"])

# --- 🌆 배경 스타일 복구 ---
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://global-assets.benzinga.com/kr/2025/02/16222019/1739712018-Cryptocurrency-Photo-by-SvetlanaParnikov.jpeg') repeat !important;
        background-size: 150px 150px !important;
    }
    .title {
        text-align: center;
        color: #ffffff !important;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .stButton>button {
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 16px;
        transition: transform 0.2s ease-in-out;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 🏫 학생용 UI ---
if user_type == "학생용":
    st.markdown("<h1 style='text-align: center; color: white;'>🚧 학생용 페이지 🚧</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: gray;'>추가 예정</h2>", unsafe_allow_html=True)

    # --- 🎥 긁어서 당첨되는 로또 GIF 추가 ---
    st.markdown(
        '<div style="text-align:center;">'
        '<img src="https://media.giphy.com/media/3o7TKMt1VVNkHV2PaE/giphy.gif" alt="Scratch GIF">'
        '</div>',
        unsafe_allow_html=True
    )

# --- 🎓 교사용 UI (기존 UI 유지) ---
else:
    # --- 🎥 헤더: 비트코인 GIF 추가 ---
    st.markdown(
        '<div style="text-align:center;">'
        '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
        '</div>',
        unsafe_allow_html=True
    )

    # --- 타이틀 ---
    st.markdown('<h1 class="title">세진코인 관리 시스템</h1>', unsafe_allow_html=True)

    # --- 데이터 로드 ---
    data = load_data()

    # --- 반 선택 ---
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]

    # --- 학생 선택 ---
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    # --- 비밀번호 입력 ---
    password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")

    if password == ADMIN_PASSWORD:
        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"{selected_student}에게 세진코인 부여"):
                data.at[student_index, "세진코인"] += 1
                record_list = ast.literal_eval(data.at[student_index, "기록"])
                record_list.append(1)
                data.at[student_index, "기록"] = str(record_list)
                save_data(data)
                st.success(f"{selected_student}에게 세진코인을 1개 부여했습니다.")

        with col2:
            if st.button(f"{selected_student}에게 세진코인 회수"):
                data.at[student_index, "세진코인"] -= 1
                record_list = ast.literal_eval(data.at[student_index, "기록"])
                record_list.append(-1)
                data.at[student_index, "기록"] = str(record_list)
                save_data(data)
                st.warning(f"{selected_student}에게서 세진코인을 1개 회수했습니다.")

        # --- 선택한 학생의 업데이트된 데이터 표시 ---
        updated_student_data = data.loc[[student_index]]
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

    # --- 전체 학생 코인 현황 보기 ---
    if st.checkbox("전체 학생 세진코인 현황 보기"):
        st.subheader("전체 학생 세진코인 현황")
        st.dataframe(data)
