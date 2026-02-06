import json
with open("tokens.json", "r", encoding="utf-8") as f:
    data = json.load(f)
# data 是个列表，直接写出即可，每一行一个 token
with open("tokens.txt", "w", encoding="utf-8") as f:
    for token in data:
        f.write(f"{token}\n")
