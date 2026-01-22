---
tasks:
- auto-speech-recognition
domain:
- audio
model-type:
- Classification
frameworks:
- onnx
metrics:
- f1_score
license: Apache License 2.0
language: 
- cn
tags:
- FunASR
- CT-Transformer
- Alibaba
- ICASSP 2020
datasets:
  train:
  - 33M-samples online data
  test:
  - wikipedia data test
  - 10000 industrial Mandarin sentences test
widgets:
  - task: punctuation
    inputs:
      - type: text
        name: input
        title: 文本
    examples:
      - name: 1
        title: 示例1
        inputs:
          - name: input
            data: 我们都是木头人不会讲话不会动
    inferencespec:
      cpu: 1 #CPU数量
      memory: 4096
---

# 模型介绍

## Highlights
模型为[SenseVoice多语言语音理解模型Small](https://www.modelscope.cn/models/iic/SenseVoiceSmall)的onnx量化导出版本，可以直接用来做生产部署，一键部署教程（[点击此处](https://github.com/alibaba-damo-academy/FunASR/blob/main/runtime/readme_cn.md)


## <strong>[ModelScope-FunASR](https://github.com/alibaba-damo-academy/FunASR)</strong>
<strong>[FunASR](https://github.com/alibaba-damo-academy/FunASR)</strong>提供可便捷本地或者云端服务器部署的离线文件转写服务，内核为FunASR已开源runtime-SDK。 集成了达摩院语音实验室在Modelscope社区开源的语音端点检测(VAD)、Paraformer-large语音识别(ASR)、标点恢复(PUNC) 等相关能力，拥有完整的语音识别链路，可以将几十个小时的音频或视频识别成带标点的文字，而且支持上百路请求同时进行转写。

[**最新动态**](https://github.com/alibaba-damo-academy/FunASR#whats-new) 
| [**环境安装**](https://github.com/alibaba-damo-academy/FunASR#installation)
| [**介绍文档**](https://alibaba-damo-academy.github.io/FunASR/en/index.html)
| [**服务部署**](https://github.com/alibaba-damo-academy/FunASR/blob/main/runtime/readme_cn.md)
| [**模型库**](https://github.com/alibaba-damo-academy/FunASR/blob/main/docs/model_zoo/modelscope_models.md)
| [**联系我们**](https://github.com/alibaba-damo-academy/FunASR#contact)

## 快速上手
### docker安装
如果您已安装docker，忽略本步骤！!
通过下述命令在服务器上安装docker：
```shell
curl -O https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ASR/shell/install_docker.sh；
sudo bash install_docker.sh
```
docker安装失败请参考 [Docker Installation](https://alibaba-damo-academy.github.io/FunASR/en/installation/docker.html)

### 镜像启动
通过下述命令拉取并启动FunASR runtime的docker镜像（[获取最新镜像版本](https://github.com/alibaba-damo-academy/FunASR/blob/main/runtime/docs/SDK_advanced_guide_offline_zh.md)）：

```shell
sudo docker pull \
  registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-cpu-0.4.6
mkdir -p ./funasr-runtime-resources/models
sudo docker run -p 10095:10095 -it --privileged=true \
  -v $PWD/funasr-runtime-resources/models:/workspace/models \
  registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-cpu-0.4.6
```

### 服务端启动

docker启动之后，启动 funasr-wss-server服务程序：
```shell
cd FunASR/runtime
nohup bash run_server.sh \
  --download-model-dir /workspace/models \
  --vad-dir damo/speech_fsmn_vad_zh-cn-16k-common-onnx \
  --model-dir damo/SenseVoiceSmall-onnx  \
  --punc-dir damo/punc_ct-transformer_cn-en-common-vocab471067-large-onnx \
  --lm-dir damo/speech_ngram_lm_zh-cn-ai-wesp-fst \
  --itn-dir thuduj12/fst_itn_zh \
  --hotword /workspace/models/hotwords.txt > log.out 2>&1 &
```

### 客户端测试与使用

运行上面安装指令后，会在./funasr-runtime-resources（默认安装目录）中下载客户端测试工具目录samples（[下载点击此处](https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ASR/sample/funasr_samples.tar.gz)），
我们以Python语言客户端为例，进行说明，支持多种音频格式输入（.wav, .pcm, .mp3等），也支持视频输入(.mp4等)，以及多文件列表wav.scp输入，其他版本客户端请参考文档（[点击此处](https://alibaba-damo-academy.github.io/FunASR/en/runtime/docs/SDK_tutorial_zh.html#id5)）

```shell
python3 wss_client_asr.py --host "127.0.0.1" --port 10095 --mode offline --audio_in "../audio/asr_example.wav"
```

更详细用法介绍（[点击此处](https://github.com/alibaba-damo-academy/FunASR/blob/main/runtime/docs/SDK_tutorial_zh.md)）


## 相关论文以及引用信息

```BibTeX
@inproceedings{chen2020controllable,
  title={Controllable Time-Delay Transformer for Real-Time Punctuation Prediction and Disfluency Detection},
  author={Chen, Qian and Chen, Mengzhe and Li, Bo and Wang, Wen},
  booktitle={ICASSP 2020-2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  pages={8069--8073},
  year={2020},
  organization={IEEE}
}
```

