# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **SenseVoice-Small ONNX speech recognition project** focused on building a **real-time AI voice input method** for macOS. The project implements low-latency audio transcription using the SenseVoiceSmall model from FunASR, optimized for local deployment with ONNX Runtime.

## Architecture

### Core Components

**1. Model Layer (`sensevoice-small/`, `SenseVoiceSmall-onnx/`)**
- Contains the SenseVoiceSmall ONNX models (quantized and full versions)
- Model files are ~240MB (quantized) and ~937MB (full)
- Uses `funasr_onnx` library for inference
- Configuration in `config.yaml` defines model architecture (50 blocks, 4 attention heads, 512 output size)

**2. Server Layer (FastAPI-based)**
- `plan2_server.py`: File upload mode - accepts audio files via HTTP POST
- `plan3_server_fast.py`: Streaming mode - accepts raw PCM audio bytes for lower latency
- Both use `uvicorn` for ASGI server
- Key optimization: `intra_op_num_threads=1` for minimal thread switching overhead

**3. Client Layer**
- `plan2_client.py`: Simple file upload client for testing
- `plan3_client_fast.py`: Real-time microphone streaming client with PyAudio
- Features real-time metrics: RTF (Real-Time Factor), latency, throughput

**4. Utility Scripts**
- `setup1_tools_revord_wav.py`: 5-second audio recorder for creating test files
- `run_one_test.py`: Basic model loading and inference test
- `fun2_more_tests.py`: Performance benchmarking (50 iterations)
- `plan1_changzhu.py`: Performance testing with 50 iterations

### Data Flow

```
Microphone (PyAudio) → Raw PCM bytes → HTTP Stream → FastAPI Server →
SenseVoiceSmall (ONNX) → Text Result → JSON Response → Client Display
```

## Key Optimization Strategies

### Performance Tuning
- **Thread Count**: `intra_op_num_threads=1` (Intel Mac) - reduces thread switching overhead
- **ITN Disabled**: `use_itn=False` - disables inverse text normalization for speed
- **Quantized Models**: Use `model_quant.onnx` (~240MB) instead of full model for faster loading
- **Warm-up**: Pre-run dummy inference to build computation graph

### Latency Targets
- Target: < 100ms inference time for real-time feel
- RTF (Real-Time Factor): < 1.0 means faster than real-time speech
- Current performance: ~50-100ms for 3-second audio clips

## Development Commands

### Testing the Model
```bash
# Basic model test (creates dummy audio if needed)
python run_one_test.py

# Performance benchmarking (50 iterations)
python fun2_more_tests.py

# Quick performance test (5 iterations)
python plan1_changzhu.py
```

### Running Servers
```bash
# File upload mode (port 8008)
python plan2_server.py

# Streaming mode (port 8008) - lower latency
python plan3_server_fast.py
```

### Running Clients
```bash
# File upload client
python plan2_client.py

# Real-time microphone streaming client
python plan3_client_fast.py
```

### Recording Audio
```bash
# Record 5-second test audio
python setup1_tools_revord_wav.py
```

## Dependencies

### Core Requirements
- `funasr_onnx`: FunASR ONNX runtime wrapper
- `onnxruntime`: ONNX inference engine (CPU or GPU)
- `fastapi`: Web framework for server
- `uvicorn`: ASGI server
- `pyaudio`: Microphone access
- `soundfile`: Audio file I/O
- `requests`: HTTP client
- `numpy`: Numerical operations

### Installation
```bash
# CPU version (recommended for development)
pip install funasr_onnx onnxruntime soundfile fastapi uvicorn pyaudio requests numpy

# GPU version (if available)
pip install funasr_onnx onnxruntime-gpu soundfile fastapi uvicorn pyaudio requests numpy
```

## Model Configuration

### SenseVoiceSmall Architecture
- **Encoder**: SenseVoiceEncoderSmall (50 blocks, 4 attention heads)
- **Output Size**: 512
- **Linear Units**: 2048
- **Input Layer**: PE (Positional Encoding)
- **Frontend**: WavFrontend (16kHz, 80 mel filters)
- **Languages Supported**: zh, ja, Yue, en, ko (auto-detection)

### Key Parameters
- `quantize=False`: Already using quantized ONNX models
- `intra_op_num_threads=1`: Optimal for Intel Mac
- `language="auto"`: Automatic language detection
- `use_itn=False`: Disable inverse text normalization for speed

## File Structure

```
sensevoice-cut/
├── sensevoice-small/          # Full model (937MB) + quantized (240MB)
│   ├── model_full.onnx
│   ├── model_quant.onnx
│   ├── config.yaml
│   └── tokens.json
├── SenseVoiceSmall-onnx/      # Official ONNX export (240MB quantized)
│   ├── model_quant.onnx
│   ├── config.yaml
│   └── README.md
├── shandianshuo-config/       # App configuration for "Shandianshuo" app
│   ├── config.json
│   └── models/
├── plan2_server.py            # File upload server (FastAPI)
├── plan2_client.py            # File upload client
├── plan3_server_fast.py       # Streaming server (FastAPI)
├── plan3_client_fast.py       # Real-time microphone client
├── plan1_changzhu.py          # Performance benchmark (50 iterations)
├── fun2_more_tests.py         # Performance benchmark (5 iterations)
├── run_one_test.py            # Basic model test
├── setup1_tools_revord_wav.py # 5-second audio recorder
├── test_audio.wav             # Test audio file (33MB)
└── auto_split.sh / auto_merge.sh # Script utilities
```

## Testing Strategy

### Quick Validation
1. Run `python run_one_test.py` - verifies model loads and basic inference works
2. Record real audio with `setup1_tools_revord_wav.py`
3. Test server/client with `plan2_server.py` + `plan2_client.py`

### Performance Testing
1. `python fun2_more_tests.py` - benchmarks 50 iterations
2. `python plan3_client_fast.py` - real-world streaming test with metrics
3. Monitor: RTF, latency_ms, audio_duration, throughput

### Expected Performance
- Model load time: ~2-5 seconds (first time)
- Inference time: 50-150ms for 3-second audio
- RTF: 0.02-0.05 (20-50x faster than real-time)

## Common Issues & Solutions

### Slow Performance
- **Issue**: High latency (>200ms)
- **Solution**: Try `intra_op_num_threads=1` or `=4`, disable ITN (`use_itn=False`)

### Model Loading Fails
- **Issue**: Missing config files
- **Solution**: Ensure `config.yaml`, `tokens.json`, `*.mvn` files are in model directory

### Audio Issues
- **Issue**: PyAudio permission errors on macOS
- **Solution**: Grant microphone access in System Preferences → Security → Microphone

### Memory Issues
- **Issue**: Out of memory with full model
- **Solution**: Use `model_quant.onnx` (240MB) instead of `model_full.onnx` (937MB)

## Integration Notes

This project appears to be part of a larger "Shandianshuo" (闪电说) application, which is a Chinese voice input method. The `shandianshuo-config/` directory contains app configuration and model paths for the main application.

The SenseVoiceSmall model is specifically designed for:
- Multi-language speech recognition (Chinese, Japanese, Cantonese, English, Korean)
- Real-time punctuation prediction
- Disfluency detection
- Industrial-grade accuracy (trained on 33M+ samples)