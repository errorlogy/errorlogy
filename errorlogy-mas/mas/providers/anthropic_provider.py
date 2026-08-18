import anthropic
from .base import BaseProvider, LLMResponse


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    models = ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "claude-opus-4-8"]

    def __init__(self, api_key: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)
        self._api_key = api_key

    def is_available(self) -> bool:
        return bool(self._api_key)

    def complete(self, system, messages, model=None, max_tokens=4096, temperature=0.2) -> LLMResponse:
        model = model or "claude-sonnet-4-6"
        resp = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
            temperature=temperature,
        )
        text = "".join(b.text for b in resp.content if hasattr(b, "text"))
        return LLMResponse(
            text=text,
            provider=self.name,
            model=model,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
        )
