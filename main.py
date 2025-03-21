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

# --- 🌟 학생/교사 선택 ---
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용"])

# --- 🎓 교사용 UI ---
if user_type == "교사용":
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
        # --- 🎯 코인 추가/차감 ---
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
            else:
                st.error("변경할 코인 수를 입력하세요.")

        # --- 🚨 초기화 버튼 추가 ---
        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            save_data(data)
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        # --- 선택한 학생의 업데이트된 데이터 표시 ---
        updated_student_data = data.loc[[student_index]]
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

    # --- 전체 학생 코인 현황 보기 ---
    if st.checkbox("전체 학생 세진코인 현황 보기"):
        st.subheader("전체 학생 세진코인 현황")
        st.dataframe(data)
