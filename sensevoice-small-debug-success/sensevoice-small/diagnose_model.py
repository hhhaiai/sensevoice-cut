"""
问题诊断
"""
import onnx
import os

MODEL_PATH = "./model_sherpa.onnx"
# MODEL_PATH = "./model.onnx"

def diagnose():
    if not os.path.exists(MODEL_PATH):
        print("❌ 找不到模型文件")
        return

    print(f"🕵️‍♂️ 正在诊断模型: {MODEL_PATH} ...")
    model = onnx.load(MODEL_PATH)

    # 1. 打印模型的所有输入口
    print("\n[1] 模型输入接口 (Inputs):")
    for input in model.graph.input:
        dims = [str(d.dim_value) if d.dim_value > 0 else "?" for d in input.type.tensor_type.shape.dim]
        print(f"   👉 {input.name}: [{', '.join(dims)}]")

    # 2. 寻找报错的节点 /embed/Gather
    print("\n[2] 寻找嫌疑节点 '/embed/Gather':")
    target_node = None
    for node in model.graph.node:
        if "/embed/Gather" in node.name or "Gather" in node.op_type:
            # 检查是否是那个只有几行数据的节点
            # Gather 的输入[0]是数据(Data)，输入[1]是索引(Indices)
            data_input_name = node.input[0]
            
            # 在 Initializer (权重) 中查找这个数据的大小
            for init in model.graph.initializer:
                if init.name == data_input_name:
                    if init.dims[0] < 100: # 如果第一维很小，就是它了！
                        print(f"   🚨 找到可疑 Gather 节点: {node.name}")
                        print(f"      输入权重名: {data_input_name}")
                        print(f"      权重形状 (Shape): {init.dims}")
                        print(f"      ⚠️ 结论: 这个节点只能接受 0 到 {init.dims[0]-1} 之间的数字！")
                        return init.dims[0] # 返回最大上限

    print("   ⚠️ 未找到明显的小维度 Gather 节点，可能是动态生成的。")
    return None

if __name__ == "__main__":
    limit = diagnose()
    if limit:
        print(f"\n💡 诊断建议: 请修改 fix_model 脚本，将 lang_auto 等 ID 设为 0 到 {limit-1} 之间的小整数。")
