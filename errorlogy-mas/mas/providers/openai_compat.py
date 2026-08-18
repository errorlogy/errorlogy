"""
OpenAI-compatible provider base.
Used by: OpenAI, OpenRouter, DeepSeek, Groq, Kimi — all share the same API shape.
"""
from openai import OpenAI
from .base import BaseProvider, LLMResponse


class OpenAICompatProvider(BaseProvider):
    name = "openai_compat"
    models: list[str] = []
    _base_url: str = "https://api.openai.com/v1"

    def __init__(self, api_key: str, base_url: str | None = None) -> None:
        self._api_key = api_key
        self._client = OpenAI(api_key=api_key, base_url=base_url or self._base_url)

    def is_available(self) -> bool:
        return bool(self._api_key)

    def complete(self, system, messages, model=None, max_tokens=4096, temperature=0.2) -> LLMResponse:
        model = model or self.models[0]
        full_messages = [{"role": "system", "content": system}] + messages
        resp = self._client.chat.completions.create(
            model=model,
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        text = resp.choices[0].message.content or ""
        usage = resp.usage
        return LLMResponse(
            text=text,
            provider=self.name,
            model=model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )


class OpenAIProvider(OpenAICompatProvider):
    name = "openai"
    models = ["gpt-4o", "gpt-4o-mini"]


class OpenRouterProvider(OpenAICompatProvider):
    name = "openrouter"
    _base_url = "https://openrouter.ai/api/v1"
    models = [
        "anthropic/claude-sonnet-4-6",
        "openai/gpt-4o",
        "google/gemini-2.0-flash-001",
        "z-ai/glm-5.2",
        "deepseek/deepseek-chat",
        "meta-llama/llama-3.3-70b-instruct",
    ]


class DeepSeekProvider(OpenAICompatProvider):
    name = "deepseek"
    _base_url = "https://api.deepseek.com/v1"
    models = ["deepseek-chat", "deepseek-reasoner"]


class GroqProvider(OpenAICompatProvider):
    name = "groq"
    _base_url = "https://api.groq.com/openai/v1"
    models = ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"]


class KimiProvider(OpenAICompatProvider):
    name = "kimi"
    _base_url = "https://api.moonshot.cn/v1"
    models = ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]


class ZaiProvider(OpenAICompatProvider):
    name = "zai"
    _base_url = "https://api.z.ai/api/paas/v4"
    models = ["glm-5.2", "glm-4.7-flash"]
