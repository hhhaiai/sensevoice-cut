#!/bin/bash

# =================配置区域=================
# 目标文件最小阈值 (大于此大小才切割)
LIMIT_SIZE="90M"
# 切割后的分片大小
CHUNK_SIZE="49m"
# =========================================

echo "=== 开始递归扫描并切割文件 ==="
echo "阈值: >$LIMIT_SIZE | 分片大小: $CHUNK_SIZE"

# find 命令解释：
# .             : 从当前目录开始
# -type f       : 只查找文件
# -size +$LIMIT_SIZE : 查找大于 90M 的文件
# ! -name "*.part*"  : 排除掉名字里包含 .part 的文件（防止重复切割分片）
# -print0       : 处理文件名中的空格和特殊字符

find . -type f -size +$LIMIT_SIZE ! -name "*.part*" -print0 | while IFS= read -r -d '' file; do

    # 获取文件名（用于显示）
    filename=$(basename "$file")

    echo "----------------------------------------"
    echo "发现大文件: $file"
    echo "正在切割..."

    # 执行切割
    # -b: 大小
    # -d: 使用数字后缀
    # -a 3: 后缀长度为3位 (000, 001...)，防止文件过大时排序错乱
    # "$file.part": 输出的文件名前缀，路径与原文件保持一致
    split -b $CHUNK_SIZE -d -a 3 "$file" "$file.part"

    # 检查切割是否成功
    if [ $? -eq 0 ]; then
        echo "切割成功，删除原文件: $filename"
        rm "$file"
    else
        echo "❌ 错误: 切割失败，保留原文件。"
    fi
done

echo "----------------------------------------"
echo "=== 所有操作完成 ==="
