#!/bin/bash
set -euo pipefail

echo "=== 开始扫描并合并文件 ==="

# 默认自动选择一个可用模型进行合并（model.onnx -> model_quant.onnx -> model_full.onnx）。
# 可通过 AUTO_MERGE_TARGET 或 AUTO_MERGE_ALL 覆盖。
# AUTO_MERGE_TARGET 示例：model.onnx / model_quant.onnx / model_full.onnx
AUTO_MERGE_TARGET="${AUTO_MERGE_TARGET:-}"
AUTO_MERGE_ALL="${AUTO_MERGE_ALL:-0}"

merge_one_group() {
    local first_part="$1"
    local original_file="${first_part%.part000}"
    local display_name
    display_name=$(basename "$original_file")
    local temp_file="${original_file}.merge_tmp"

    echo "----------------------------------------"
    echo "发现分片组，目标: $original_file"
    echo "正在合并..."

    cat "${original_file}.part"* > "$temp_file"
    mv "$temp_file" "$original_file"

    echo "合并成功: $display_name"
    echo "正在清理分片文件..."
    rm -f "${original_file}.part"*
}

matched=0

if [ "$AUTO_MERGE_ALL" = "1" ]; then
    while IFS= read -r -d '' first_part; do
        merge_one_group "$first_part"
        matched=1
    done < <(find . -type f -name "*.part000" -print0)
else
    if [ -n "$AUTO_MERGE_TARGET" ]; then
        while IFS= read -r -d '' first_part; do
            merge_one_group "$first_part"
            matched=1
        done < <(find . -type f -name "${AUTO_MERGE_TARGET}.part000" -print0)
    else
        for preferred in model.onnx model_quant.onnx model_full.onnx; do
            while IFS= read -r -d '' first_part; do
                merge_one_group "$first_part"
                matched=1
            done < <(find . -type f -name "${preferred}.part000" -print0)
            if [ "$matched" = "1" ]; then
                break
            fi
        done
    fi
fi

if [ "$matched" = "0" ]; then
    if [ "$AUTO_MERGE_ALL" = "1" ]; then
        echo "未发现可合并分片，跳过。"
    elif [ -n "$AUTO_MERGE_TARGET" ]; then
        echo "未发现 ${AUTO_MERGE_TARGET}.part000，跳过。"
    else
        echo "未发现可用于运行时的模型分片（model.onnx/model_quant.onnx/model_full.onnx），跳过。"
    fi
fi

echo "----------------------------------------"
echo "=== 所有操作完成 ==="
