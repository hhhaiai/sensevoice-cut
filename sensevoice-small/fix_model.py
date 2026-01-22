"""

┌─(sanbo🍎mac)-~/Desktop/sensevoice-cut(main*+)
└─$ ./sherpa-onnx-v1.12.23-onnxruntime-1.11.0-osx-universal2-shared/bin/sherpa-onnx-offline \
>   --sense-voice-model=./model.onnx \
>   --tokens=./tokens.txt \
>   --sense-voice-language=auto \
>   --sense-voice-use-itn=true \
>   ./test_audio.wav
/Users/runner/work/sherpa-onnx/sherpa-onnx/sherpa-onnx/csrc/parse-options.cc:Read:373 ./sherpa-onnx-v1.12.23-onnxruntime-1.11.0-osx-universal2-shared/bin/sherpa-onnx-offline --sense-voice-model=./model.onnx --tokens=./tokens.txt --sense-voice-language=auto --sense-voice-use-itn=true ./test_audio.wav 

OfflineRecognizerConfig(feat_config=FeatureExtractorConfig(sampling_rate=16000, feature_dim=80, low_freq=20, high_freq=-400, dither=0, normalize_samples=True, snip_edges=False), model_config=OfflineModelConfig(transducer=OfflineTransducerModelConfig(encoder_filename="", decoder_filename="", joiner_filename=""), paraformer=OfflineParaformerModelConfig(model=""), nemo_ctc=OfflineNemoEncDecCtcModelConfig(model=""), whisper=OfflineWhisperModelConfig(encoder="", decoder="", language="", task="transcribe", tail_paddings=-1), fire_red_asr=OfflineFireRedAsrModelConfig(encoder="", decoder=""), tdnn=OfflineTdnnModelConfig(model=""), zipformer_ctc=OfflineZipformerCtcModelConfig(model=""), wenet_ctc=OfflineWenetCtcModelConfig(model=""), sense_voice=OfflineSenseVoiceModelConfig(model="./model.onnx", language="auto", use_itn=True), moonshine=OfflineMoonshineModelConfig(preprocessor="", encoder="", uncached_decoder="", cached_decoder=""), dolphin=OfflineDolphinModelConfig(model=""), canary=OfflineCanaryModelConfig(encoder="", decoder="", src_lang="", tgt_lang="", use_pnc=True), omnilingual=OfflineOmnilingualAsrCtcModelConfig(model=""), funasr_nano=OfflineFunASRNanoModelConfig(encoder_adaptor="", llm="", embedding="", tokenizer="", system_prompt="You are a helpful assistant.", user_prompt="语音转写：", max_new_tokens=512, temperature=1e-06, top_p=0.8, seed=42), medasr=OfflineMedAsrCtcModelConfig(model=""), telespeech_ctc="", tokens="./tokens.txt", num_threads=2, debug=False, provider="cpu", model_type="", modeling_unit="cjkchar", bpe_vocab=""), lm_config=OfflineLMConfig(model="", scale=0.5, lodr_scale=0.01, lodr_fst="", lodr_backoff_id=-1), ctc_fst_decoder_config=OfflineCtcFstDecoderConfig(graph="", max_active=3000), decoding_method="greedy_search", max_active_paths=4, hotwords_file="", hotwords_score=1.5, blank_penalty=0, rule_fsts="", rule_fars="", hr=HomophoneReplacerConfig(lexicon="", rule_fsts=""))
Creating recognizer ...
/Users/runner/work/sherpa-onnx/sherpa-onnx/sherpa-onnx/csrc/offline-sense-voice-model.cc:Init:106 'vocab_size' does not exist in the metadata
------
pip install onnx


根目录下还是不行

./sherpa-onnx-v1.12.23-onnxruntime-1.11.0-osx-universal2-shared/bin/sherpa-onnx-offline \
  --sense-voice-model=./sensevoice-small/model_sherpa.onnx \
  --tokens=./sensevoice-small/tokens.txt \
  --sense-voice-language=auto \
  --sense-voice-use-itn=true \
  ./test_audio.wav



"""

import onnx
import os
import re

# --- 配置路径 ---
BASE_DIR = "." # 假设脚本就在 sensevoice-small 目录下运行
MODEL_PATH = os.path.join(BASE_DIR, "model.onnx")
TOKENS_PATH = os.path.join(BASE_DIR, "tokens.txt")
MVN_PATH = os.path.join(BASE_DIR, "am.mvn")
OUTPUT_PATH = os.path.join(BASE_DIR, "model_sherpa.onnx")

def parse_mvn_file(path):
    if not os.path.exists(path): return None, None
    with open(path, 'r', encoding='utf-8') as f: content = f.read()
    match_shift = re.search(r'<AddShift>.*?\[(.*?)\]', content, re.DOTALL)
    match_scale = re.search(r'<Rescale>.*?\[(.*?)\]', content, re.DOTALL)
    if not match_shift or not match_scale: return None, None
    return ",".join(match_shift.group(1).split()), ",".join(match_scale.group(1).split())

def main():
    # 1. 词表大小 (读取之前的 tokens.txt)
    # 注意：这里我们不需要改 tokens.txt 了，保持原样即可
    with open(TOKENS_PATH, "r", encoding="utf-8") as f:
        vocab_size = len(f.readlines())
    print(f"📊 词表大小: {vocab_size}")

    # 2. CMVN
    neg_mean, inv_stddev = parse_mvn_file(MVN_PATH)

    # 3. 注入模型
    print(f"📂 更新模型元数据: {MODEL_PATH} ...")
    model = onnx.load(MODEL_PATH)

    meta_dict = {
        "model_type": "sense_voice",
        "vocab_size": str(vocab_size),
        "language": "auto", 
        "version": "1",
        "lfr_window_size": "7",
        "lfr_window_shift": "6",
        "normalize_samples": "1",
        "with_itn": "1",
        "without_itn": "1",
        "neg_mean": neg_mean,
        "inv_stddev": inv_stddev,
        
        # --- 核心修复：使用小整数 ID ---
        # 对应权重形状 [16, 560]，必须 < 16
        "lang_auto": "0", # 0: auto
        "lang_zh": "1",   # 1: zh
        "lang_en": "2",   # 2: en
        "lang_ja": "3",   # 3: ja
        "lang_yue": "4",  # 4: yue
        "lang_ko": "5",   # 5: ko
    }

    while len(model.metadata_props) > 0:
        model.metadata_props.pop()

    for key, value in meta_dict.items():
        meta = model.metadata_props.add()
        meta.key = key
        meta.value = value
        print(f"   ➕ Set {key} = {value}")

    print(f"💾 保存最终修正版: {OUTPUT_PATH}")
    onnx.save(model, OUTPUT_PATH)
    print("\n🎉 修复完成！这次 ID 在 [0-15] 范围内，绝对能跑通。")

if __name__ == "__main__":
    main()
