import pyaudio
import wave
import os

# 配置
FILENAME = "test_audio.wav"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5  # 录 5 秒

def main():
    # 如果旧文件存在，先删除
    if os.path.exists(FILENAME):
        os.remove(FILENAME)

    p = pyaudio.PyAudio()

    print("---------------------------------------")
    print(f"🎙️  准备录音... (请说话 {RECORD_SECONDS} 秒)")
    print("---------------------------------------")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("🛑 录音结束，正在保存...")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"✅ 生成成功: {FILENAME} (标准 WAV 格式)")

if __name__ == "__main__":
    main()
