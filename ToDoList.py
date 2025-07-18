import streamlit as st
import datetime
import pickle
import os

DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

# CSS 스타일 삽입
st.markdown("""
<style>
.task-card {
    background-color: #f9fafb;
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 12px;
    box-shadow: 0 3px 6px rgba(0,0,0,0.1);
    transition: box-shadow 0.3s ease;
}
.task-card:hover {
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}
.task-title {
    font-weight: 700;
    font-size: 18px;
    color: #0a2647;
    margin-bottom: 4px;
}
.task-date {
    font-size: 14px;
    color: #52616b;
    margin-bottom: 8px;
}
.checkbox-col {
    padding-top: 6px;
}
.btn-small {
    padding: 4px 8px;
    font-size: 14px;
    border-radius: 6px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ---------- 로그인 & 회원가입 ----------
def login():
    st.title("🔐 로그인 또는 회원가입")

    mode = st.radio("모드 선택", ["로그인", "회원가입"], horizontal=True)

    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    user_file = os.path.join(DATA_DIR, f"{username}.pkl")

    if mode == "로그인":
        if st.button("로그인"):
            if os.path.exists(user_file):
                with open(user_file, "rb") as f:
                    user_data = pickle.load(f)
                if user_data.get("password") == password:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["tasks"] = user_data.get("tasks", [])
                    st.success("로그인 성공")
                else:
                    st.error("❌ 비밀번호가 틀렸습니다.")
            else:
                st.error("❌ 존재하지 않는 아이디입니다.")
    else:
        if st.button("회원가입"):
            if os.path.exists(user_file):
                st.error("이미 존재하는 아이디입니다.")
            else:
                with open(user_file, "wb") as f:
                    pickle.dump({"password": password, "tasks": []}, f)
                st.success("회원가입 완료! 로그인 해주세요.")

# ---------- 데이터 저장 ----------
def save_data():
    username = st.session_state["username"]
    user_file = os.path.join(DATA_DIR, f"{username}.pkl")
    with open(user_file, "wb") as f:
        pickle.dump({
            "password": get_password(username),
            "tasks": st.session_state["tasks"]
        }, f)

def get_password(username):
    user_file = os.path.join(DATA_DIR, f"{username}.pkl")
    if os.path.exists(user_file):
        with open(user_file, "rb") as f:
            return pickle.load(f).get("password")
    return None

# ---------- 수정 화면 ----------
def edit_task(index):
    st.markdown("### ✏️ 할 일 수정")
    original = st.session_state["tasks"][index]
    new_task = st.text_input("수정할 내용", value=original["task"])
    new_due = st.date_input("새 마감일", value=original["due"])

    if st.button("수정 완료"):
        if new_task.strip() == "":
            st.warning("내용을 입력해주세요.")
            return
        st.session_state["tasks"][index]["task"] = new_task
        st.session_state["tasks"][index]["due"] = new_due
        save_data()
        st.success("수정 완료!")
        st.experimental_rerun()

    if st.button("취소"):
        st.experimental_rerun()

# ---------- 메인 앱 ----------
def todo_app():
    st.title(f"📋 {st.session_state['username']}님의 To-Do List")
    st.markdown("---")

    # 할 일 추가 폼
    with st.form("add_task"):
        task = st.text_input("할 일 내용")
        due_date = st.date_input("마감 날짜", min_value=datetime.date.today())
        submitted = st.form_submit_button("추가")
        if submitted:
            if task.strip() == "":
                st.warning("할 일 내용을 입력해주세요.")
            else:
                st.session_state["tasks"].append({
                    "task": task,
                    "due": due_date,
                    "done": False
                })
                save_data()
                st.success("할 일이 추가되었습니다.")

    # 검색 기능
    search_keyword = st.text_input("🔍 할 일 검색")
    filtered_tasks = st.session_state["tasks"]
    if search_keyword:
        filtered_tasks = [t for t in filtered_tasks if search_keyword.lower() in t["task"].lower()]

    # 임박 일정 필터
    filter_days = st.slider("며칠 이내 마감된 일정 보기", 0, 14, 0)
    today = datetime.date.today()
    if filter_days > 0:
        deadline = today + datetime.timedelta(days=filter_days)
        filtered_tasks = [t for t in filtered_tasks if today <= t["due"] <= deadline]

    # 완료된 할 일 숨기기
    hide_done = st.checkbox("완료된 할 일 숨기기")
    if hide_done:
        filtered_tasks = [t for t in filtered_tasks if not t["done"]]

    st.markdown("### 📆 할 일 목록")
    if not filtered_tasks:
        st.info("표시할 할 일이 없습니다.")
    else:
        for i, task in enumerate(filtered_tasks):
            # 카드형 디자인 출력
            done = task["done"]
            task_html = f"""
            <div class="task-card">
                <div class="task-title">{'✅' if done else '📝'} {task['task']}</div>
                <div class="task-date">📅 마감일: {task['due']}</div>
            </div>
            """
            st.markdown(task_html, unsafe_allow_html=True)

            cols = st.columns([0.1, 0.1, 0.1])
            with cols[0]:
                done_checkbox = st.checkbox("완료", value=done, key=f"done_{i}")
                st.session_state["tasks"][i]["done"] = done_checkbox
            with cols[1]:
                if st.button("✏️ 수정", key=f"edit_{i}"):
                    edit_task(i)
                    return
            with cols[2]:
                if st.button("🗑️ 삭제", key=f"del_{i}"):
                    st.session_state["tasks"].pop(i)
                    save_data()
                    st.experimental_rerun()

    st.markdown("---")
    if st.button("저장"):
        save_data()
        st.success("저장 완료 ✅")

    if st.button("로그아웃"):
        st.session_state.clear()
        st.experimental_rerun()

# ---------- 실행 ----------
def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        todo_app()
    else:
        login()

if __name__ == "__main__":
    main()
