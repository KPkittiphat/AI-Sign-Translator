import sys
sys.stdout.reconfigure(encoding='utf-8')
import cv2
import os
import csv
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. ดาวน์โหลดโมเดล Hand Landmarker แบบใหม่ถ้ายังไม่มี
model_path = 'hand_landmarker.task'
if not os.path.exists(model_path):
    print("[INFO] Downloading Hand Landmarker model...")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, model_path)
    print("[INFO] Download completed.")

# 2. ตั้งค่า MediaPipe Hands (ใช้ Tasks API)
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5)

detector = vision.HandLandmarker.create_from_options(options)

# 3. พาธโฟลเดอร์ (ต้องสร้างโฟลเดอร์ชื่อ my_sign_dataset ไว้ที่เดียวกับไฟล์นี้)
GIF_FOLDER = './my_sign_dataset' 
OUTPUT_CSV = 'sign_language_dataset.csv'

label_map = {}
label_counter = 0

print("[INFO] Starting feature extraction from GIF dataset...")

with open(OUTPUT_CSV, mode='w', newline='') as f:
    writer = csv.writer(f)

    # วนลูปอ่านทุกไฟล์ในโฟลเดอร์
    for filename in os.listdir(GIF_FOLDER):
        if filename.endswith('.gif'):
            # ตัดเอาเฉพาะคำศัพท์ข้างหน้าเครื่องหมาย _
            word = filename.split('_')[0]
            
            # ลงทะเบียนจับคู่คำศัพท์กับตัวเลข Label
            if word not in label_map:
                label_map[word] = label_counter
                label_counter += 1
            
            current_label = label_map[word]
            gif_path = os.path.join(GIF_FOLDER, filename)
            
            # ใช้ OpenCV เปิดอ่านไฟล์ GIF
            cap = cv2.VideoCapture(gif_path)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break  # อ่านจนหมดเฟรมใน GIF ให้ข้ามไปไฟล์ถัดไป
                
                # แปลงสีภาพให้ตรงกับที่ MediaPipe ต้องการ
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
                
                # ตรวจจับด้วย Tasks API แบบใหม่
                detection_result = detector.detect(mp_image)
                
                # ถ้าเฟรมนี้ตรวจเจอข้อนิ้วมือ
                if detection_result.hand_landmarks:
                    left_hand = [0.0] * 63
                    right_hand = [0.0] * 63
                    
                    for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                        # ดึงประเภทของมือ (Left หรือ Right)
                        handedness = detection_result.handedness[idx][0].category_name
                        
                        # ใช้พิกัดสัมพัทธ์ (Relative Coordinates) โดยลบกับตำแหน่งข้อมือ (จุดที่ 0)
                        wrist = hand_landmarks[0]
                        coords = []
                        for lm in hand_landmarks:
                            coords.extend([lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z])
                            
                        # นำไปใส่ถูกข้าง
                        if handedness == 'Left':
                            left_hand = coords
                        elif handedness == 'Right':
                            right_hand = coords
                            
                    # เขียนลง CSV: [พิกัดมือซ้าย 63 ตัว] + [พิกัดมือขวา 63 ตัว] + [ตัวเลข Label] รวมเป็น 126+1 คอลัมน์
                    writer.writerow(left_hand + right_hand + [current_label])

print(f"\n[SUCCESS] Dataset generated successfully: {OUTPUT_CSV}")
print("[INFO] Class Dictionary Mapping:")
for word, label_id in label_map.items():
    print(f"   - {word} : Class ID {label_id}")