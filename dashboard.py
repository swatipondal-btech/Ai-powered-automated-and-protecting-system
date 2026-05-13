import streamlit as st
import pandas as pd
import os
import time
import json

st.set_page_config(page_title="AI Proctoring System", layout="wide", page_icon="🛡️")

# Custom CSS for premium look
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    .stButton>button {
        background: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background: #155a8a;
    }
</style>
""", unsafe_allow_html=True)

# Load students data
def load_students():
    if os.path.exists('students.json'):
        with open('students.json', 'r') as f:
            return json.load(f)
    return {"students": [], "admin": {"username": "admin", "password": "admin123"}}

def save_students(data):
    with open('students.json', 'w') as f:
        json.dump(data, f, indent=2)

students_data = load_students()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

def login_page():
    st.markdown('<h1 class="main-header">🛡️ AI Proctoring System</h1>', unsafe_allow_html=True)
    st.subheader("Login")
    
    user_type = st.radio("Login as:", ["Student", "Admin"])
    
    if user_type == "Student":
        student_id = st.text_input("Student ID")
        password = st.text_input("Password", type="password")
        if st.button("Login as Student"):
            for student in students_data["students"]:
                if student["id"] == student_id and student["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_type = "student"
                    st.session_state.user_name = student["name"]
                    st.success(f"Welcome, {student['name']}!")
                    st.rerun()
                    break
            else:
                st.error("Invalid credentials")
    else:
        username = st.text_input("Admin Username")
        password = st.text_input("Password", type="password")
        if st.button("Login as Admin"):
            if username == students_data["admin"]["username"] and password == students_data["admin"]["password"]:
                st.session_state.logged_in = True
                st.session_state.user_type = "admin"
                st.session_state.user_name = "Admin"
                st.success("Welcome, Admin!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")

def student_page():
    st.markdown(f'<h1 class="main-header">Welcome, {st.session_state.user_name}</h1>', unsafe_allow_html=True)
    st.subheader("Student Proctoring Session")
    
    st.info("To start your proctoring session, run the following command in a separate terminal:")
    st.code(f'py main.py "{st.session_state.user_name}"', language='bash')
    st.write("This will open the camera and monitor your exam session.")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

def admin_page():
    st.markdown('<h1 class="main-header">Admin Dashboard</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "👥 Manage Students", "📋 Student Records"])
    
    with tab1:
        LOG_FILE = 'SuspiciousLog.csv'
        df = load_data(LOG_FILE)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Students", len(students_data["students"]))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            latest_score = int(df['SuspicionScore'].iloc[-1]) if not df.empty and 'SuspicionScore' in df.columns else 0
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Current Suspicion Score", f"{latest_score}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            total_warnings = len(df)
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Suspicious Events", f"{total_warnings}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📋 Activity Log")
        if not df.empty:
            st.dataframe(df.sort_values(by='Timestamp', ascending=False), use_container_width=True)
        else:
            st.info("No activity logged yet.")
    
    with tab2:
        st.subheader("Manage Students")
        for i, student in enumerate(students_data["students"]):
            col1, col2, col3 = st.columns([2,2,1])
            with col1:
                st.write(f"**{student['name']}** ({student['id']})")
            with col2:
                st.write(student['email'])
            with col3:
                if st.button(f"Remove {student['id']}", key=f"remove_{i}"):
                    students_data["students"].pop(i)
                    save_students(students_data)
                    st.success("Student removed")
                    st.rerun()
        
        st.subheader("Add New Student")
        with st.form("add_student"):
            name = st.text_input("Name")
            sid = st.text_input("ID")
            pwd = st.text_input("Password", type="password")
            email = st.text_input("Email")
            if st.form_submit_button("Add Student"):
                students_data["students"].append({"name": name, "id": sid, "password": pwd, "email": email})
                save_students(students_data)
                st.success("Student added")
    
    with tab3:
        st.subheader("Student Records")
        student_names = [s["name"] for s in students_data["students"]]
        selected_student = st.selectbox("Select Student", student_names)
        if selected_student:
            df = load_data(LOG_FILE)
            student_df = df[df['Student'] == selected_student]
            if not student_df.empty:
                st.dataframe(student_df.sort_values(by='Timestamp', ascending=False))
                # Show metrics for this student
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Suspicious Events", len(student_df))
                with col2:
                    avg_score = student_df['SuspicionScore'].mean() if 'SuspicionScore' in student_df.columns else 0
                    st.metric("Average Suspicion Score", f"{avg_score:.1f}")
            else:
                st.info(f"No records for {selected_student}")
    
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

def load_data(log_file):
    expected_columns = ['Timestamp', 'Student', 'Activity', 'SuspicionScore', 'ScreenshotFile']
    if os.path.exists(log_file):
        try:
            df = pd.read_csv(log_file)
            if len(df.columns) < len(expected_columns):
                df = pd.read_csv(log_file, header=None, names=expected_columns)
            return df
        except Exception:
            return pd.DataFrame(columns=expected_columns)
    return pd.DataFrame(columns=expected_columns)

# Main app
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.user_type == "student":
        student_page()
    elif st.session_state.user_type == "admin":
        admin_page()
