import os
import base64
from openai import OpenAI

class ModerationResult:
    """封装审核结果，包含原始路径和API响应"""
    def __init__(self, image_path, api_response):
        self.image_path = image_path
        self.api_response = api_response
        self.flagged = api_response.results[0].flagged if api_response else False
        
    def __str__(self):
        return f"路径: {self.image_path}, 审核结果: {'违规' if self.flagged else '安全'}"

def moderate_image(client, image_path):
    """审核本地图片并返回包含路径的结果对象"""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    try:
        with open(image_path, "rb") as file:
            base64_image = base64.b64encode(file.read()).decode('utf-8')
            input_data = [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
            
            response = client.moderations.create(
                model="omni-moderation-latest",
                input=input_data
            )
            
            return ModerationResult(image_path, response)
    except Exception as e:
        print(f"调用OpenAI Moderation API时出错: {e}")
        return ModerationResult(image_path, None)


# 命令行参数支持
import sys
import re

if __name__ == "__main__":
    client = OpenAI()
    if len(sys.argv) < 2:
        print("用法: python image_moderation_client.py <图片路径1> [图片路径2 ...]")
        sys.exit(1)

    for raw_path in sys.argv[1:]:
        raw_path = raw_path.strip()
        # 修正正则表达式，去除多余的中括号
        image_path = re.sub(r'^(["\']?)(.*?)(["\']?)$', r'\2', raw_path)
        image_path = image_path.replace('/', os.sep).replace('\\', os.sep)
        result = moderate_image(client, image_path)
        print(result)
        if result.api_response:
            print(result.api_response.model_dump_json(indent=2))
        else:
            print("未获得API响应。")
