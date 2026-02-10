import pyaudio
import requests
import time
import threading
import re

# --- 配置 ---
SERVER_URL = "http://127.0.0.1:8008/transcribe_stream"
USE_ITN = True  # 开启 withitn 更容易输出数字/符号格式
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

class SafeAudioRecorder:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.is_recording = False
        self.stream = None
        self.record_thread = None

    def start(self):
        if self.is_recording: return
        self.frames = []
        self.is_recording = True
        self.stream = self.p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                                  input=True, frames_per_buffer=CHUNK)
        self.record_thread = threading.Thread(target=self._record_loop)
        self.record_thread.start()
        print("\n🎙️  正在录音... (再次按回车发送)")

    def _record_loop(self):
        while self.is_recording:
            try:
                if self.stream and self.stream.is_active():
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
            except:
                break

    def stop_and_send(self):
        if not self.is_recording: return
        
        print("🛑 处理中...")
        self.is_recording = False
        if self.record_thread: self.record_thread.join()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self._send_request()

    def _clean_text(self, text):
        """去除 <|zh|> 等特殊标签，只保留纯文本"""
        if not text: return ""
        # 正则替换掉 <|...|> 格式的标签
        cleaned = re.sub(r'<\|.*?\|>', '', text)
        return cleaned.strip()

    def _send_request(self):
        audio_data = b''.join(self.frames)
        if len(audio_data) < 16000 * 0.2: # 忽略小于0.2秒的噪音
            print("⚠️ 录音太短")
            return

        try:
            t0 = time.time()
            resp = requests.post(
                SERVER_URL, 
                data=audio_data,
                params={"use_itn": str(USE_ITN).lower()},
                headers={"Content-Type": "application/octet-stream"}
            )
            t1 = time.time()
            
            if resp.status_code == 200:
                data = resp.json()
                raw_text = data.get('text', '')
                clean_text = self._clean_text(raw_text)
                
                server_ms = data.get('latency_ms', 0)
                audio_dur = data.get('audio_duration', 0.1)
                rtf = data.get('rtf', 0)
                textnorm = data.get('textnorm', 'withitn' if USE_ITN else 'woitn')
                total_ms = (t1 - t0) * 1000
                
                # 计算指标
                char_count = len(clean_text)
                speed_ratio = 1.0 / rtf if rtf > 0 else 0
                
                print("\n" + "="*50)
                print(f"📝 识别内容: {clean_text}")
                print("-" * 50)
                print(f"📊 性能量化指标:")
                print(f"   🧾  文本规范: {textnorm}")
                print(f"   🗣️  语音时长: {audio_dur:.2f} 秒")
                print(f"   ⚡  系统耗时: {server_ms} ms (网络+总耗时: {total_ms:.1f} ms)")
                print(f"   🚀  RTF(实时率): {rtf:.4f} (比说话快 {speed_ratio:.1f} 倍)")
                print(f"   📈  吞吐量: {char_count} 字")
                
                if audio_dur > 0:
                    speaking_speed = (char_count / audio_dur) * 60
                    print(f"   👄  你的语速: {int(speaking_speed)} 字/分钟")
                
                print("="*50 + "\n")
            else:
                print(f"❌ 错误: {resp.text}")
        except Exception as e:
            print(f"❌ 网络错误: {e}")

    def close(self):
        if self.is_recording:
            self.is_recording = False
            if self.record_thread: self.record_thread.join()
        if self.stream: self.stream.close()
        self.p.terminate()

def main():
    recorder = SafeAudioRecorder()
    print("AI 语音输入法 (性能量化版) - 输入 'q' 退出")
    try:
        while True:
            cmd = input(">> ")
            if cmd.lower() == 'q': break
            if not recorder.is_recording: recorder.start()
            else: recorder.stop_and_send()
    except KeyboardInterrupt: pass
    finally: recorder.close()

if __name__ == "__main__":
    main()
