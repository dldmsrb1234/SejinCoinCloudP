import streamlit as st
import pandas as pd
import random
import time

# Google Sheets 데이터 불러오기
@st.cache_data
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    df = pd.read_csv(sheet_url)
    return df

def save_data(df):
    df.to_csv("student_data.csv", index=False)

def add_record(df, index, activity, result, detail):
    new_record = f"{activity}: {result} ({detail})"
    df.at[index, "기록"] = f"{df.at[index, '기록']} | {new_record}" if pd.notna(df.at[index, "기록"]) else new_record

# 초기화
data = load_data()
st.title("🎲 학생 코인 관리 시스템")

student_name = st.text_input("이름을 입력하세요:")
if student_name:
    student_row = data[data["이름"] == student_name]

    if student_row.empty:
        st.error("존재하지 않는 학생입니다.")
    else:
        student_index = student_row.index[0]
        student_coins = data.at[student_index, "세진코인"]

        st.write(f"💰 현재 세진코인: `{student_coins}`")

        # ✅ 코인 추가 / 차감 기능
        with st.expander("💰 코인 관리"):
            change_amount = st.number_input("변경할 코인 수", min_value=-100, max_value=100, value=0)
            if st.button("코인 업데이트"):
                data.at[student_index, "세진코인"] += change_amount
                add_record(data, student_index, "코인 변경", f"{change_amount:+}", "관리자 조정")
                save_data(data)
                st.success(f"✅ 코인이 {change_amount:+}만큼 변경되었습니다!")

        # ✅ 로또 게임 추가
        st.header("🎯 로또 게임")
        chosen_numbers = st.multiselect("1~20 사이에서 3개의 숫자를 선택하세요.", list(range(1, 21)), default=[])

        if len(chosen_numbers) == 3 and st.button("로또 게임 시작"):
            if student_coins < 1:
                st.error("세진코인이 부족합니다.")
            else:
                data.at[student_index, "세진코인"] -= 1
                main_balls = random.sample(range(1, 21), 3)
                bonus_ball = random.choice([n for n in range(1, 21) if n not in main_balls])

                st.markdown(f"🎲 **추첨 중...**", unsafe_allow_html=True)
                time.sleep(2)

                st.write(f"🎯 **당첨번호:** `{sorted(main_balls)}` | 보너스 볼: `{bonus_ball}`")
                matches = set(chosen_numbers) & set(main_balls)

                reward = "꽝"
                if len(matches) == 3:
                    reward = "🎉 **치킨 당첨! 🍗**"
                elif len(matches) == 2 and bonus_ball in chosen_numbers:
                    reward = "🍔 **햄버거세트 당첨!**"
                elif len(matches) == 2:
                    reward = "🛒 **매점 이용권 당첨!**"
                elif len(matches) == 1:
                    reward = "🪙 **0.5 세진코인 지급!**"
                    data.at[student_index, "세진코인"] += 0.5
                else:
                    reward = "❌ **아쉽지만 꽝! 다음 기회에...**"

                add_record(data, student_index, "로또", reward, f"선택: {chosen_numbers}")
                save_data(data)

                # 결과 출력
                if reward != "꽝":
                    st.success(f"🎉 {reward}")
                else:
                    st.warning(f"{reward}")

        # ✅ 기록 조회
        st.header("📜 기록 조회")
        if pd.notna(data.at[student_index, "기록"]):
            st.text_area("📌 최근 활동 기록", data.at[student_index, "기록"], height=150)
        else:
            st.info("기록이 없습니다.")

