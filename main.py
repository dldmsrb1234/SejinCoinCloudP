import streamlit as st
import pandas as pd
import ast
import random
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

# Google Sheets 데이터 로드 및 저장
def load_data():
    sheet = connect_gsheet()
    return pd.DataFrame(sheet.get_all_records())

def save_data(data):
    sheet = connect_gsheet()
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

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

# --- 🎒 학생용 UI --- 
if user_type == "학생용":
    data = load_data()
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    student_coins = int(data.at[student_index, "세진코인"])

    # 세진코인 상태 표시 함수
    def get_coin_display(coins):
        if coins < 0:
            return f'<h2 style="color:red;">{selected_student}님의 세진코인은 {coins}개입니다. 😢</h2>'
        elif coins == 0:
            return f'<h2 style="color:gray;">{selected_student}님의 세진코인은 {coins}개입니다. 😐</h2>'
        elif coins >= 5 and coins < 10:
            return f'<h2 style="color:green;">{selected_student}님의 세진코인은 {coins}개입니다. 😊</h2>'
        else:
            return f'<h2 style="color:yellow;">{selected_student}님의 세진코인은 {coins}개입니다. 🎉</h2>'

    # 세진코인 상태 표시
    st.markdown(get_coin_display(student_coins), unsafe_allow_html=True)

    # --- 로또 UI (따로 분리됨) ---
    st.subheader("🎰 세진코인 로또 게임 (1코인 차감)")
    chosen_numbers = st.multiselect("1부터 20까지 숫자 중 **3개**를 선택하세요:", list(range(1, 21)))

    if len(chosen_numbers) == 3 and st.button("로또 게임 시작 (1코인 차감)"):
        if student_coins < 1:
            st.error("세진코인이 부족합니다.")
        else:
            # 코인 차감 후 상태 갱신
            data.at[student_index, "세진코인"] -= 1
            student_coins -= 1
            save_data(data)

            # 로또 결과
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
                student_coins += 0.5  # 보상 후 실시간 코인 업데이트
            else:
                st.error("😢 아쉽게도 당첨되지 않았습니다.")
            
            # 로또 기록 추가
            record_list = ast.literal_eval(data.at[student_index, "기록"])
            record_list.append(f"로또 ({reward})")
            data.at[student_index, "기록"] = str(record_list)
            save_data(data)

            # 로또 결과 후 코인 상태 업데이트
            st.markdown(get_coin_display(student_coins), unsafe_allow_html=True)
