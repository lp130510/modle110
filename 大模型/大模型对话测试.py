import requests

# 服务端的 URL
url = "http://56.20.129.177:8012/generate"

# 与模型交互的主循环
while True:
    # 获取用户输入
    prompt = input("请输入你的问题（输入 'quit' 退出）: ")

    # 检查是否退出
    if prompt.lower() == 'quit':
        print("退出程序。")
        break

    # 构建请求数据
    data = {"prompt": prompt}

    try:
        # 发送 POST 请求
        response = requests.post(url, json=data)

        # 检查响应状态码
        if response.status_code == 200:
            # 打印模型的回复
            response_data = response.json()
            print("模型回复：", response_data.get("response", "无回复内容"))
        else:
            # 如果状态码不是 200，打印错误信息
            print(f"错误：{response.status_code} - {response.text}")
    except requests.RequestException as e:
        # 如果请求过程中发生异常，打印错误信息
        print(f"请求发生错误: {e}")
