import os
import base64
from openai import OpenAI

def read_text_file(file_path):
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"读取文本文件失败: {e}")
        return None

def encode_image_to_base64(file_path):
    """将图片文件编码为 Base64 格式"""
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except Exception as e:
        print(f"编码图片文件失败: {e}")
        return None

def normalize_path(path):
    path = path.strip().strip('"').strip("'")
    path = os.path.expanduser(path)
    path = os.path.normpath(path)
    return path

def main():
    # 初始化 OpenAI 客户端
    client = OpenAI()
    
    # 输入文件路径
    text_file_path = input("请输入文本文件路径: ").strip().strip('"')
    image_file_path = input("请输入图片文件路径: ").strip().strip('"')
    
    # 准备审核内容
    inputs = []
    
    # 添加文本内容
    if text_file_path and os.path.exists(text_file_path):
        text_content = read_text_file(text_file_path)
        if text_content:
            inputs.append({"type": "text", "text": text_content})
    
    # 添加图片内容
    if image_file_path and os.path.exists(image_file_path):
        base64_image = encode_image_to_base64(image_file_path)
        if base64_image:
            inputs.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
    
    # 检查是否有内容可审核
    if not inputs:
        print("没有有效的内容可审核，请检查文件路径是否正确。")
        return
    
    try:
        # 调用审核 API
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=inputs
        )
        
        # 输出审核结果
        print(response)
        
        
    except Exception as e:
        print(f"调用审核 API 失败: {e}")

if __name__ == "__main__":
    main()
