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
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1wjciGq95qos6h1dBwUvMB56QhRRj-GZq3DS_btspsfE/edit?gid=1589455850#gid=1589455850/edit"
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

# 헤더 비트코인 GIF 이미지
st.markdown(
    '<div style="text-align:center;">'
    '<img class="header-img" src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExemVldTNsMGVpMjZzdjhzc3hnbzl0d2szYjNoNXY2ZGt4ZXVtNncyciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/30VBSGB7QW1RJpNcHO/giphy.gif" alt="Bitcoin GIF">'
    '</div>',
    unsafe_allow_html=True
)

# --- 🌟 학생/교사 선택 --- 
user_type = st.sidebar.radio("모드를 선택하세요", ["학생용", "교사용"])

# 디버그 메시지 출력 영역
debug_message = st.empty()
debug_message.text("디버그 메시지가 여기에 표시됩니다.")

# HTML과 JavaScript를 통해 키보드 이벤트 감지
st.markdown("""
    <script>
    window.addEventListener('keydown', function(e) {
        // 'z', 'x', 'c' 키를 동시에 누르면
        if (e.key == 'z' && e.ctrlKey && e.shiftKey) {
            // JavaScript에서 Streamlit에 메시지를 전달
            window.parent.postMessage({ type: 'streamlit:setComponentValue', value: '디버그 출력: z, x, c 동시에 눌림' }, '*');
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 🎓 교사용 UI --- 
if user_type == "교사용":
    data = load_data()
    selected_class = st.selectbox("반을 선택하세요:", data["반"].unique())
    filtered_data = data[data["반"] == selected_class]
    selected_student = st.selectbox("학생을 선택하세요:", filtered_data["학생"].tolist())
    student_index = data[(data["반"] == selected_class) & (data["학생"] == selected_student)].index[0]

    password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
    if password == st.secrets["general"]["admin_password"]:  # 비밀번호 확인
        coin_amount = st.number_input("부여 또는 회수할 코인 수:", min_value=-100, max_value=100, value=1)

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

        if st.button("⚠️ 세진코인 초기화"):
            data.at[student_index, "세진코인"] = 0
            data.at[student_index, "기록"] = "[]"
            save_data(data)
            st.error(f"{selected_student}의 세진코인이 초기화되었습니다.")

        updated_student_data = data.loc[[student_index]]
        st.subheader(f"{selected_student}의 업데이트된 세진코인")
        st.dataframe(updated_student_data)

    else:
        st.warning("비밀번호가 틀렸습니다!")

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
    
    # 코인 개수 출력
    if student_coins < 1:
        coin_display = f"<h2 style='color: gray;'>😐 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    elif student_coins >= 5 and student_coins < 10:
        coin_display = f"<h2 style='color: green;'>😊 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    elif student_coins >= 10:
        coin_display = f"<h2 style='color: yellow;'>🎉 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    else:
        coin_display = f"<h2 style='color: red;'>😢 {selected_student}님의 세진코인은 {student_coins}개입니다.</h2>"
    
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
                st.success("🎉 4등 당첨! 상품: 초코송이")
                reward = "초코송이"
                data.at[student_index, "세진코인"] += 0.5
            else:
                st.info("🎰 아쉽게도 당첨되지 않았습니다.")

            # 업데이트된 코인 표시
            st.markdown(f"<h3>업데이트된 {selected_student}님의 세진코인: {data.at[student_index, '세진코인']}개</h3>", unsafe_allow_html=True)

            save_data(data)
