#!/bin/bash

echo "=== 开始递归扫描并合并文件 ==="

# 查找所有以 .part000 结尾的文件（这是分片的第一个部分）
# 只要找到了第000号分片，就说明有一组文件需要合并
find . -type f -name "*.part000" -print0 | while IFS= read -r -d '' first_part; do

    # 获取原始文件路径（去掉 .part000 后缀）
    # 例如: ./subdir/video.mp4.part000 -> ./subdir/video.mp4
    original_file="${first_part%.part000}"

    # 获取文件名用于显示
    display_name=$(basename "$original_file")

    echo "----------------------------------------"
    echo "发现分片组，目标: $original_file"
    echo "正在合并..."

    # 合并操作
    # 使用通配符 *.part* 匹配该文件的所有分片
    # Bash 会自动按字母/数字顺序排序 (part000, part001, part002...)
    cat "${original_file}.part"* > "$original_file"

    # 检查合并结果
    if [ $? -eq 0 ]; then
        echo "合并成功: $display_name"
        echo "正在清理分片文件..."
        # 删除该文件的所有分片
        rm "${original_file}.part"*
    else
        echo "❌ 错误: 合并失败，未删除分片文件。"
    fi
done

echo "----------------------------------------"
echo "=== 所有操作完成 ==="
