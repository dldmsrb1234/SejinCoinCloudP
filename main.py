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
        background: black !important;
    }
    
    html, body, [class*="css"] {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }

    /* 버튼 스타일 동적 변경 */
    .coin-change-btn {
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 16px !important;
        transition: transform 0.2s ease-in-out !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3) !important;
        width: 100%;
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

# --- 🎓 교사용 UI ---
if user_type == "교사용":
    data = load_data()

    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]

    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")

    if password == ADMIN_PASSWORD:
        coin_amount = st.number_input("부여 또는 회수할 코인 수를 입력하세요 (음수 입력 시 회수)", min_value=-100, max_value=100, value=1)

        # 버튼 색상 결정
        if coin_amount > 0:
            btn_color = "#32CD32"  # 초록색
        elif coin_amount < 0:
            btn_color = "#FF4C4C"  # 빨간색
        else:
            btn_color = "#D3D3D3"  # 회색

        # 버튼 HTML & CSS 적용
        st.markdown(
            f"""
            <style>
            .coin-change-btn {{
                background-color: {btn_color} !important;
            }}
            </style>
            <button class="coin-change-btn" onclick="document.getElementById('coin_submit').click()">세진코인 변경하기</button>
            <button id="coin_submit" style="display: none;"></button>
            """,
            unsafe_allow_html=True,
        )

        if st.button("세진코인 변경하기", key="coin_submit"):
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

        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            save_data(data)
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        updated_student_data = data.loc[[student_index]]
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

    if st.checkbox("전체 학생 세진코인 현황 보기"):
        st.subheader("전체 학생 세진코인 현황")
        st.dataframe(data)

# --- 🎒 학생용 UI ---
elif user_type == "학생용":
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

        st.markdown(
            f"""
            <div class="coin-display" style="background-color: {bg_color}; color: black; text-align:center; padding:15px; border-radius:10px; font-size:24px; font-weight:bold; margin-top:20px;">
                {student_name}님의 세진코인은 <b>{student_coins}개</b>입니다! {emoji}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.error("학생 정보를 찾을 수 없습니다.")


