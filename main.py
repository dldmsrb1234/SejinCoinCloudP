import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- Firebase 설정 ---
if not firebase_admin._apps:
    cred = credentials.Certificate(r"firebase_config.json")

  # Firebase JSON 키 파일 로드
    firebase_admin.initialize_app(cred)

db = firestore.client()  # Firestore 클라이언트

# --- 관리자 비밀번호 (환경 변수로 설정하는 것이 안전) ---
ADMIN_PASSWORD = "wjddusdlcjswo"

# --- UI 스타일 추가 ---
st.markdown(
    """
    <style>
    body {
        background-color: #1e1e1e;
        color: white;
        font-family: Arial, sans-serif;
    }
    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        color: #FFD700;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.05);
    }
    .stSelectbox, .stTextInput {
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- UI 구성 ---
st.markdown("<h1 class='title'>세진코인 관리 시스템 (Firebase)</h1>", unsafe_allow_html=True)

# 반 리스트 가져오기
classes_ref = db.collection("classes")
class_docs = classes_ref.stream()
class_list = [doc.id for doc in class_docs]

selected_class = st.selectbox("반을 선택하세요:", class_list)

# 학생 리스트 가져오기
students_ref = db.collection("classes").document(selected_class).collection("students")
student_docs = students_ref.stream()
student_list = [doc.id for doc in student_docs]

selected_student = st.selectbox("학생을 선택하세요:", student_list)

# 비밀번호 입력
password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")

if password == ADMIN_PASSWORD:
    student_ref = students_ref.document(selected_student)
    student_data = student_ref.get()

    if student_data.exists:
        student_info = student_data.to_dict()
        st.metric(f"{selected_student}의 세진코인", student_info["세진코인"])
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("세진코인 부여"):
                student_ref.update({
                    "세진코인": student_info["세진코인"] + 1,
                    "기록": firestore.ArrayUnion([1])
                })
                st.success(f"{selected_student}에게 1코인 부여!")
                time.sleep(45)
                st.experimental_rerun()

        with col2:
            if st.button("세진코인 회수"):
                student_ref.update({
                    "세진코인": max(0, student_info["세진코인"] - 1),
                    "기록": firestore.ArrayUnion([-1])
                })
                st.warning(f"{selected_student}에게서 1코인 회수!")
                time.sleep(45)
                st.experimental_rerun()

    else:
        st.error("학생 데이터를 찾을 수 없습니다.")

# 전체 학생 코인 현황 보기
if st.checkbox("전체 학생 세진코인 현황 보기"):
    st.subheader("전체 학생 세진코인 현황")
    all_students = students_ref.stream()
    
    student_data_list = [
        {"학생": doc.id, "세진코인": doc.to_dict().get("세진코인", 0)}
        for doc in all_students
    ]
    
    st.dataframe(student_data_list)
