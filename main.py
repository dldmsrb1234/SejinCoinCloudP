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

# Google Sheets 데이터 로드
def load_data():
    sheet = connect_gsheet()
    return pd.DataFrame(sheet.get_all_records())

# 기록을 추가하는 함수
def add_record(student_index, activity, reward=None, additional_info=None):
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

# 데이터 저장 함수 (구현 필요)
def save_data(data):
    sheet = connect_gsheet()
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

# --- 🎓 교사용 UI --- 
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용"])

# 교사용 UI
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
                add_record(student_index, "세진코인 변경", reward=None, additional_info=f"변경된 코인: {coin_amount}")
                save_data(data)  # 코인 변경 시만 Google Sheets에 저장

                if coin_amount > 0:
                    st.success(f"{selected_student}에게 세진코인 {coin_amount}개를 부여했습니다!")
                else:
                    st.warning(f"{selected_student}에게서 세진코인 {-coin_amount}개를 회수했습니다!")

        # 세진코인 초기화 버튼
        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            add_record(student_index, "세진코인 초기화", reward=None, additional_info="세진코인 및 기록 초기화")
            save_data(data)  # 초기화 시만 Google Sheets에 저장
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")
        
        updated_student_data = data.loc[[student_index]].drop(columns=["비밀번호"])  # 비밀번호 제외
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

# --- 🎒 학생용 UI --- 
if user_type == "학생용":
    data = load_data()
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    student_coins = int(data.at[student_index, "세진코인"])
    coin_display = f"<h2>{selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    st.markdown(coin_display, unsafe_allow_html=True)

    # 학생 비밀번호 입력 받기
    password = st.text_input("비밀번호를 입력하세요:", type="password")

    # 로또 게임과 관련된 변수들
    if password == str(data.at[student_index, "비밀번호"]):
        # --- 🎰 로또 시스템 --- 
        st.subheader("🎰 세진코인 로또 게임 (1코인 차감)")

        chosen_numbers = st.multiselect("1부터 20까지 숫자 중 **3개**를 선택하세요:", list(range(1, 21)))

        # 로또 버튼이 활성화되었을 때만 게임을 진행하도록
        if 'last_play_time' not in st.session_state or time.time() - st.session_state.last_play_time > 5:
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

                    add_record(student_index, "로또", reward, f"당첨번호: {main_balls}")
                    save_data(data)  # 로또 실행 시만 Google Sheets에 저장
                    
                    # 5초 동안 버튼 비활성화
                    st.session_state.last_play_time = time.time()
        else:
            st.warning("로또 게임을 진행한 후 5초가 지나야 다시 시도할 수 있습니다.")
        
        # --- 최근 당첨 기록 탭 ---
        st.subheader(f"{selected_student}님의 최근 당첨 기록")
        record_list = ast.literal_eval(data.at[student_index, "기록"])
        
        # "로또" 활동만 필터링
        lotto_records = [record for record in record_list if record["activity"] == "로또"]
        
        if lotto_records:
            for record in lotto_records:
                st.write(f"**{record['timestamp']}**")
                st.write(f"당첨 번호: {record['additional_info']}")
                st.write(f"보상: {record['reward']}")
                st.write("---")
        else:
            st.info("아직 당첨 기록이 없습니다. 로또 게임에 도전해보세요!")
        
        # 학생 본인의 전체 활동 기록 보기
        st.subheader(f"{selected_student}님의 전체 활동 기록")
        for record in record_list:
            st.write(f"**{record['timestamp']}** - {record['activity']}")
            if record['reward']:
                st.write(f"  보상: {record['reward']}")
            if record['additional_info']:
                st.write(f"  추가 정보: {record['additional_info']}")
    else:
        st.error("비밀번호가 틀렸습니다. 다시 시도해주세요.")
