import bpy
import socket
import json
import threading

# 設定 UDP 通訊
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# 創建 UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"UDP 接收器已啟動在端口 {UDP_PORT}")

def receive_data():
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = json.loads(data.decode())
            
            if "distance" in message:
                distance = message["distance"]
                # 控制模型
                if "Cube" in bpy.data.objects:
                    # 將距離值映射到縮放
                    scale = 1.0 + (distance * 2)
                    bpy.data.objects["Cube"].scale = (scale, scale, scale)
        except:
            pass

# 創建並啟動接收線程
receive_thread = threading.Thread(target=receive_data, daemon=True)
receive_thread.start()

# 註冊更新計時器
def update_view():
    bpy.context.view_layer.update()
    return 0.1

bpy.app.timers.register(update_view) 