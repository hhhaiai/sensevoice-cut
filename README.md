# SenseVoice High-Performance Local API

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![SenseVoice](https://img.shields.io/badge/Model-SenseVoiceSmall-green)](https://github.com/FunAudioLLM/SenseVoice)
[![Performance](https://img.shields.io/badge/Latency-Milliseconds-red)](https://github.com/FunAudioLLM/SenseVoice)

这是一个基于 **SenseVoiceSmall** 的高性能本地语音识别系统。

本项目的核心目标是 **极致的响应速度**。通过移除所有不必要的磁盘 I/O，采用 **Raw PCM 内存流（Memory-to-Memory）** 传输技术，实现了**毫秒级**的语音转文字响应。

## ✨ 核心特性

*   **🚀 极速流式识别 (Plan 3)**
    *   全链路内存操作：客户端录音 -> 内存 PCM 流 -> 网络 -> 服务端内存 -> 推理。
    *   全程无文件读写，延迟极低，适用于实时交互场景。
*   **📂 标准文件识别 (Plan 2)**
    *   兼容传统架构，支持标准 WAV 文件上传识别（Multipart Upload）。
*   **📊 性能可视化**
    *   客户端内置实时性能仪表盘，显示 RTF (实时率)、系统吞吐量和延迟统计。
*   **🛠 工程化配套**
    *   提供模型大文件切割/合并脚本，完美解决 GitHub 100MB 文件限制，开箱即用。

---

## 🛠 安装与配置

### 1. 环境依赖

请确保 Python 版本 ≥ 3.8。

**系统级依赖 (PyAudio 驱动):**
*   **MacOS**: `brew install portaudio`
*   **Ubuntu/Debian**: `sudo apt-get install portaudio19-dev`
*   **Windows**: 通常无需额外操作，如报错请安装对应的 `.whl` 包。

**Python 依赖:**
```bash
pip install -r requirements.txt
```

### 2. 模型准备 (⚠️ 重要)

由于 GitHub 限制单文件大小，模型文件 (`model.onnx`) 被切割为多个 `.part` 文件。**在运行代码前，必须执行合并操作：**

```bash
# 1. 赋予脚本执行权限
chmod +x auto_merge.sh

# 2. 运行合并脚本 (自动扫描并还原模型)
./auto_merge.sh
```

**检查点**：确保你的目录结构如下所示，且 `model.onnx` 大小 > 400MB：
```text
.
├── sensevoice-small/      # 模型目录
│   ├── model.onnx         # 核心模型 (必须存在)
│   ├── config.yaml
│   └── ...
├── plan3_server_fast.py
└── ...
```

---

## 🚀 运行指南

### 准备工作：录制测试音频
如果你没有麦克风，或想进行标准化测试，请先生成测试音频：
```bash
python setup1_tools_revord_wav.py
# 按提示录音，程序将生成 'test_audio.wav'
```

### 🌟 模式 A：极速流式识别 (推荐)
> **适用场景**：实时语音输入法、语音助手、对延迟极其敏感的应用。
> **原理**：Raw PCM Bytes 直传，服务端启动即预热，单线程优化。

1.  **启动服务端**:
    ```bash
    python plan3_server_fast.py
    # 等待控制台显示 "✅ [3/3] 服务就绪"
    ```

2.  **启动客户端 (支持麦克风)**:
    ```bash
    python plan3_client_fast.py
    ```
    *   **交互方式**：按 `Enter` 开始录音，再次按 `Enter` 停止并立即识别。
    *   **观察指标**：留意控制台输出的 `RTF` 和 `系统耗时`。

### 📁 模式 B：标准文件上传
> **适用场景**：处理现有的录音文件、Web 后台上传接口集成。

1.  **启动服务端**:
    ```bash
    python plan2_server.py
    ```

2.  **运行客户端**:
    ```bash
    python plan2_client.py
    # 自动上传目录下的 'test_audio.wav' 并显示结果
    ```

### 🧪 模式 C：本地基准测试
不经过网络传输，直接测试本机 CPU/GPU 的推理极限性能。

```bash
# 单次测试
python run_one_test.py

# 循环压力测试 (计算平均耗时)
python fun2_more_tests.py
```

---

## 📊 性能指标说明

在 `plan3_client_fast.py` 的输出中，关注以下核心指标：

| 指标 | 说明 | 性能基准 |
| :--- | :--- | :--- |
| **RTF (Real Time Factor)** | `处理耗时 / 音频时长` | **< 0.1**: 极快 (1s 处理 10s 音频)<br>**< 0.3**: 流畅<br>**> 1.0**: 卡顿 (慢于实时) |
| **系统耗时** | 服务端推理 + 网络传输的总时间 | 越低越好 |
| **吞吐量** | 每分钟识别字数 (CPM) | 越高越好 |

---

## 📂 项目文件清单

| 文件名 | 类型 | 描述 |
| :--- | :--- | :--- |
| **`plan3_server_fast.py`** | 🔥 核心服务 | **极速版服务端**。支持 PCM 流，单线程优化，启动预热。 |
| **`plan3_client_fast.py`** | 🔥 核心客户 | **交互式客户端**。支持麦克风录音、线程安全、性能量化统计。 |
| `plan2_server.py` | 标准服务 | 基于 Multipart Upload 的传统文件上传接口。 |
| `plan2_client.py` | 标准客户 | 演示如何上传本地 `.wav` 文件。 |
| `run_one_test.py` | 测试脚本 | 简单的单次推理测试脚本。 |
| `fun2_more_tests.py` | 测试脚本 | 循环多次推理，计算平均耗时。 |
| `setup1_tools_revord_wav.py`| 工具 | 调用 PyAudio 录制一段真实的 WAV 音频用于测试。 |
| `auto_split.sh` | 运维脚本 | 将大模型文件切割为小分片 (用于提交 GitHub)。 |
| `auto_merge.sh` | 运维脚本 | 将分片文件合并还原 (用于拉取代码后恢复)。 |