import streamlit as st
import pandas as pd
import ast
from datetime import datetime
import random
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets API 연결 ---
def connect_gsheet():
    creds = Credentials.from_service_account_info(
        st.secrets["Drive"],
        scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    sheet_url = st.secrets["general"]["spreadsheet"]
    sheet = client.open_by_url(sheet_url).sheet1
    return sheet

# Google Sheets 데이터 로드
def load_data():
    sheet = connect_gsheet()
    return pd.DataFrame(sheet.get_all_records())

# 기록 추가 함수
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

# 데이터 저장 함수
def save_data(data):
    sheet = connect_gsheet()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())

# --- 🌟 UI 스타일 ---
st.markdown("""
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

# --- 🎓 UI 선택 ---
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용", "통계용"])

# 데이터 로드
data = load_data()

# --- 🎓 교사용 UI ---
if user_type == "교사용":
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
    if password == st.secrets["general"]["admin_password"]:
        coin_amount = st.number_input("부여 또는 회수할 코인 수:", min_value=-100, max_value=100, value=1)

        if st.button("세진코인 변경하기"):
            data.at[student_index, "세진코인"] += coin_amount
            add_record(student_index, "세진코인 변경", additional_info=f"변경된 코인: {coin_amount}")
            save_data(data)
            st.success(f"{selected_student}에게 세진코인 {coin_amount}개를 부여했습니다!")

        # 세진코인 초기화
        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            add_record(student_index, "세진코인 초기화", additional_info="세진코인 및 기록 초기화")
            save_data(data)
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        updated_student_data = data.loc[[student_index]].drop(columns=["비밀번호"])
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

# --- 🎒 학생용 UI ---
elif user_type == "학생용":
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    student_coins = int(data.at[student_index, "세진코인"])
    st.markdown(f"<h2>{selected_student}님의 세진코인은 {student_coins}개입니다.</h2>", unsafe_allow_html=True)

    password = st.text_input("비밀번호를 입력하세요:", type="password")

    if password == str(data.at[student_index, "비밀번호"]):
        # --- 🎰 로또 시스템 ---
        st.subheader("🎰 세진코인 로또 게임 (1코인 차감)")
        chosen_numbers = st.multiselect("1부터 20까지 숫자 중 **3개**를 선택하세요:", list(range(1, 21)))

        if len(chosen_numbers) == 3 and st.button("로또 게임 시작 (1코인 차감)"):
            if student_coins < 1:
                st.error("세진코인이 부족합니다.")
            else:
                data.at[student_index, "세진코인"] -= 1
                main_balls = random.sample(range(1, 21), 3)
                bonus_ball = random.choice([n for n in range(1, 21) if n not in main_balls])

                st.write("**컴퓨터 추첨 결과:**")
                st.write("메인 볼:", sorted(main_balls))
                st.write("보너스 볼:", bonus_ball)

                matches = set(chosen_numbers) & set(main_balls)
                match_count = len(matches)
                reward = None

                if match_count == 3:
                    reward = "치킨"
                elif match_count == 2 and (set(chosen_numbers) - matches).pop() == bonus_ball:
                    reward = "햄버거세트"
                elif match_count == 2:
                    reward = "매점이용권"
                elif match_count == 1:
                    reward = "0.5코인"
                    data.at[student_index, "세진코인"] += 0.5

                add_record(student_index, "로또", reward, f"당첨번호: {main_balls}")
                save_data(data)

# --- 📊 통계용 UI ---
elif user_type == "통계용":
    st.subheader("📊 로또 당첨 통계")
    all_records = []
    for _, row in data.iterrows():
        records = ast.literal_eval(row["기록"])
        for record in records:
            if record["activity"] == "로또":
                all_records.append({
                    "학생": row["학생"],
                    "반": row["반"],
                    "시간": record["timestamp"],
                    "보상": record["reward"],
                    "당첨번호": record["additional_info"]
                })

    df_records = pd.DataFrame(all_records)
    if not df_records.empty:
        st.dataframe(df_records)
        st.write(df_records["보상"].value_counts())
        high_prize_df = df_records[df_records["보상"].isin(["매점이용권", "햄버거세트", "치킨"])]
        if not high_prize_df.empty:
            st.dataframe(high_prize_df)
        else:
            st.info("아직 3등 이상 당첨된 학생이 없습니다.")
