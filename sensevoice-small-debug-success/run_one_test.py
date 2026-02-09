"""
# 如果你有NVIDIA显卡，安装 onnxruntime-gpu，否则安装 onnxruntime
pip install funasr_onnx onnxruntime-gpu  
# 或者 CPU 版本：

pip install funasr_onnx onnxruntime soundfile

"""

import os
import numpy as np
import soundfile as sf
from funasr_onnx import SenseVoiceSmall

# --- 配置部分 ---
# 你的模型绝对路径
MODEL_PATH = "sensevoice-small"
# 测试音频文件名
TEST_AUDIO_FILE = "test_audio.wav" 

def generate_dummy_audio(filename):
    """
    如果没有音频文件，生成一个静音的wav文件用于测试模型是否能跑通。
    如果有真实音频，请手动替换该文件。
    """
    if not os.path.exists(filename):
        print(f"⚠️ 未找到 {filename}，正在生成一段 3秒 的静音测试音频...")
        # 生成 3秒 的静音 (采样率 16000)
        samplerate = 16000
        data = np.zeros(samplerate * 3) 
        sf.write(filename, data, samplerate)
        print("✅ 测试音频已生成。注意：因为是静音，识别结果可能为空或乱码，但能证明模型加载成功。")

def main():
    # 1. 检查模型路径是否存在
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 错误：找不到模型路径: {MODEL_PATH}")
        return

    print(f"🚀 正在加载模型 (Intel CPU 模式)...")
    print(f"   内存充足 (64GB)，加载中...")

    try:
        # 初始化模型
        # quantize=False: 你的模型已经是onnx了，不需要再量化
        # intra_op_num_threads=4: 设置CPU线程数，Intel Mac上设置4-8比较合适
        model = SenseVoiceSmall(model_dir=MODEL_PATH, quantize=False, intra_op_num_threads=8)
        print("✅ 模型加载成功！")
    except Exception as e:
        print(f"❌ 模型加载失败。可能是缺少某些配置文件。\n错误信息: {e}")
        return

    # 2. 准备音频
    generate_dummy_audio(TEST_AUDIO_FILE)

    # 3. 执行推理
    print(f"🎤 正在识别音频: {TEST_AUDIO_FILE} ...")
    try:
        # language="auto" 自动识别语言
        # use_itn=True 开启逆文本标准化 (例如 "一百" -> "100")
        res = model(TEST_AUDIO_FILE, language="auto", use_itn=True)
        
        print("\n" + "="*30)
        print("📝 识别结果:")
        print(res)
        print("="*30 + "\n")
        print("🎉 测试通过！你的 Mac 可以完美运行此本地模型。")
        
    except Exception as e:
        print(f"❌ 推理过程中出错: {e}")

if __name__ == "__main__":
    main()
