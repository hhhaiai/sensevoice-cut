import uvicorn
import time
import io
import soundfile as sf
import numpy as np
from fastapi import FastAPI, UploadFile, File
from funasr_onnx import SenseVoiceSmall

app = FastAPI()

# --- 配置 ---
MODEL_PATH = "sensevoice-small"

print("🚀 正在加载模型...")
# 单线程通常延迟最低
model = SenseVoiceSmall(model_dir=MODEL_PATH, quantize=False, intra_op_num_threads=1)

print("🔥 正在预热...")
dummy = np.zeros(16000, dtype=np.float32)
model(dummy, language="auto", use_itn=False)
print("✅ 服务就绪 (文件模式)")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        t_start = time.time()
        
        # 1. 直接读取文件内容到内存 (不存硬盘)
        content = await file.read()
        
        # 2. 在内存中解码音频 (如果是 wav/mp3 等格式)
        # sf.read 支持传入 BytesIO
        audio_data, sample_rate = sf.read(io.BytesIO(content))
        
        # 3. 推理
        res = model(audio_data, language="auto", use_itn=False)
        
        t_end = time.time()
        
        return {
            "text": res[0],
            "time_cost": f"{(t_end - t_start) * 1000:.2f} ms"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8008)
