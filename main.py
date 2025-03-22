import streamlit as st
import pandas as pd
import ast
import random
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets API 연결 ---
def connect_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["Drive"],
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    
    # 👉 Google Sheets URL 사용
    sheet_url = "https://docs.google.com/spreadsheets/d/1wjciGq95qos6h1dBwUvMB56QhRRj-GZq3DS_btspsfE/edit?gid=1589455850#gid=1589455850/edit"  # secrets.toml 파일에서 불러오기
    sheet = client.open_by_url(sheet_url).sheet1  # 첫 번째 시트 선택
    return sheet

# 캐시된 데이터를 로드
@st.cache_data(ttl=60)  # 1분 동안 데이터 캐싱
def load_data():
    sheet = connect_gsheet()
    return pd.DataFrame(sheet.get_all_records())

def save_data(data):
    sheet = connect_gsheet()
    sheet.clear()  # 기존 시트 내용을 삭제
    sheet.update([data.columns.values.tolist()] + data.values.tolist())  # 새로운 데이터를 시트에 업데이트

# --- 🌟 UI 스타일 --- 
st.markdown(
    """
    <style>
    /* 배경화면 및 GIF 설정 */
    .stApp {
        background: url('https://global-assets.benzinga.com/kr/2025/02/16222019/1739712018-Cryptocurrency-Photo-by-SvetlanaParnikov.jpeg') repeat !important;
        background-size: 150px 150px !important;
    }

    /* 헤더 비트코인 GIF 추가 */
    .header-img {
        width: 100%;
        max-height: 300px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* 텍스트 색상 및 폰트 설정 */
    html, body, [class*="css"] {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }

    /* 버튼 스타일링 */
    .stButton>button {
         background-color: #808080 !important;
         color: #fff;
         font-weight: bold;
         border: none;
         border-radius: 8px;
         padding: 10px 20px;
         font-size: 16px;
         transition: transform 0.2s ease-in-out;
         box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# 헤더 비트코인 GIF 이미지
st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
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
    if password == st.secrets["general"]["admin_password"]:
        coin_amount = st.number_input("부여 또는 회수할 코인 수:", min_value=-100, max_value=100, value=1)

        if st.button("세진코인 변경하기"):
            if coin_amount != 0:
                data.at[student_index, "세진코인"] += coin_amount
                record_list = ast.literal_eval(data.at[student_index, "기록"])
                record_list.append(coin_amount)
                data.at[student_index, "기록"] = str(record_list)
                save_data(data)  # 변경된 데이터를 Google Sheets에 저장

                if coin_amount > 0:
                    st.success(f"{selected_student}에게 세진코인 {coin_amount}개를 부여했습니다!")
                else:
                    st.warning(f"{selected_student}에게서 세진코인 {-coin_amount}개를 회수했습니다!")

        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            save_data(data)  # 초기화된 데이터를 Google Sheets에 저장
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        updated_student_data = data.loc[[student_index]]
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

    if st.checkbox("전체 학생 세진코인 현황 보기"):
        st.subheader("전체 학생 세진코인 현황")
        st.dataframe(data)

# --- 🎒 학생용 UI --- 
else:
    data = load_data()
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    student_coins = int(data.at[student_index, "세진코인"])
    coin_display = f"<h2>{selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"

    # 세진코인 상태에 따른 텍스트 스타일 변경
    if student_coins < 0:
        coin_display = f"<h2 style='color: red;'>😢 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    elif student_coins == 0:
        coin_display = f"<h2 style='color: gray;'>😐 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    elif student_coins >= 5 and student_coins < 10:
        coin_display = f"<h2 style='color: green;'>😊 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    elif student_coins >= 10:
        coin_display = f"<h2 style='color: yellow;'>🎉 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"

    st.markdown(coin_display, unsafe_allow_html=True)

    # --- 🎰 로또 시스템 --- 
    st.subheader("🎰 세진코인 로또 게임 (1코인 차감)")
    chosen_numbers = st.multiselect("1부터 20까지 숫자 중 **3개**를 선택하세요:", list(range(1, 21)))

    if len(chosen_numbers) == 3 and st.button("로또 게임 시작 (1코인 차감)"):
        if student_coins < 1:
            st.error("세진코인이 부족합니다.")
        else:
            data.at[student_index, "세진코인"] -= 1
            pool = list(range(1, 21))
            main_balls = random.sample(pool, 3)
            bonus_ball = random.choice([n for n in pool if n not in main_balls])
            
            st.write("**컴퓨터 추첨 결과:**")
            st.write("메인 볼:", sorted(main_balls))
            st.write("보너스 볼:", bonus_ball)
            
            matches = set(chosen_numbers) & set(main_balls)
            match_count = len(matches)
            
            reward = ""
            if match_count == 3:
                st.success("🎉 1등 당첨! 상품: 치킨")
                reward = "치킨"
            elif match_count == 2 and list(set(chosen_numbers) - matches)[0] == bonus_ball:
                st.success("🎉 2등 당첨! 상품: 햄버거세트")
                reward = "햄버거세트"
            elif match_count == 2:
                st.success("🎉 3등 당첨! 상품: 매점이용권")
                reward = "매점이용권"
            elif match_count == 1:
                st.success("🎉 4등 당첨! 보상: 0.5코인")
                reward = "0.5코인"
                data.at[student_index, "세진코인"] += 0.5
            else:
                st.error("😢 아쉽게도 당첨되지 않았습니다.")
            
            record_list = ast.literal_eval(data.at[student_index, "기록"])
            record_list.append(f"로또 ({reward})")
            data.at[student_index, "기록"] = str(record_list)
            save_data(data)  # 변경된 데이터를 Google Sheets에 저장
