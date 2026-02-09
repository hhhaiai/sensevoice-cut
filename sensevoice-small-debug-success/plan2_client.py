import requests
import os
import time

url = "http://127.0.0.1:8008/transcribe"
file_path = "test_audio.wav"

if not os.path.exists(file_path):
    print(f"❌ 找不到文件: {file_path}")
    exit()

print(f"🚀 正在发送: {file_path}")

try:
    t0 = time.time()
    
    # 普通文件上传
    with open(file_path, "rb") as f:
        response = requests.post(url, files={"file": f})
    
    t1 = time.time()
    
    if response.status_code == 200:
        data = response.json()
        print("-" * 30)
        print(f"📝 结果: {data.get('text')}")
        print(f"⚡ 服务端耗时: {data.get('time_cost')}")
        print(f"🌐 总耗时: {(t1-t0)*1000:.2f} ms")
        print("-" * 30)
    else:
        print("❌ 失败:", response.text)

except Exception as e:
    print(f"❌ 错误: {e}")
