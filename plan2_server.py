"""
pip install fastapi uvicorn python-multipart

"""

from fastapi import FastAPI, UploadFile, File
from funasr_onnx import SenseVoiceSmall
import uvicorn
import shutil
import os
import time

app = FastAPI()

# 全局加载模型 (常驻内存，就像闪电说一样)
print("正在加载模型...")
MODEL_PATH = "sensevoice-small"
model = SenseVoiceSmall(model_dir=MODEL_PATH, quantize=False, intra_op_num_threads=1)
print("模型加载完毕，服务就绪！")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # 保存临时文件
    temp_filename = f"temp_{int(time.time())}.wav"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 推理
    start = time.time()
    # 这里的 use_itn=False 保证速度
    res = model(temp_filename, language="auto", use_itn=False)
    end = time.time()
    
    # 清理文件
    os.remove(temp_filename)
    
    return {
        "text": res[0],
        "time_cost": f"{end - start:.4f}s"
    }

if __name__ == "__main__":
    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=8008)
