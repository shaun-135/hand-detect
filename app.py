import cv2
import mediapipe as mp
import socket
import json
import signal
import sys

# 全域變數
is_running = True
sock = None
cap = None

def signal_handler(signum, frame):
    global is_running
    print("\n收到關閉信號，正在清理...")
    is_running = False

def cleanup():
    global sock, cap
    if cap:
        cap.release()
        print("已釋放攝影機")
    if sock:
        sock.close()
        print("已關閉 socket")
    cv2.destroyAllWindows()
    print("清理完成")

# 註冊信號處理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 設定 UDP 通訊
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# 創建 UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允許端口重用

# 初始化 MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# 初始化攝影機
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("無法開啟攝影機")
    cleanup()
    sys.exit(1)

# 創建手部追蹤器
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

try:
    while is_running and cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 處理影像
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 繪製手部標記點
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # 計算手指間距
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
                
                # 發送數據到 Blender
                data = {"distance": distance}
                sock.sendto(json.dumps(data).encode(), (UDP_IP, UDP_PORT))

        # 顯示影像
        cv2.imshow("Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    cleanup()
