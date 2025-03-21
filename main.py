import streamlit as st
import pandas as pd
import ast
import gspread
from google.oauth2.service_account import Credentials
ADMIN_PASSWORD = [rlagorhkdWkd]
# --- Google Sheets API 연결 ---
def connect_gsheet():
    # Google API 인증
    creds = Credentials.from_service_account_info(
        st.secrets["Drive"],  # "Drive.json" → "Drive"로 수정
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)

    # 스프레드시트 URL을 사용하여 열기
    sheet_url = "https://docs.google.com/spreadsheets/d/1TGcuiSP_ZKN8ijk42v01tM9ZS05jQYlhPTOrv6b1zF0/edit?gid=0#gid=0/edit"  # 여기에 실제 스프레드시트 URL을 넣으세요
    sheet = client.open_by_url(sheet_url).sheet1  # URL로 스프레드시트 열기
    return sheet

# Google Sheets에서 데이터 로드
def load_data():
    sheet = connect_gsheet()
    data = pd.DataFrame(sheet.get_all_records())
    return data

# Google Sheets에 데이터 저장
def save_data(data):
    sheet = connect_gsheet()
    sheet.clear()  # 기존 데이터 삭제 후 업데이트
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# --- Streamlit UI ---
st.markdown(
    """
    <style>
    /* Google Fonts: Orbitron (미래지향적 느낌) */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* .stApp 배경 설정: 코인이 바둑판식으로 배열된 이미지 */
    .stApp {
        background: url('https://global-assets.benzinga.com/kr/2025/02/16222019/1739712018-Cryptocurrency-Photo-by-SvetlanaParnikov.jpeg') repeat !important;
        background-size: 150px 150px !important;
    }
    
    /* 기본 텍스트 스타일 */
    html, body, [class*="css"] {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }
    
    /* 헤더 이미지 스타일 */
    .header-img {
        width: 100%;
        max-height: 300px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* 타이틀 스타일: 빨간색, 굵은 글씨 */
    .title {
        text-align: center;
        color: #ffffff !important;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* 버튼 기본 스타일 */
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
    /* 부여 버튼 (첫 번째 컬럼) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button {
         background-color: #00cc66 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) .stButton > button:hover {
         background-color: #00e673 !important;
         transform: scale(1.05);
    }
    /* 회수 버튼 (두 번째 컬럼) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button {
         background-color: #cc3300 !important;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover {
         background-color: #ff1a1a !important;
         transform: scale(1.05);
    }
    
    /* 체크박스 스타일 */
    .stCheckbox label {
         font-size: 16px;
         font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 헤더: 움직이는 비트코인 GIF 추가 ---
st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
    '</div>',
    unsafe_allow_html=True
)

# --- 타이틀 ---
st.markdown('<h1 class="title">세진코인 관리 시스템</h1>', unsafe_allow_html=True)
# 관리자 비밀번호 설정


# 데이터 로드
data = load_data()

# 반 선택
selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
filtered_data = data[data["반"] == selected_class]

# 학생 선택
selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

# 관리자 비밀번호 입력
password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")

# 관리자 인증 후 코인 부여/회수 가능
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

else:
    st.warning("올바른 관리자 비밀번호를 입력해야 세진코인을 부여할 수 있습니다.")

# 선택한 학생의 업데이트된 데이터 표시
updated_student_data = data.loc[[student_index]]
st.subheader(f"{selected_student}의 업데이트된 세진코인")
st.dataframe(updated_student_data)

# 전체 학생 세진코인 현황 보기
if st.checkbox("전체 학생 세진코인 현황 보기"):
    st.subheader("전체 학생 세진코인 현황")
    st.dataframe(data)

