from google import genai
from google.genai import types
from .base import BaseProvider, LLMResponse


class GoogleProvider(BaseProvider):
    name = "google"
    models = ["gemini-2.0-flash", "gemini-2.5-flash-preview-05-20", "gemini-1.5-pro"]

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = genai.Client(api_key=api_key)

    def is_available(self) -> bool:
        return bool(self._api_key)

    def complete(self, system, messages, model=None, max_tokens=4096, temperature=0.2) -> LLMResponse:
        model_name = model or self.models[0]
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=temperature,
        )
        response = self._client.models.generate_content(
            model=model_name,
            contents=contents,
            config=config,
        )
        text = response.text or ""
        return LLMResponse(text=text, provider=self.name, model=model_name)
