import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---- Pie Chart Helper ----
def pie_chart(attended, missed):
    fig, ax = plt.subplots()
    ax.pie(
        [attended, missed],
        labels=["Attended", "Missed"],
        colors=["#4CAF50", "#F44336"],
        startangle=90,
        autopct="%1.1f%%"
    )
    ax.axis("equal")
    return fig

# ---- Load users and courses ----
@st.cache_data
def load_users():
    return pd.read_csv("users.csv")

@st.cache_data
def load_courses():
    return pd.read_csv("courses.csv")

df_users = load_users()
df_courses = load_courses()

# ---- Page settings ----
st.set_page_config(page_title="HRMS Portal", layout="wide")

# ---- ASU Banner ----
st.image("asu_banner.jpg", use_container_width=True)

# ---- App Title ----
st.markdown("<h2 style='text-align: center;'>Welcome to MyASU-Inspired HRMS Portal</h2>", unsafe_allow_html=True)

# ---- Login Section ----
st.subheader("🔐 Login")
email = st.text_input("Enter your ASU email to log in:")

if email:
    if email in df_users['email'].values:
        user = df_users[df_users['email'] == email].squeeze()
        st.success(f"Welcome {user['name']}! You are logged in as **{user['role']}**.")

        # Check if 'working' column exists for students
        is_student_working = user.get('working', 'No') == "Yes"  # Default to 'No' if 'working' column doesn't exist

        # Sidebar menu with icons to navigate to different pages
        st.sidebar.title("📂 Menu")
        
        menu_options = ["👤 Profile", "📆 Attendance", "💵 Payroll", "🏦 Finances", "📚 Courses"]

        # Add visibility conditions based on role and whether student is working
        if user['role'] == "Admin":
            # Admins can see all options
            menu = st.sidebar.radio("Navigate to:", menu_options)
        elif user['role'] == "Professor":
            # Professors can see all except Courses
            menu = st.sidebar.radio("Navigate to:", menu_options[:-1])
        elif user['role'] == "Student":
            # Students can see Profile, Attendance, and Courses, and Payroll if they are working
            if is_student_working:
                menu = st.sidebar.radio("Navigate to:", ["👤 Profile", "📆 Attendance", "💵 Payroll", "📚 Courses"])
            else:
                menu = st.sidebar.radio("Navigate to:", ["👤 Profile", "📆 Attendance", "📚 Courses"])
        else:
            menu = st.sidebar.radio("Navigate to:", ["👤 Profile", "📆 Attendance"])

        role = user['role']

        # ---- Profile Page ----
        if menu == "👤 Profile":
            st.subheader("👤 Profile")
            st.write(user)

        # ---- Attendance Page ----
        elif menu == "📆 Attendance":
            if role == "Student":  # ✅ Checking exactly as written in the CSV
                st.subheader("📆 Attendance")

                attendance_option = st.radio("Choose an option:", ["Show Attendance for Now", "View Course-wise Attendance"])

                if attendance_option == "Show Attendance for Now":
                    view_type = st.radio("View by:", ["Day-wise", "Week-wise"])

                    if view_type == "Day-wise":
                        st.info("📅 Day-wise tracking is a work in progress.")

                    elif view_type == "Week-wise":
                        st.subheader("📊 Weekly Attendance Breakdown")

                        # Sample data for visualization
                        courses = {
                            "AI and Data Analytics": {"total_hours": 5, "classes": 2, "attended": 1},
                            "Logistics in Supply Chain": {"total_hours": 5, "classes": 2, "attended": 2}
                        }

                        for course, stats in courses.items():
                            st.markdown(f"**{course}**")
                            attendance_ratio = stats["attended"] / stats["classes"]
                            attended_hours = attendance_ratio * stats["total_hours"]

                            st.write(f"Total Hours: {stats['total_hours']}")
                            st.write(f"Attended Classes: {stats['attended']} / {stats['classes']}")
                            st.write(f"Attended Hours: {attended_hours:.1f}")
                            st.pyplot(pie_chart(attended_hours, stats["total_hours"] - attended_hours))
                else:
                    semester = st.selectbox("Select Semester", ["Semester 1", "Semester 2", "Semester 3"])

                    if semester == "Semester 1":
                        st.warning("🕰 Semester 1 is over. Past data not available.")
                    elif semester == "Semester 2":
                        sub_period = st.radio("Select Period", ["Jan–Mar", "Mar–May"])
                        if sub_period == "Jan–Mar":
                            st.warning("📅 Data not yet updated for Jan–Mar.")
                        elif sub_period == "Mar–May":
                            st.success("✅ Courses: AI and Data Analytics, Logistics in Supply Chain")
                    else:
                        st.warning("🚧 Semester 3 has not started yet.")
            else:
                st.warning("⛔ You do not have permission to view attendance.")

        # ---- Payroll Page ----
        elif menu == "💵 Payroll":
            # Admins, Professors, and Students who are working can access Payroll
            if role in ["Admin", "Professor"] or is_student_working:
                st.subheader("💵 Payroll")
                st.write("Payroll summary coming soon!")
            else:
                st.warning("Access denied: Payroll is restricted.")

        # ---- Finances Page ----
        elif menu == "🏦 Finances":
            if role == "Admin":
                st.subheader("🏦 Finances")
                st.write("Fee info and payments coming soon!")
            else:
                st.warning("Access denied: Finances only for Admins.")

        # ---- Courses Page (for students) ----
        elif menu == "📚 Courses" and role == "Student":
            st.subheader("📚 Your Courses")
            
            # Filter courses for the logged-in student
            student_courses = df_courses[df_courses['email'] == email]

            if student_courses.empty:
                st.write("You are not enrolled in any courses.")
            else:
                # Show courses semester-wise
                semesters = student_courses['semester'].unique()
                for semester in semesters:
                    st.markdown(f"### {semester}")
                    semester_courses = student_courses[student_courses['semester'] == semester]
                    for _, course_row in semester_courses.iterrows():
                        st.write(f"📘 {course_row['course_name']}")
                
    else:
        st.error("Email not found. Please try again or contact admin.")
