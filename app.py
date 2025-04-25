import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from deepface import DeepFace
import requests
import numpy as np
from PIL import Image
from io import BytesIO

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

        # Normalize 'working' column to ensure it works for comparison
        is_student_working = str(user.get('working', 'No')).strip().lower() == "yes"

        # Sidebar menu with icons to navigate to different pages
        st.sidebar.title("📂 Menu")
        
        menu_options = ["👤 Profile", "📆 Attendance", "💵 Payroll", "🏦 Finances", "📚 Courses"]

        # Add visibility conditions based on role and whether student is working
        if user['role'] == "Admin":
            menu = st.sidebar.radio("Navigate to:", menu_options)
        elif user['role'] == "Professor":
            # Professors can see all except Courses
            menu = st.sidebar.radio("Navigate to:", menu_options)
        elif user['role'] == "Payroll_Admin":
            menu = st.sidebar.radio("Navigate to:", menu_options)
        elif user['role'] == "Staff":
            # Staff can always see Payroll
            menu = st.sidebar.radio("Navigate to:", menu_options)
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

                        # Add the "Record Attendance" button
                        record_button = st.button("Record Attendance")
                        
                        if record_button:
                            st.success("Attendance recorded successfully!")  # Add your logic here to record attendance

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
            # **Staff** and **Professors** always see Payroll; **Students** only see Payroll if working
            if user['role'] == "Staff" or user['role'] == "Professor" or is_student_working:
                st.subheader("💵 Payroll")
                st.write("Payroll summary coming soon!")
            else:
                st.warning("Access denied: Payroll is restricted.")

        # ---- Finances Page ----
        elif menu == "🏦 Finances":
            if user['role'] == "Admin":
                st.subheader("🏦 Finances")
                st.write("Fee info and payments coming soon!")
            else:
                st.warning("Access denied: Finances only for Admins.")

        # ---- Courses Page (for students) ----
        elif menu == "📚 Courses" and user['role'] == "Student":
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

        # ---- Attendance Model Using DeepFace ----
        if menu == "📆 Attendance" and user['role'] == "Student":
            st.subheader("Capture and Compare Image for Attendance")

            # Button to start webcam capture
            if st.button("Record Attendance"):
                st.info("Please take your picture for attendance")

                # Capture image from webcam
                captured_image = st.camera_input("Capture your image")
                if captured_image:
                    image = Image.open(captured_image)
                    st.image(image, caption="Captured Image", use_column_width=True)

                    # GitHub repository URL of student images
                    github_repo_url = "https://raw.githubusercontent.com/bmacherl/students_images/main"

                    # Fetch student images from GitHub
                    def fetch_images_from_github(github_repo_url):
                        image_urls = []
                        for i in range(1, 6):  # Adjust the range as per the number of students in your dataset
                            image_url = f"{github_repo_url}/students_images/{i}_Bhanu.jpg"
                            image_urls.append(image_url)
                        return image_urls

                    # Compare captured image with images from GitHub
                    def compare_images(captured_image, image_urls):
                        captured_image = np.array(captured_image)
                        captured_encodings = DeepFace.represent(captured_image, model_name="VGG-Face")
                        for url in image_urls:
                            try:
                                response = requests.get(url)
                                img = Image.open(BytesIO(response.content))
                                img = np.array(img)
                                img_encodings = DeepFace.represent(img, model_name="VGG-Face")

                                # Compare the encodings
                                similarity = DeepFace.verify(captured_encodings, img_encodings)
                                if similarity['distance'] < 0.6:  # You can adjust the threshold for better accuracy
                                    return url.split("/")[-1].split(".")[0]  # Return the student's name
                            except Exception as e:
                                st.error(f"Error fetching image from URL: {url}. Error: {str(e)}")
                        return None  # No match found

                    # Fetch images from GitHub and compare with the captured image
                    image_urls = fetch_images_from_github(github_repo_url)
                    matched_student = compare_images(image, image_urls)
                    if matched_student:
                        st.success(f"Attendance recorded for: {matched_student}")
                    else:
                        st.error("No match found! Attendance could not be recorded.")
