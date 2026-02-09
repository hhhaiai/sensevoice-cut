import os
import time
import numpy as np
import soundfile as sf
from funasr_onnx import SenseVoiceSmall

# --- 配置部分 ---
MODEL_PATH = "sensevoice-small"
TEST_AUDIO_FILE = "test_audio.wav" 

def generate_dummy_audio(filename):
    if not os.path.exists(filename):
        print(f"ℹ️ 生成测试音频...")
        samplerate = 16000
        # 生成 3秒 的静音
        data = np.zeros(samplerate * 3) 
        sf.write(filename, data, samplerate)

def main():
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 找不到模型路径: {MODEL_PATH}")
        return

    generate_dummy_audio(TEST_AUDIO_FILE)

    print(f"🚀 开始性能测试 (Intel CPU)...")
    print("-" * 40)

    # --- 阶段 1: 模型加载耗时 ---
    t_start_load = time.time()
    
    # 关键优化点：intra_op_num_threads
    # 对于 Intel Mac，通常设置为 4 或 1 甚至比 8 更快，因为减少了线程切换开销
    # 你可以尝试修改这个数字 (1, 4, 8) 看看哪个最快
    model = SenseVoiceSmall(model_dir=MODEL_PATH, quantize=False, intra_op_num_threads=4)
    
    t_end_load = time.time()
    load_time = t_end_load - t_start_load
    print(f"📦 模型加载耗时: {load_time:.4f} 秒 (这是输入法启动时的耗时，仅需一次)")

    # --- 阶段 2: 预热 (Warm-up) ---
    # ONNX Runtime 第一次运行需要构建计算图，通常较慢
    print("🔥 正在预热模型 (第一次推理)...")
    model(TEST_AUDIO_FILE, language="auto", use_itn=True)
    
    # --- 阶段 3: 真实推理速度测试 ---
    print(f"⚡️ 开始正式推理测试 (模拟输入法连续识别)...")
    
    # 循环跑 5 次取平均值
    times = []
    for i in range(5):
        t_start = time.time()
        res = model(TEST_AUDIO_FILE, language="auto", use_itn=True)
        t_end = time.time()
        cost = t_end - t_start
        times.append(cost)
        print(f"   第 {i+1} 次耗时: {cost:.4f} 秒")

    avg_time = sum(times) / len(times)
    
    print("-" * 40)
    print(f"📝 识别结果: {res}")
    print("-" * 40)
    print(f"📊 最终性能统计:")
    print(f"   平均推理耗时: {avg_time:.4f} 秒")
    print(f"   实时率 (RTF): {avg_time / 3.0:.4f} (越小越快，<1 表示比说话快)")
    
    if avg_time < 0.2:
        print("✅ 结论: 速度达标！已达到毫秒级响应。")
    else:
        print("⚠️ 结论: 仍有延迟，请尝试调整线程数。")

if __name__ == "__main__":
    main()
