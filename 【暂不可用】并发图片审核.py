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
    """审核单张本地图片并返回结果对象"""
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

def moderate_images(client, image_paths):
    """审核多张本地图片并返回结果列表"""
    if not image_paths:
        raise ValueError("请提供至少一张图片路径")
    
    # 构建所有图片的输入数据
    input_data = []
    for path in image_paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"图片文件不存在: {path}")
        
        try:
            with open(path, "rb") as file:
                base64_image = base64.b64encode(file.read()).decode('utf-8')
                input_data.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                })
        except Exception as e:
            print(f"无法处理图片 {path}: {e}")
    
    if not input_data:
        raise ValueError("所有图片均无法处理")
    
    # 调用API
    try:
        response = client.moderations.create(
            model="omni-moderation-latest",
            input=input_data
        )
        
        # 将结果与原始路径一一对应
        results = []
        for i, path in enumerate(image_paths):
            if i < len(response.results):
                # 为每张图片创建单独的结果对象
                results.append(ModerationResult(path, response))
            else:
                # 如果API返回的结果少于请求数量（异常情况）
                results.append(ModerationResult(path, None))
        
        return results
    except Exception as e:
        print(f"调用OpenAI Moderation API时出错: {e}")
        # 为每个路径创建失败结果
        return [ModerationResult(path, None) for path in image_paths]

# 使用示例
if __name__ == "__main__":
    client = OpenAI()
    
    # 批量审核多张图片
    image_paths = [
        r"C:\Users\18918\Documents\test\92126507_p0.png",
        r"C:\Users\18918\Documents\test\92126507_p1.png",
        r"C:\Users\18918\Documents\test\92126507_p2.png"
    ]
    
    results = moderate_images(client, image_paths)
    
    # 输出每张图片的审核结果
    for result in results:
        print(result)  # 打印简要结果
        if result.api_response:
            # 获取该图片对应的审核结果（假设结果顺序与输入一致）
            image_result = result.api_response.results[results.index(result)]
            print(json.dumps(image_result.model_dump(), indent=2))    