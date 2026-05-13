  AI AUTOMATED PROCTORING SYSTEM PROJECT GUIDE

 1. What is this Project About?
This project is an AI Proctoring System designed to monitor students during online exams. Just like a human invigilator watches students in an exam hall, this AI system uses a computer's webcam to watch the student. 
It detects if the student is missing, if there are multiple people in the room, or if the student is looking away from the screen for too long. It also features web portals for the Admin (to manage students and see logs) and the Student (to start the exam).

---

 2. Tools and Technologi
 Python: The core programming language used to build the entire system.
 OpenCV (`cv2`): Used for accessing the webcam, reading video frames, and drawing warnings on the screen.
MediaPipe: Google's AI framework used here for detecting faces and mapping facial landmarks in real-time.
Streamlit: A Python framework used to create the beautiful web-based user interfaces (Admin Dashboard and Student Portal).
 Pandas: A data analysis library used to read, manage, and write data to our CSV "databases".

---

3. How to Run on a New Laptop (Step-by-Step)

If you are moving this project to a completely new system, follow these steps exactly:

Pre-requisites (What you need before starting):
You must have Python installed on your computer. You can download it from [python.org](https://www.python.org/).

Step 1: Download the Project
Copy the entire project folder (containing `main.py`, `student_portal.py`, etc.) to your new laptop. 

Step 2: Open Terminal / Command Prompt
Open your terminal (or Command Prompt / PowerShell in Windows) and navigate to the project folder. You can do this by opening the folder in VS Code and opening the terminal there.

Step 3: Install Required Libraries
You need to download the tools we used. Run this command in the terminal:
```bash
pip install -r requirements.txt
```(This will automatically download OpenCV, MediaPipe, Streamlit, and Pandas).

Step 4: Run the Admin Dashboard
To see the Admin panel, open a new terminal in the same folder and type:
```bash
streamlit run admin_dashboard.py
```
(Login with Username: `admin` and Password: `admin123`)

Step 5: Run the Student Portal
To start the student side, open another terminal and type:
`bash
streamlit run student_portal.py
```(Login with a student account created by the Admin. Once logged in, click "Launch Camera & Start Exam" to start the AI engine).

-

 4. How We Built This Project (Process Phase)

Here is the sequential story of how this project was developed, step by step:

Phase 1: Planning and Environment Setup
First, we created a `requirements.txt` file. This is like a shopping list of tools we need (OpenCV for camera, Streamlit for web pages). 

Phase 2: Building the Core AI Engine (`main.py`)
This was the most important step. We wrote a Python script that turns on the webcam and uses MediaPipe to detect faces. We added math logic to calculate "Pitch" and "Yaw" (angles of the head) to know if the student is looking Left, Right, Up, or Down. 

Phase 3: Creating the Database (CSV Files)
Instead of using complex database software like MySQL, we used simple `.csv` files (Excel-like files) to act as our database.
users.csv`: Stores usernames and passwords.
`Attendance.csv`: Marks when a student appears on camera.
 `SuspiciousLog.csv`: Records every time a student does something wrong.

Phase 4: Building the Admin Dashboard (`admin_dashboard.py`)
We used Streamlit to build a secure webpage where an admin can log in. We designed it to read the CSV files and show total infractions, photos of suspicious activity, and gave the admin buttons to block or unblock students.

Phase 5: Building the Student Portal (`student_portal.py`)
Finally, we built a login page for students. This page checks if the student is blocked. If they are active, it provides a big button that magically opens the AI camera engine (`main.py`).

---

5. Detailed Code Analysis (How It Works Internally)

Let's understand how the code is written in simple terms.

A. How `main.py` was built (The AI Engine)
 What was added:We imported `cv2` and `mediapipe`. We created a class `ProctoringSystem` that manages everything.
 The Backend Logic: The system continuously captures pictures from the webcam (frames). For each picture, MediaPipe checks for a face. If it finds 0 faces or more than 1 face, it increases a "Suspicion Score". 
Database Storage:When a suspicious event happens (like looking away for too long), `main.py` writes a line of text into `SuspiciousLog.csv`. It also uses `cv2.imwrite()` to save a picture (screenshot) of the student into the `screenshots` folder.
B. How `main.py` Connects to the Dashboards
They communicate through Files 
1. `main.py` acts as the **Writer**. It writes logs and saves screenshots.
2. `admin_dashboard.py` acts as the Reader It opens those same logs and screenshots to display them to the admin.

C. How `student_portal.py` was built-Authentication: It uses Pandas to open `users.csv` and checks if the typed username and password match.
 The Connection to Engine: When the student clicks "Start Exam", the portal uses a Python tool called `subprocess.Popen()`. This command tells the computer: *"Hey, silently open `main.py` in the background and pass the student's name to it."* This is how the web portal launches the desktop camera.

D. How `admin_dashboard.py` was built
Layout: We used Streamlit tabs (`st.tabs`) to divide the page into Overview, Student Records, and Manage Accounts.
 Data Display: It uses `pd.read_csv()` to load the data. For the Student Records, it filters the data to show only logs matching a specific student, and uses `st.image()` to display the photos saved in the `screenshots` folder.
 Actions: When the admin clicks "Block", the code updates the `users.csv` file, changing the student's status from 'Active' to 'Blocked'. The next time the student tries to log in to the Student Portal, the portal reads the 'Blocked' status and stops them.


Summary:This project is a perfect combination of Computer Vision (AI seeing things) and Web Development (Dashboards displaying things), connected seamlessly using simple data files!


