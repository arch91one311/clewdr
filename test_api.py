"""ClewdR API 测试脚本 - Claude Opus 4.6"""

import json
import os
import urllib.request
import urllib.error

BASE_URL = os.environ.get("CLEWDR_BASE_URL", "http://127.0.0.1:8484")
API_KEY = os.environ.get("CLEWDR_API_KEY", "your-api-key-here")
MODEL = "claude-opus-4-6"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def request(method, path, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def test_models():
    print("=" * 50)
    print("[1] GET /v1/models - 获取模型列表")
    print("=" * 50)
    status, body = request("GET", "/v1/models")
    print(f"状态码: {status}")
    data = json.loads(body)
    for m in data.get("data", []):
        print(f"  - {m['id']}")
    print()


def test_chat_completions():
    print("=" * 50)
    print("[2] POST /v1/chat/completions - OpenAI 兼容格式")
    print("=" * 50)
    status, body = request("POST", "/v1/chat/completions", {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "用一句话介绍量子计算"},
        ],
        "max_tokens": 200,
    })
    print(f"状态码: {status}")
    data = json.loads(body)
    if "choices" in data:
        print(f"回复: {data['choices'][0]['message']['content']}")
        print(f"用量: {data.get('usage', {})}")
    else:
        print(f"错误: {body}")
    print()


def test_messages():
    print("=" * 50)
    print("[3] POST /v1/messages - Claude 原生格式")
    print("=" * 50)
    status, body = request("POST", "/v1/messages", {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "用一句话介绍相对论"},
        ],
        "max_tokens": 200,
    })
    print(f"状态码: {status}")
    data = json.loads(body)
    if "content" in data:
        for block in data["content"]:
            if block.get("type") == "text":
                print(f"回复: {block['text']}")
        print(f"用量: {data.get('usage', {})}")
    else:
        print(f"错误: {body}")
    print()


def test_streaming():
    print("=" * 50)
    print("[4] POST /v1/chat/completions - 流式请求")
    print("=" * 50)
    url = f"{BASE_URL}/v1/chat/completions"
    data = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "写一首关于春天的五言绝句"},
        ],
        "max_tokens": 200,
        "stream": True,
    }).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            print(f"状态码: {resp.status}")
            print("回复: ", end="", flush=True)
            buffer = ""
            for chunk in iter(lambda: resp.read(1).decode(), ""):
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload == "[DONE]":
                        break
                    obj = json.loads(payload)
                    delta = obj.get("choices", [{}])[0].get("delta", {})
                    text = delta.get("content", "")
                    if text:
                        print(text, end="", flush=True)
            print("\n")
    except urllib.error.HTTPError as e:
        print(f"错误 {e.code}: {e.read().decode()}\n")


def test_count_tokens():
    print("=" * 50)
    print("[5] POST /code/v1/messages/count_tokens - Token 计数")
    print("=" * 50)
    status, body = request("POST", "/code/v1/messages/count_tokens", {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "Hello, how are you today?"},
        ],
        "max_tokens": 100,
    })
    print(f"状态码: {status}")
    data = json.loads(body)
    print(f"Input tokens: {data.get('input_tokens', 'N/A')}")
    print()


def test_multi_turn():
    print("=" * 50)
    print("[6] POST /v1/chat/completions - 多轮对话")
    print("=" * 50)
    status, body = request("POST", "/v1/chat/completions", {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": "我叫小明"},
            {"role": "assistant", "content": "你好小明！有什么可以帮你的？"},
            {"role": "user", "content": "我叫什么名字？"},
        ],
        "max_tokens": 100,
    })
    print(f"状态码: {status}")
    data = json.loads(body)
    if "choices" in data:
        print(f"回复: {data['choices'][0]['message']['content']}")
    else:
        print(f"错误: {body}")
    print()


def test_system_prompt():
    print("=" * 50)
    print("[7] POST /v1/chat/completions - 系统提示")
    print("=" * 50)
    status, body = request("POST", "/v1/chat/completions", {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "你是一个海盗，所有回复都要用海盗的口吻。"},
            {"role": "user", "content": "今天天气怎么样？"},
        ],
        "max_tokens": 200,
    })
    print(f"状态码: {status}")
    data = json.loads(body)
    if "choices" in data:
        print(f"回复: {data['choices'][0]['message']['content']}")
    else:
        print(f"错误: {body}")
    print()


if __name__ == "__main__":
    print(f"ClewdR API 测试 | 模型: {MODEL}")
    print(f"Base URL: {BASE_URL}\n")

    test_models()
    test_chat_completions()
    test_messages()
    test_streaming()
    test_count_tokens()
    test_multi_turn()
    test_system_prompt()

    print("=" * 50)
    print("所有测试完成")
