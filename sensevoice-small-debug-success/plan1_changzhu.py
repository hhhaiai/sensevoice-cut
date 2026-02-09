
import os
import time
import numpy as np
import soundfile as sf
from funasr_onnx import SenseVoiceSmall

# --- 配置 ---
MODEL_PATH = "sensevoice-small"
TEST_AUDIO_FILE = "test_audio.wav"

def generate_dummy_audio(filename):
    if not os.path.exists(filename):
        samplerate = 16000
        data = np.zeros(samplerate * 3) 
        sf.write(filename, data, samplerate)

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 找不到模型")
        return

    generate_dummy_audio(TEST_AUDIO_FILE)

    print(f"🚀 正在初始化 (模拟 App 启动)...")
    
    # 1. 加载模型 (只做一次)
    # 优化：intra_op_num_threads=1 (Intel CPU 上的魔法数字，通常比 4 或 8 快)
    model = SenseVoiceSmall(model_dir=MODEL_PATH, quantize=False, intra_op_num_threads=1)
    
    # 2. 预热 (Warmup)
    print("🔥 预热中...")
    model(TEST_AUDIO_FILE, language="auto", use_itn=False)

    print("-" * 40)
    print(f"⚡️ 开始极致性能测试 (循环 50 次)")
    print(f"ℹ️ 优化策略: 单线程 + 关闭 ITN (use_itn=False)")
    print("-" * 40)

    total_time = 0
    loop_count = 50
    
    # 3. 连续推理
    for i in range(loop_count):
        t_start = time.time()
        
        # 核心调用：关闭 ITN
        res = model(TEST_AUDIO_FILE, language="auto", use_itn=False)
        
        t_end = time.time()
        cost = t_end - t_start
        total_time += cost
        
        # 只打印前5次，避免刷屏
        if i < 5:
            print(f"   第 {i+1} 次耗时: {cost:.5f} 秒")

    avg_time = total_time / loop_count
    print("-" * 40)
    print(f"📊 最终结果 (平均值): {avg_time:.5f} 秒")
    print(f"   RTF (实时率): {avg_time/3.0:.4f}")
    
    if avg_time < 0.1:
        print("✅ 恭喜！速度已超越或持平闪电说 (0.1s)。")
    else:
        print("⚠️ 依然不够快？那可能需要 C++ 了。")

if __name__ == "__main__":
    main()
