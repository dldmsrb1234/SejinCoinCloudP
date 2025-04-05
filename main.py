import streamlit as st
import pandas as pd
import ast
from datetime import datetime, timedelta, timezone
import random
import time
import gspread
from google.oauth2.service_account import Credentials
import os
import pickle

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



# 캐시된 데이터를 로드하는 함수
def load_data_from_cache():
    cache_file = "data_cache.pkl"
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            return pickle.load(f)
    else:
        return None

# 캐시된 데이터를 저장하는 함수
def save_data_to_cache(data):
    with open("data_cache.pkl", "wb") as f:
        pickle.dump(data, f)

# Google Sheets 데이터 로드
def load_data():
    cached_data = load_data_from_cache()
    if cached_data is not None:
        return cached_data
    else:
        sheet = connect_gsheet()
        data = pd.DataFrame(sheet.get_all_records())
        save_data_to_cache(data)
        return data

def save_data(data):
    sheet = connect_gsheet()
    sheet.update([data.columns.values.tolist()] + data.values.tolist())
    save_data_to_cache(data)

# 기록을 추가하는 함수 (KST 적용)
def add_record(student_index, activity, reward=None, additional_info=None):
    kst = timezone(timedelta(hours=9))
    timestamp = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")
    record_list = ast.literal_eval(data.at[student_index, "기록"])
    new_record = {
        "timestamp": timestamp,
        "activity": activity,
        "reward": reward,
        "additional_info": additional_info
    }
    record_list.append(new_record)
    data.at[student_index, "기록"] = str(record_list)

def get_student_password(class_name, student_name):
    df = get_worksheet_data("학생정보")  # 비밀번호가 저장된 시트
    row = df[(df["반"] == class_name) & (df["이름"] == student_name)]
    if not row.empty:
        return str(row.iloc[0]["비밀번호"])
    return ""

def save_student_lotto_status(class_name, student_name, date_str, numbers):
    worksheet = get_worksheet("로또진행상태")
    worksheet.append_row([class_name, student_name, date_str, ','.join(map(str, numbers))])

def load_student_lotto_status(class_name, student_name, date_str):
    df = get_worksheet_data("로또진행상태")
    row = df[(df["반"] == class_name) & (df["이름"] == student_name) & (df["날짜"] == date_str)]
    if not row.empty:
        return list(map(int, row.iloc[0]["번호"].split(',')))
    return None

def get_class_list():
    sheet = get_worksheet("학생정보")
    class_col = sheet.col_values(1)[1:]  # 첫 번째 열 (1열): 반 이름
    return sorted(list(set(class_col)))


def get_student_list(class_name):
    sheet = get_worksheet("학생정보")
    records = sheet.get_all_records()
    students = [row["이름"] for row in records if row["반"] == class_name]
    return students

# --- BGM 재생: 학생 비밀번호 입력 시 재생 (로컬 파일 "bgm.mp3") ---
def render_bgm():
    return """
    <audio id="bgm" autoplay loop>
        <source src="bgm.mp3" type="audio/mp3">
    </audio>
    """

# --- 🌟 UI 스타일 ---
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://i.ibb.co/vCZs9W58/bgi2.jpg') no-repeat center center fixed !important;
        background-size: cover !important;
    }
    .content-container {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 20px;
        border-radius: 10px;
        max-width: 800px;
        margin: auto;
        font-size: 1.2em;
    }
    .header-img {
        width: 100%;
        max-height: 300px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    p, h1, h2, h3, h4, h5, h6 {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 4px;
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
    /* 버튼 안 글씨 배경 제거 스타일 추가 */
    .stButton button span {
        background-color: transparent !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 헤더 이미지
st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
    '</div>',
    unsafe_allow_html=True
)
st.markdown('<h1 style="text-align:center; font-size:3em; color:yellow; background-color:rgba(0,0,0,0.7); padding:10px; border-radius:10px;">$$세진코인$$</h1>', unsafe_allow_html=True)

st.markdown('<div class="content-container">', unsafe_allow_html=True)

# --- 🎓 UI 선택 ---
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용", "통계용", "로그 확인"])

data = load_data()

if "drawing" not in st.session_state:
    st.session_state["drawing"] = False

# --- 로그 확인 UI ---
if user_type == "로그 확인":
    st.sidebar.subheader("📜 로그 확인")
    selected_class_log = st.sidebar.selectbox("반 선택:", data["반"].unique(), key="log_class")
    filtered_data_log = data[data["반"] == selected_class_log]
    selected_student_log = st.sidebar.selectbox("학생 선택:", filtered_data_log["학생"].tolist(), key="log_student")
    student_index_log = data[(data["반"] == selected_class_log) & (data["학생"] == selected_student_log)].index[0]
    log_password = st.text_input("비밀번호 입력:", type="password")
    if log_password:
        admin_password = st.secrets["general"]["admin_password"]
        student_password = str(data.at[student_index_log, "비밀번호"])
        if log_password == admin_password or log_password == student_password:
            st.subheader(f"{selected_student_log}님의 활동 로그")
            student_logs = ast.literal_eval(data.at[student_index_log, "기록"])
            for log in student_logs:
                timestamp = log["timestamp"]
                activity = log["activity"]
                reward = log.get("reward", "")
                additional_info = log.get("additional_info", "")
                log_text = f"🕒 {timestamp} - {activity}"
                if reward:
                    log_text += f" (보상: {reward})"
                if additional_info:
                    log_text += f" [{additional_info}]"
                st.write(log_text)
        else:
            st.error("올바른 비밀번호를 입력하세요.")

# --- 교사용 UI ---
if user_type == "교사용":
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]
    password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
    if password == st.secrets["general"]["admin_password"]:
        # 개별 학생 코인 부여/차감
        coin_amount = st.number_input("부여 또는 회수할 코인 수:", min_value=-100, max_value=100, value=1)
        if st.button("세진코인 변경하기"):
            if coin_amount != 0:
                data.at[student_index, "세진코인"] += coin_amount
                add_record(student_index, "세진코인 변경", reward=None, additional_info=f"변경된 코인: {coin_amount}")
                save_data(data)
                if coin_amount > 0:
                    st.success(f"{selected_student}에게 세진코인 {coin_amount}개를 부여했습니다!")
                else:
                    st.warning(f"{selected_student}에게서 세진코인 {-coin_amount}개를 회수했습니다!")
        st.subheader(f"🔑 {selected_student}의 비밀번호 변경")
        new_password = st.text_input("새로운 비밀번호 입력:", type="password")
        if st.button("비밀번호 변경"):
            data.at[student_index, "비밀번호"] = new_password
            save_data(data)
            st.success(f"{selected_student}의 비밀번호가 성공적으로 변경되었습니다!")
        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            add_record(student_index, "세진코인 초기화", reward=None, additional_info="세진코인 및 기록 초기화")
            save_data(data)
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")
        
        # ★ 학급 전체 일괄 작업 기능 ★
        st.markdown("---")
        st.subheader("학급 전체 일괄 작업")
        batch_coin_amount = st.number_input("전체 학급에 부여/차감할 코인 수:", min_value=-100, max_value=100, value=1, key="batch_coin")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("전체 일괄 부여/차감", key="batch_change"):
                if batch_coin_amount != 0:
                    class_indices = data[data["반"] == selected_class].index
                    for idx in class_indices:
                        data.at[idx, "세진코인"] += batch_coin_amount
                        add_record(idx, "학급 전체 세진코인 변경", reward=None, additional_info=f"일괄 변경된 코인: {batch_coin_amount}")
                    save_data(data)
                    if batch_coin_amount > 0:
                        st.success(f"{selected_class} 전체 학생에게 세진코인 {batch_coin_amount}개 부여 완료!")
                    else:
                        st.warning(f"{selected_class} 전체 학생에게서 세진코인 {-batch_coin_amount}개 회수 완료!")
        with col2:
            if st.button("전체 세진코인 초기화", key="batch_reset"):
                class_indices = data[data["반"] == selected_class].index
                for idx in class_indices:
                    data.at[idx, "세진코인"] = 0
                    data.at[idx, "기록"] = "[]"
                    add_record(idx, "학급 전체 세진코인 초기화", reward=None, additional_info="일괄 초기화")
                save_data(data)
                st.error(f"{selected_class} 전체 학생의 세진코인 초기화 완료!")
        
        updated_student_data = data.loc[[student_index]].drop(columns=["비밀번호"])
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)
    student_coins = float(data.at[student_index, "세진코인"])
    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 학생 정보")
    st.sidebar.write(f"**이름:** {selected_student}")
    st.sidebar.write(f"**보유 코인:** {student_coins:.1f}개")
    st.sidebar.markdown("---")
    st.markdown(
        f"<h2 style='background-color: rgba(0, 0, 0, 0.7); padding: 10px; border-radius: 8px;'>"
        f"{selected_student}님의 세진코인은 {student_coins:.1f}개입니다."
        f"</h2>",
        unsafe_allow_html=True
    )

# --- 학생용 UI ---
elif user_type == "학생용":
    st.header("🎓 학생용 페이지")

    # 1. 반, 학생 선택
    student_class = st.selectbox("반을 선택하세요", options=class_list, key="student_class")
    student_name = st.selectbox("이름을 선택하세요", options=get_student_list(student_class), key="student_name")
    
    # 2. 비밀번호 입력
    password_input = st.text_input("비밀번호를 입력하세요", type="password")

    # 학생 정보 가져오기
    student_info = get_student_info(student_class, student_name)

    if student_info is None:
        st.warning("학생 정보를 불러올 수 없습니다.")
        st.stop()

    # 비밀번호 확인
    correct_password = student_info.get("비밀번호", "")
    if password_input != correct_password:
        st.info("비밀번호가 일치해야 로또 UI를 볼 수 있습니다.")
        st.stop()

    # 로또 UI 진입
    st.success("비밀번호 확인 완료! 로또를 시작하세요 🎉")

    # 날짜 및 키
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    student_key = f"{today}_{student_class}_{student_name}"

    # 상태 초기화
    if "selected_numbers" not in st.session_state:
        st.session_state.selected_numbers = []
    if "lotto_animating" not in st.session_state:
        st.session_state.lotto_animating = False

    # 번호 선택
    st.subheader("1~20 중에서 숫자 3개를 선택하세요")

    if st.session_state.lotto_animating:
        st.info("추첨 중입니다. 번호를 선택할 수 없습니다.")
    else:
        cols = st.columns(5)
        for i in range(1, 21):
            col = cols[(i - 1) % 5]
            if col.button(str(i), key=f"lotto_num_{i}"):
                if i in st.session_state.selected_numbers:
                    st.session_state.selected_numbers.remove(i)
                elif len(st.session_state.selected_numbers) < 3:
                    st.session_state.selected_numbers.append(i)

    st.write("선택한 번호:", st.session_state.selected_numbers)

    # 추첨 버튼
    if st.button("🎰 로또 추첨 시작"):
        if len(st.session_state.selected_numbers) != 3:
            st.warning("숫자 3개를 정확히 선택해주세요.")
        elif st.session_state.lotto_animating:
            st.info("이미 추첨이 진행 중입니다.")
        else:
            current_coin = student_info.get("코인", 0)
            if current_coin < 1:
                st.error("세진코인이 부족합니다. 로또를 진행할 수 없습니다.")
            else:
                # 코인 차감
                new_coin = current_coin - 1
                student_cell = students_sheet.find(student_name)
                students_sheet.update_cell(student_cell.row, student_cell.col + 2, new_coin)  # '코인' 열은 +2번째

                st.success(f"세진코인 1개 차감! 남은 코인: {new_coin}개")

                st.session_state.lotto_animating = True
                with st.spinner("로또 추첨 중..."):
                    time.sleep(3)

                # 당첨 번호 및 보너스
                winning_numbers = random.sample(range(1, 21), 3)
                bonus = random.choice([n for n in range(1, 21) if n not in winning_numbers])
                st.success(f"당첨 번호: {winning_numbers}, 보너스: {bonus}")

                # 결과 판정
                selected = st.session_state.selected_numbers
                match = len(set(selected) & set(winning_numbers))
                bonus_match = bonus in selected

                if match == 3:
                    result = "🎉 1등 (치킨)"
                elif match == 2 and bonus_match:
                    result = "🥳 2등 (햄버거세트)"
                elif match == 2:
                    result = "😊 3등 (매점이용권)"
                elif match == 1:
                    result = "😅 4등 (0.5코인)"
                else:
                    result = "😭 꽝"

                st.subheader(f"결과: {result}")

                # 기록 저장
                lotto_cache = load_lotto_cache()
                cache_key = f"{student_key}_{datetime.datetime.now().strftime('%H%M%S')}"
                lotto_cache[cache_key] = {
                    "class": student_class,
                    "name": student_name,
                    "selected": selected,
                    "winning": winning_numbers,
                    "bonus": bonus,
                    "result": result,
                    "date": today
                }
                save_lotto_cache(lotto_cache)

                # 구글 시트 기록
                add_lotto_log(student_class, student_name, selected, winning_numbers, bonus, result, today)

                # 상태 초기화
                st.session_state.selected_numbers = []
                st.session_state.lotto_animating = False

        
       

# --- 통계용 UI ---
elif user_type == "통계용":
    st.subheader("📊 로또 당첨 통계")
    reward_stats = {
        "치킨": 0,
        "햄버거세트": 0,
        "매점이용권": 0,
        "0.5코인": 0
    }
    winners = data[data["기록"].str.contains("로또")]
    for index, row in winners.iterrows():
        records = ast.literal_eval(row["기록"])
        for record in records:
            if record.get("reward") in reward_stats:
                reward_stats[record["reward"]] += 1
    st.write("전체 당첨 횟수:")
    st.write(reward_stats)
    st.write("3등 이상 당첨자 목록:")
    winners_list = []
    for index, row in winners.iterrows():
        records = ast.literal_eval(row["기록"])
        for record in records:
            if record.get("reward") in ["치킨", "햄버거세트", "매점이용권"]:
                winners_list.append({
                    "학생": row["학생"],
                    "당첨 보상": record["reward"],
                    "당첨 날짜": record["timestamp"]
                })
    st.write(pd.DataFrame(winners_list))
    st.write("로또 당첨 분석이 완료되었습니다.")

st.markdown('</div>', unsafe_allow_html=True)
