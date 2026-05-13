# AI Proctoring System - Documentation & Setup Guide

## 📌 What is this project?
This is an advanced **AI-powered Proctoring System** built for hackathons and academic integrity monitoring. It uses computer vision to continuously monitor a candidate taking an exam. 

**Key Features (The Flow):**
1. **Face Verification**: Matches the candidate's face against a known student database.
2. **Absence Detection**: Flags if the candidate leaves the camera frame.
3. **Multiple Face Detection**: Alerts if a second person enters the frame.
4. **Suspicious Movement (Head Pose)**: Uses 3D Face Mesh mapping to detect if the student is continuously looking Left, Right, Up, or Down.
5. **Suspicion Scoring Engine**: A mathematical score that dynamically increases upon suspicious events and triggers evidence capture.
6. **Evidence Capture**: Automatically takes a screenshot of the frame when a major violation occurs.
7. **Live Dashboard**: A clean, auto-refreshing Streamlit dashboard to review logs and screenshot evidence.

**Why it doesn't look copy-pasted:**
- We implemented an Object-Oriented structure (`ProctoringSystem` class) which is rare in standard OpenCV tutorials.
- We combined multiple heavy AI models efficiently (dlib's face_recognition + Google's MediaPipe Face Mesh) in a single loop.
- It dynamically manages a "Suspicion Score" rather than just hardcoded print statements.
- Includes a full-fledged accompanying web dashboard.

---

## 🚀 How to Run on a New Laptop (Step-by-Step)

If you are moving this project to a new laptop for presentation or testing, follow these exact steps:

### Step 1: Install Python
Ensure Python 3.8+ is installed on the new laptop. Also ensure you have a C++ compiler installed (On Windows, this is usually *Visual Studio Build Tools* which is required to compile `dlib` for `face_recognition`).

### Step 2: Set up the project directory
Copy the entire project folder to the new laptop. The folder should contain:
- `main.py`
- `dashboard.py`
- `requirements.txt`
- `students/` (Directory)
- `screenshots/` (Directory)

### Step 3: Install Dependencies
Open a terminal (Command Prompt, PowerShell, or VS Code terminal) in the project folder and run:
```bash
pip install -r requirements.txt
```
*(Note: Installing `face_recognition` might take a few minutes as it compiles `dlib` locally on Windows. Make sure CMake is installed if it throws errors).*

### Step 4: Add Student Data
Inside the `students` folder, place an image of the candidate. 
- Example: `John.jpg` or `Gayatri.png`.
- The system will use this image to verify the person on camera.

### Step 5: Run the Proctoring Engine (Camera)
In your terminal, execute:
```bash
python main.py
```
This will open the webcam and start monitoring. The system will start analyzing face orientation, presence, and multiple people. To close the camera, click the camera window and press the **ESC** key.

### Step 6: Run the Live Dashboard
Open a **new** terminal window (keep `main.py` running in the first one) and execute:
```bash
streamlit run dashboard.py
```
This will automatically open a beautiful dashboard in your web browser where you can see the live Suspicion Score, logs, and screenshots of any cheating attempts!
