import uvicorn
import time
import numpy as np
import os
import re
from fastapi import FastAPI, Request
from funasr_onnx import SenseVoiceSmall

app = FastAPI()

MODEL_PATH = "sensevoice-small"
DEFAULT_USE_ITN = True
TAG_PATTERN = re.compile(r"<\|.*?\|>")

print("🚀 [1/3] 正在加载模型...")

# --- 修改：只计算 model.onnx 的大小 ---
abs_path = os.path.abspath(MODEL_PATH)
onnx_file_path = os.path.join(MODEL_PATH, "model.onnx")

if os.path.exists(MODEL_PATH):
    print(f"   📂 模型目录: {abs_path}")
    
    if os.path.exists(onnx_file_path):
        size_mb = os.path.getsize(onnx_file_path) / (1024 * 1024)
        print(f"   📦 核心模型 (model.onnx): {size_mb:.2f} MB")
    else:
        # 如果找不到 model.onnx，可能是量化版 model_quant.onnx
        quant_path = os.path.join(MODEL_PATH, "model_quant.onnx")
        if os.path.exists(quant_path):
            size_mb = os.path.getsize(quant_path) / (1024 * 1024)
            print(f"   📦 核心模型 (model_quant.onnx): {size_mb:.2f} MB")
        else:
            print("   ⚠️ 未找到 .onnx 模型文件")
else:
    print(f"   ⚠️ 警告: 目录 {abs_path} 不存在")
# ------------------------------------

# 加载模型
model = SenseVoiceSmall(model_dir=MODEL_PATH, quantize=False, intra_op_num_threads=1)

print("🔥 [2/3] 预热模型...")
dummy = np.zeros(16000, dtype=np.float32)
warmup_textnorm = "withitn" if DEFAULT_USE_ITN else "woitn"
model(dummy, language="auto", textnorm=warmup_textnorm)
print("✅ [3/3] 服务就绪 (Port: 8008)")


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def pick_textnorm(request: Request) -> str:
    textnorm = request.query_params.get("textnorm", "").strip().lower()
    if textnorm in {"withitn", "woitn"}:
        return textnorm
    use_itn_raw = request.query_params.get("use_itn")
    if use_itn_raw is not None:
        return "withitn" if str_to_bool(use_itn_raw) else "woitn"
    return "withitn" if DEFAULT_USE_ITN else "woitn"


def clean_text(text: str) -> str:
    return TAG_PATTERN.sub("", text).strip()

@app.post("/transcribe_stream")
async def transcribe_stream(request: Request):
    try:
        body_bytes = await request.body()
        if not body_bytes or len(body_bytes) < 100:
            return {"text": "", "latency_ms": 0}

        t_start = time.time()

        # 转换数据
        audio_int16 = np.frombuffer(body_bytes, dtype=np.int16)
        audio_float32 = audio_int16.astype(np.float32) / 32768.0
        
        # 计算音频物理时长 (秒)
        audio_duration = len(audio_float32) / 16000.0

        # 推理
        textnorm = pick_textnorm(request)
        res = model(audio_float32, language="auto", textnorm=textnorm)
        
        t_end = time.time()
        inference_time = t_end - t_start
        
        # 结果处理
        text = res[0] if isinstance(res, list) else str(res)
        text = clean_text(text)
        
        return {
            "text": text,
            "textnorm": textnorm,
            "latency_ms": int(inference_time * 1000),
            "audio_duration": audio_duration,
            "rtf": round(inference_time / audio_duration, 4) if audio_duration > 0 else 0
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008, log_level="error")
