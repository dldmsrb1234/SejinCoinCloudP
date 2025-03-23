import streamlit as st
import pandas as pd
import ast
from datetime import datetime
import random
import time
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
    sheet_url = st.secrets["general"]["spreadsheet"]  # secrets.toml 파일에서 불러오기
    sheet = client.open_by_url(sheet_url).sheet1  # 첫 번째 시트 선택
    return sheet

# --- 데이터 캐싱 적용: 데이터 로딩 최적화 ---
@st.cache_data(ttl=30)  # 캐시 30초 동안 유지
def load_data():
    sheet = connect_gsheet()
    return pd.DataFrame(sheet.get_all_records())

# 데이터 저장 (캐시된 데이터 업데이트)
def save_data(data):
    sheet = connect_gsheet()
    sheet.clear()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# 기록을 추가하는 함수
def add_record(data, student_index, activity, reward=None, additional_info=None):
    record_list = ast.literal_eval(data.at[student_index, "기록"])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = {
        "timestamp": timestamp,
        "activity": activity,
        "reward": reward,
        "additional_info": additional_info
    }
    record_list.append(new_record)
    data.at[student_index, "기록"] = str(record_list)
    save_data(data)

# --- 🌟 UI 스타일 --- 
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://global-assets.benzinga.com/kr/2025/02/16222019/1739712018-Cryptocurrency-Photo-by-SvetlanaParnikov.jpeg') repeat !important;
        background-size: 150px 150px !important;
    }
    .header-img {
        width: 100%;
        max-height: 300px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    html, body, [class*="css"] {
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }
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

st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
    '</div>',
    unsafe_allow_html=True
)

# --- 🎓 교사용 UI --- 
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용"])

# 데이터 로드
data = load_data()

# 로또 게임 결과 계산 (캐싱 적용)
@st.cache_data(ttl=300)  # 캐시 5분 동안 유지
def calculate_lotto_result(chosen_numbers, student_coins):
    main_balls = random.sample(range(1, 21), 3)
    bonus_ball = random.choice([n for n in range(1, 21) if n not in main_balls])
    matches = set(chosen_numbers) & set(main_balls)
    match_count = len(matches)
    bonus_matched = bonus_ball in chosen_numbers

    reward = "당첨 없음"
    if match_count == 3:
        reward = "🎉 1등! 치킨 🎉"
    elif match_count == 2 and bonus_matched:
        reward = "🥈 2등! 햄버거 세트 🍔"
    elif match_count == 2:
        reward = "🥉 3등! 매점 이용권 🍫"
    elif match_count == 1:
        reward = "💰 4등! 0.5코인 💰"
        student_coins += 0.5

    return main_balls, bonus_ball, reward, student_coins

if user_type == "교사용":
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
                add_record(data, student_index, "세진코인 변경", None, f"변경된 코인: {coin_amount}")
                save_data(data)
                st.success(f"{selected_student}에게 {coin_amount}개를 변경했습니다!")

        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            add_record(data, student_index, "세진코인 초기화", None, "초기화됨")
            save_data(data)
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        updated_student_data = data.loc[[student_index]].drop(columns=["비밀번호"])
        st.subheader(f"{selected_student}의 최신 정보")
        st.dataframe(updated_student_data)

elif user_type == "학생용":
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    # 세진코인 상태를 session_state로 관리
    if "student_coins" not in st.session_state:
        st.session_state.student_coins = int(data.at[student_index, "세진코인"])

    st.markdown(f"<h2>{selected_student}님의 세진코인은 {st.session_state.student_coins}개입니다.</h2>", unsafe_allow_html=True)

    password = st.text_input("비밀번호를 입력하세요:", type="password")

    if password == str(data.at[student_index, "비밀번호"]):
        st.subheader("🎰 세진코인 로또 게임 (1코인 차감)")

        chosen_numbers = st.multiselect("1부터 20까지 숫자 중 **3개** 선택:", list(range(1, 21)))

        if 'last_play_time' not in st.session_state or time.time() - st.session_state.last_play_time > 5:
            if len(chosen_numbers) == 3 and st.button("로또 게임 시작"):
                if st.session_state.student_coins < 1:
                    st.error("세진코인이 부족합니다.")
                else:
                    # 로또 게임을 시작한 후, 코인을 차감하고 결과를 계산합니다.
                    main_balls, bonus_ball, reward, updated_coins = calculate_lotto_result(chosen_numbers, st.session_state.student_coins)

                    # 세진코인 업데이트
                    st.session_state.student_coins = updated_coins

                    st.write(f"**당첨번호:** {sorted(main_balls)}, 보너스 볼: {bonus_ball}")
                    st.write(f"**결과:** {reward}")

                    if reward == "💰 4등! 0.5코인 💰":
                        data.at[student_index, "세진코인"] += 0.5

                    add_record(data, student_index, "로또", reward, f"선택: {chosen_numbers}")
                    save_data(data)

                    st.session_state.last_play_time = time.time()

        else:
            st.warning("5초 후에 다시 시도하세요.")
