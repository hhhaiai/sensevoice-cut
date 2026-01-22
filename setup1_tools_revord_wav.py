import pyaudio
import wave

# 配置
FILENAME = "test_audio.wav"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def record_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("🎙️  按住回车开始录音，松开回车不会停... 哎呀命令行做不到按住。")
    print(f"🎙️  正在录音 (5秒后自动停止)... 请说话！")
    
    frames = []
    for _ in range(0, int(RATE / CHUNK * 5)):
        data = stream.read(CHUNK)
        frames.append(data)
        
    print("🛑 录音结束")
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    with wave.open(FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f"✅ 已保存真实语音到: {FILENAME}")

if __name__ == "__main__":
    record_audio()
