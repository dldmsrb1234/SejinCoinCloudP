import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets 인증 함수
def authenticate_google_sheets(json_keyfile_path):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client

# 구글 스프레드시트에서 데이터 가져오는 함수
def get_student_data(sheet_name):
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_records()  # 모든 데이터를 가져옴
    return data

# 세진코인 부여 및 회수 함수
def update_student_coin(sheet_name, student_name, coin_change):
    sheet = client.open(sheet_name).sheet1
    cell = sheet.find(student_name)  # 학생 이름 찾기
    if cell:
        row = cell.row
        current_coin = int(sheet.cell(row, 2).value)  # 두 번째 열이 코인 수
        new_coin = current_coin + coin_change
        sheet.update_cell(row, 2, new_coin)  # 코인 수 업데이트
        return new_coin
    else:
        return None

# Streamlit UI 설정
st.title("세진코인 관리 시스템")

# 구글 스프레드시트에서 데이터 가져오기
sheet_name = "학생코인관리"  # 사용하고자 하는 스프레드시트 이름
client = authenticate_google_sheets('sejincoin-project-8a5959328de5.json')
students_data = get_student_data(sheet_name)

# 학생 이름 목록
student_names = [student['이름'] for student in students_data]

# 학생 선택
selected_student = st.selectbox("학생을 선택하세요:", student_names)

# 선택된 학생의 코인 현황 표시
selected_student_data = next(student for student in students_data if student['이름'] == selected_student)
st.metric(f"{selected_student}의 세진코인", selected_student_data["세진코인"])

# 코인 부여 및 회수 버튼 UI
col1, col2 = st.columns(2)

with col1:
    if st.button("세진코인 부여"):
        new_coin = update_student_coin(sheet_name, selected_student, 1)
        if new_coin is not None:
            st.success(f"{selected_student}에게 1코인 부여! 새로운 코인: {new_coin}")
        else:
            st.error("학생 데이터를 찾을 수 없습니다.")

with col2:
    if st.button("세진코인 회수"):
        new_coin = update_student_coin(sheet_name, selected_student, -1)
        if new_coin is not None:
            st.warning(f"{selected_student}에게서 1코인 회수! 새로운 코인: {new_coin}")
        else:
            st.error("학생 데이터를 찾을 수 없습니다.")

# 전체 학생 코인 현황 보기
if st.checkbox("전체 학생 세진코인 현황 보기"):
    st.subheader("전체 학생 세진코인 현황")
    for student in students_data:
        st.write(f"{student['이름']} : {student['세진코인']}")
