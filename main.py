import streamlit as st
import pandas as pd
import ast
import time
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets API 연결 ---
def connect_gsheet():
    # Google API 인증
    creds = Credentials.from_service_account_info(
        st.secrets["Drive"],  # "Drive.json" → "Drive"로 수정
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet = client.open("세진코인_관리").sheet1  # 스프레드시트 이름
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
st.title("세진코인 관리 시스템")

# 관리자 비밀번호 설정
ADMIN_PASSWORD = "wjddusdlcjswo"

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
