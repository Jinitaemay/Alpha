import os
import base64
from openai import OpenAI

class ModerationResult:
    """封装审核结果，包含原始路径和API响应"""
    def __init__(self, image_path, api_response):
        self.image_path = image_path
        self.api_response = api_response
        # 更健壮地处理API响应结构
        try:
            self.flagged = api_response.results[0].flagged if api_response and hasattr(api_response, 'results') and api_response.results else False
        except Exception:
            self.flagged = False
        
    def __str__(self):
        if self.api_response is None:
            return f"路径: {self.image_path}"
        return f"路径: {self.image_path}, 审核结果: {'违规' if self.flagged else '安全'}"

def moderate_image(client, image_path):
    """审核本地图片并返回包含路径的结果对象"""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    try:
        with open(image_path, "rb") as file:
            base64_image = base64.b64encode(file.read()).decode('utf-8')
            # 自动识别图片类型
            ext = os.path.splitext(image_path)[1].lower()
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "application/octet-stream"
            input_data = [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{base64_image}"}
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
import glob

if __name__ == "__main__":
    client = OpenAI()
    if len(sys.argv) < 2:
        print("用法: python image_moderation_client.py <图片路径1> [图片路径2 ...]")
        sys.exit(1)

    # 支持通配符批量处理
    all_image_paths = []
    for raw_path in sys.argv[1:]:
        raw_path = raw_path.strip()
        # 修正正则表达式，去除多余的中括号
        image_path = re.sub(r'^(\["\']?)(.*?)(\["\']?)$', r'\2', raw_path)
        image_path = image_path.replace('/', os.sep).replace('\\', os.sep)
        # 展开通配符
        expanded = glob.glob(image_path)
        if expanded:
            all_image_paths.extend(expanded)
        else:
            all_image_paths.append(image_path)

    if not all_image_paths:
        print("未找到任何图片文件。")
        sys.exit(1)

    for image_path in all_image_paths:
        image_path = os.path.normpath(image_path)
        try:
            result = moderate_image(client, image_path)
            print(result)
            # 保存审核结果到文本文件
            img_name = os.path.splitext(os.path.basename(image_path))[0]
            txt_path = os.path.join(os.path.dirname(image_path), f"{img_name}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(str(result) + "\n")
                if result.api_response:
                    f.write(result.api_response.model_dump_json(indent=2) + "\n")
                else:
                    f.write("未获得API响应。\n")
            if result.api_response:
                print(result.api_response.model_dump_json(indent=2))
            else:
                print("未获得API响应。")
        except Exception as e:
            print(f"处理图片 {image_path} 时出错: {e}")
