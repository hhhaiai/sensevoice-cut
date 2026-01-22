import requests

# 接口地址
url = "http://127.0.0.1:8008/transcribe"

# 你的测试音频路径
file_path = "test_audio.wav"

print(f"正在发送音频: {file_path} ...")

try:
    # 打开文件并发送 POST 请求
    with open(file_path, "rb") as f:
        # files={'file': ...} 这里的 'file' 必须和服务端参数名一致
        response = requests.post(url, files={"file": f})
    
    # 解析结果
    if response.status_code == 200:
        data = response.json()
        print("-" * 30)
        print(f"识别结果: {data['text']}")
        print(f"服务端耗时: {data['time_cost']}")
        print("-" * 30)
    else:
        print("调用失败:", response.text)

except Exception as e:
    print(f"发生错误: {e}")
