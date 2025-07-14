from openai import OpenAI
client = OpenAI()

text = input("请输入要审核的文本：")
moderation = client.moderations.create(input=text)
print(moderation)
