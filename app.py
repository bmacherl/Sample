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

# ---- Page settings ----
st.set_page_config(page_title="HRMS Portal", layout="wide")

# ---- ASU Banner ----
st.image("asu_banner.jpg", use_container_width=True)

# ---- App Title ----
st.markdown("<h2 style='text-align: center;'>Welcome to MyASU-Inspired HRMS Portal</h2>", unsafe_allow_html=True)

# ---- Load users ----
@st.cache_data
def load_users():
    return pd.read_csv("users.csv")

df_users = load_users()

# ---- Login Section ----
st.subheader("🔐 Login")
email = st.text_input("Enter your ASU email to log in:")

if email:
    if email in df_users['email'].values:
        user = df_users[df_users['email'] == email].squeeze()
        st.success(f"Welcome {user['name']}! You are logged in as **{user['role']}**.")

        # Sidebar menu using radio with icons
        st.sidebar.title("📂 Menu")
        menu = st.sidebar.radio("Navigate to:", 
            ["👤 Profile", "📆 Attendance", "💵 Payroll", "🏦 Finances"]
        )
        role = user['role']

        # ---- Profile Section ----
        if menu == "👤 Profile":
            st.subheader("👤 Profile")
            st.write(user)

        # ---- Attendance Section ----
        if menu == "📆 Attendance":
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

        # ---- Payroll Section ----
        if menu == "💵 Payroll":
            if role in ["Staff", "Payroll_Admin", "Admin"]:
                st.subheader("💵 Payroll")
                st.write("Payroll summary coming soon!")
            else:
                st.warning("Access denied: Payroll is restricted.")

        # ---- Finances Section ----
        if menu == "🏦 Finances":
            if role in ["Student", "Admin"]:
                st.subheader("🏦 Finances")
                st.write("Fee info and payments coming soon!")
            else:
                st.warning("Access denied: Finances only for students/admins.")
    else:
        st.error("Email not found. Please try again or contact admin.")
