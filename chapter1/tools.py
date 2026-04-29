import os
import requests
from tavily import TavilyClient

def get_attraction(city: str, weather: str) -> str:
    """
    根据城市和天气，调用 Tavily API搜索并返回优化后的景点推荐。
    """

    # 1. 从环境变量中读取API密钥
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Tavily API 密钥未配置，请检查环境变量设置。"
    
    # 2. 初始化Tavily客户端
    tavily = TavilyClient(api_key=api_key)

    # 3. 构造一个精确的查询
    query = f"推荐在{city}天气{weather}时适合游玩的景点，并提供简短的理由。"

    try:
        # 4. 调用API，include_answer=True会返回一个综合性的回答
        response = tavily.search(query=query, search_depth="basic", include_answer=True)

        # 5. Tavily返回的结果已经非常干净，可以直接使用
        # response['answer'] 是一个基于所有搜索结果的总结性回答
        if response.get('answer'):
            return response['answer']
        
        # 如果没有综合性回答，则格式化原始结果
        formatted_results = []
        for result in response.get("results", []):
            formatted_results.append(f"{result['title']}: {result['snippet']}")

        if not formatted_results:
            return "抱歉，没有找到相关的景点推荐。"
        
        return "根据搜索，为您找到以下信息:\n" + "\n".join(formatted_results)
    except Exception as e:
        return f"错误:执行Tavily搜索时出现问题 - {e}"


def get_weather(city: str) -> str:
    """
    通过调用 wttr.in API 查询真实的天气信息。
    """

    # API端点，我们请求JSON格式的数据
    url = f"https://wttr.in/{city}?format=j1"

    try:
        # 发送GET请求
        response = requests.get(url)
        # 检查响应状态码是否为200 (成功)
        response.raise_for_status()
        # 解析JSON响应
        data = response.json()

        # 提取当前天气信息
        current_condition = data['current_condition'][0]
        weather_desc = current_condition['weatherDesc'][0]['value']
        temp_c = current_condition['temp_C']

        # 格式化成自然语言
        return f"{city}当前天气:{weather_desc}, 温度: {temp_c}摄氏度"

    except requests.RequestException as e:
        # 处理网络错误
        return f"无法获取天气信息: {e}"
    except (KeyError, IndexError) as e:
        # 处理数据解析错误
        return f"错误：解析天气数据失败，可能是城市名称无效 - {e}"