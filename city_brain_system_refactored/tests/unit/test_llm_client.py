import pytest

from infrastructure.external.llm_client import LLMClient, ChatMessage

class DummyLLMClient(LLMClient):
    def _make_request_with_retry(self, endpoint: str, payload: dict):
        # 构造一个与 API 相近的响应结构
        return {
            "choices": [
                {
                    "message": {"content": "OK: 测试响应"},
                    "finish_reason": "stop"
                }
            ],
            "model": payload.get("model", "deepseek-chat"),
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }

def test_chat_accepts_string_messages():
    client = DummyLLMClient(api_key="dummy", base_url="http://dummy")
    resp = client.chat(messages=["你好", "请做一个简短介绍"])
    assert resp.success is True
    assert "OK" in resp.content

def test_chat_accepts_dict_messages():
    client = DummyLLMClient(api_key="dummy", base_url="http://dummy")
    msgs = [
        {"role": "system", "content": "你是一个专业助手"},
        {"role": "user", "content": "请总结以下文本"}
    ]
    resp = client.chat(messages=msgs, temperature=0.5)
    assert resp.success is True
    assert resp.finish_reason in (None, "stop")

def test_chat_accepts_chatmessage_objects():
    client = DummyLLMClient(api_key="dummy", base_url="http://dummy")
    msgs = [
        ChatMessage.system("系统指令"),
        ChatMessage.user("用户消息")
    ]
    resp = client.chat(messages=msgs, max_tokens=64)
    assert resp.success is True
    assert isinstance(resp.usage, dict)