import cv2
import os
import time
import urllib.request
from datetime import datetime
import mediapipe as mp
import numpy as np
import sys

# =========================
# CONFIGURATION
# =========================
STUDENT_IMAGES_DIR = 'students'
SCREENSHOTS_DIR = 'screenshots'
ATTENDANCE_FILE = 'Attendance.csv'
LOG_FILE = 'SuspiciousLog.csv'

# Ensure directories exist
os.makedirs(STUDENT_IMAGES_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def download_model():
    """Downloads the MediaPipe Face Landmarker model if it doesn't exist."""
    model_path = 'face_landmarker.task'
    if not os.path.exists(model_path):
        print("[INFO] Downloading MediaPipe Face Landmarker model (First time only)...")
        url = 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task'
        urllib.request.urlretrieve(url, model_path)
        print("[INFO] Download complete.")
    return model_path

class ProctoringSystem:
    def __init__(self, student_name="Candidate"):
        # Python 3.13 requires MediaPipe Tasks API instead of old solutions API
        self.model_path = download_model()
        BaseOptions = mp.tasks.BaseOptions
        FaceLandmarker = mp.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.IMAGE,
            num_faces=5
        )
        self.face_mesh = FaceLandmarker.create_from_options(options)
        
        self.student_name = student_name
        self.marked_students = set()
        
        self.suspicion_score = 0.0
        self.absence_frames = 0
        self.last_screenshot_time = 0
        self.head_turn_frames = 0
        
        # Initialization
        self._init_csv_files()
        if self.student_name == "Candidate":
            self._load_student_name()

    def _init_csv_files(self):
        """Creates CSV files with headers if they don't exist."""
        if not os.path.exists(ATTENDANCE_FILE):
            with open(ATTENDANCE_FILE, 'w') as f:
                f.write("Name,Time\n")
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as f:
                f.write("Timestamp,Student,Activity,SuspicionScore,ScreenshotFile\n")

    def _load_student_name(self):
        """Loads the student name from the images directory for the demo."""
        if not os.path.exists(STUDENT_IMAGES_DIR):
            print(f"[WARNING] Directory '{STUDENT_IMAGES_DIR}' not found.")
            return

        files = os.listdir(STUDENT_IMAGES_DIR)
        if files:
            self.student_name = os.path.splitext(files[0])[0].upper()
            print(f"[INFO] Student set to: {self.student_name}")
        else:
            print("[INFO] No student images found. Defaulting to 'Candidate'.")

    def mark_attendance(self, name):
        """Logs attendance."""
        if name not in self.marked_students:
            with open(ATTENDANCE_FILE, 'a+') as f:
                dt_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f'{name},{dt_string}\n')
            self.marked_students.add(name)
            print(f"[VERIFIED] {name} attendance marked.")

    def log_suspicious_activity(self, activity, img=None):
        """Logs suspicious events and optionally saves a screenshot."""
        dt_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        screenshot_name = "N/A"
        
        # Save screenshot if image is provided (with a 5-second cooldown)
        if img is not None:
            current_time = time.time()
            if current_time - self.last_screenshot_time > 5:  
                screenshot_name = f"screenshot_{int(current_time)}.jpg"
                filepath = os.path.join(SCREENSHOTS_DIR, screenshot_name)
                cv2.imwrite(filepath, img)
                self.last_screenshot_time = current_time

        with open(LOG_FILE, 'a+') as f:
            f.write(f'{dt_string},{self.student_name},{activity},{int(self.suspicion_score)},{screenshot_name}\n')

    def get_head_pose(self, image, face_landmarks):
        """Calculates Pitch and Yaw to determine where the user is looking."""
        img_h, img_w, _ = image.shape
        face_3d = []
        face_2d = []

        # 3D Model Points (Nose tip, Chin, Left Eye L, Right Eye R, Mouth L, Mouth R)
        landmark_indices = [33, 263, 1, 61, 291, 199]
        for idx, lm in enumerate(face_landmarks):
            if idx in landmark_indices:
                if idx == 1:
                    nose_2d = (int(lm.x * img_w), int(lm.y * img_h))
                x, y = int(lm.x * img_w), int(lm.y * img_h)
                face_2d.append([x, y])
                face_3d.append([x, y, lm.z])
                
        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        # Camera Matrix
        focal_length = 1 * img_w
        cam_matrix = np.array([
            [focal_length, 0, img_h / 2],
            [0, focal_length, img_w / 2],
            [0, 0, 1]
        ])
        distortion_matrix = np.zeros((4, 1), dtype=np.float64)
        
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, distortion_matrix)
        rmat, jac = cv2.Rodrigues(rot_vec)
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

        x = angles[0] * 360 # Pitch (Up/Down)
        y = angles[1] * 360 # Yaw (Left/Right)

        # Determine Direction
        direction = "Forward"
        if y < -10:
            direction = "Looking Left"
        elif y > 10:
            direction = "Looking Right"
        elif x < -10:
            direction = "Looking Down"
        elif x > 15:
            direction = "Looking Up"
            
        return direction, nose_2d

    def run(self):
        """Main loop for capturing video and processing frames."""
        cap = cv2.VideoCapture(0)
        print("[INFO] Starting video stream. Press ESC to exit.")
        self.log_suspicious_activity("Session Started")
        
        while True:
            success, img = cap.read()
            if not success:
                break
                
            # Flip image for a mirror effect
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_h, img_w, _ = img.shape
            
            # ---------------------------------------------------------
            # Process Frame with MediaPipe Tasks API
            # ---------------------------------------------------------
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
            results = self.face_mesh.detect(mp_image)
            
            num_faces = 0
            if results.face_landmarks:
                num_faces = len(results.face_landmarks)
            
            # Decrease suspicion score gradually if student is sitting normally
            if self.suspicion_score > 0 and num_faces == 1 and self.head_turn_frames == 0:
                self.suspicion_score -= 0.05 
                self.suspicion_score = max(0, self.suspicion_score)

            # Check Absence
            if num_faces == 0:
                self.absence_frames += 1
                if self.absence_frames > 30: # Absent for ~1 second
                    cv2.putText(img, "WARNING: CANDIDATE ABSENT!", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    self.suspicion_score += 0.5
                    if self.absence_frames % 30 == 0: # Log periodically
                        self.log_suspicious_activity("Candidate Absent", img)
            else:
                self.absence_frames = 0
            
            # Check Multiple Faces
            if num_faces > 1:
                cv2.putText(img, "WARNING: MULTIPLE FACES DETECTED!", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                self.suspicion_score += 2
                self.log_suspicious_activity("Multiple Faces Detected", img)

            # Process 1 Face (Normal Case)
            if num_faces == 1:
                face_landmarks = results.face_landmarks[0]
                
                # Draw bounding box and name
                x_min = int(min([lm.x for lm in face_landmarks]) * img_w)
                y_min = int(min([lm.y for lm in face_landmarks]) * img_h)
                x_max = int(max([lm.x for lm in face_landmarks]) * img_w)
                y_max = int(max([lm.y for lm in face_landmarks]) * img_h)
                
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                cv2.putText(img, f"Verified: {self.student_name}", (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                self.mark_attendance(self.student_name)

                # Head Pose Estimation
                direction, nose_2d = self.get_head_pose(img, face_landmarks)
                
                if direction in ["Looking Left", "Looking Right"]:
                    self.head_turn_frames += 1
                    cv2.putText(img, f"Head Direction: {direction}", (20, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                else:
                    self.head_turn_frames = max(0, self.head_turn_frames - 2)
                
                # Repeatedly looking left/right logic (approx > 1 second)
                if self.head_turn_frames > 20:
                    self.suspicion_score += 1
                    cv2.putText(img, "WARNING: SUSPICIOUS MOVEMENT!", (20, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    if self.head_turn_frames == 21: # Log only once per sequence
                        self.log_suspicious_activity("Suspicious Head Movement", img)

            # ---------------------------------------------------------
            # UI Overlay
            # ---------------------------------------------------------
            score_color = (0, 255, 0) if self.suspicion_score < 30 else (0, 165, 255) if self.suspicion_score < 70 else (0, 0, 255)
            cv2.putText(img, f"Suspicion Score: {int(self.suspicion_score)}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, score_color, 3)
            
            # Display Window
            cv2.imshow('AI Proctoring System - Engine', img)
            
            # Exit on ESC key
            if cv2.waitKey(1) & 0xFF == 27:
                break
                
        # Cleanup
            self.log_suspicious_activity("Session Ended")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    student_name = sys.argv[1] if len(sys.argv) > 1 else "Candidate"
    system = ProctoringSystem(student_name)
    system.run()
