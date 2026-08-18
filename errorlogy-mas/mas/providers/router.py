"""
LLM Router — выбирает провайдера для каждого агента.
Стратегия:
  1. Попробовать предпочтительный провайдер агента
  2. При ошибке — пройти по fallback-цепочке
  3. Логировать провайдер и токены каждого вызова
"""
import logging
from .base import BaseProvider, LLMResponse

logger = logging.getLogger("errorlogy.router")

# Роли агентов → предпочтительные провайдеры (по умолчанию)
AGENT_PREFERENCES: dict[str, list[str]] = {
    "scout":        ["openai", "deepseek", "groq", "openrouter", "anthropic", "google"],
    "wms":          ["openai", "deepseek", "groq", "openrouter", "anthropic"],
    "classifier":   ["openai", "deepseek", "groq", "openrouter", "anthropic"],
    "pno":          ["openai", "deepseek", "google", "openrouter", "anthropic"],
    "acc":          ["openai", "groq", "deepseek", "openrouter", "anthropic"],
    "egd":          ["openai", "deepseek", "google", "openrouter", "anthropic"],
    "t4d":          ["openai", "zai", "kimi", "deepseek", "openrouter", "anthropic"],
    "cat":          ["openai", "deepseek", "groq", "openrouter", "anthropic"],
    "fpd":          ["openai", "deepseek", "google", "openrouter", "anthropic"],
    "lbi":          ["openai", "groq", "deepseek", "openrouter", "anthropic"],
    "red_team":     ["openai", "deepseek", "groq", "openrouter", "anthropic"],
    "neutrality":   ["groq", "deepseek", "openai", "openrouter", "anthropic"],
    "card_compiler":["openai", "zai", "deepseek", "kimi", "openrouter", "anthropic", "google"],
    "default":      ["openai", "deepseek", "groq", "google", "kimi", "openrouter", "anthropic"],
}

# Модели для openrouter по роли (чтобы использовать разные модели для разных задач)
OPENROUTER_MODEL_MAP: dict[str, str] = {
    "classifier":    "anthropic/claude-sonnet-4-6",
    "red_team":      "openai/gpt-4o",
    "neutrality":    "google/gemini-2.0-flash-001",
    "card_compiler": "z-ai/glm-5.2",   # long-form structured public cards
    "t4d":           "z-ai/glm-5.2",   # worldline narrative / long-horizon explanation
    "default":       "anthropic/claude-sonnet-4-6",
}

ZAI_MODEL_MAP: dict[str, str] = {
    "card_compiler": "glm-5.2",
    "t4d":           "glm-5.2",
    "default":       "glm-5.2",
}


class LLMRouter:
    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        self._providers[provider.name] = provider
        logger.info(f"Registered provider: {provider.name}")

    def complete(
        self,
        agent_name: str,
        system: str,
        messages: list[dict],
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> LLMResponse:
        chain = AGENT_PREFERENCES.get(agent_name, AGENT_PREFERENCES["default"])
        errors: list[str] = []

        for provider_name in chain:
            provider = self._providers.get(provider_name)
            if not provider or not provider.is_available():
                continue

            # Pick model
            model: str | None = None
            if provider_name == "openrouter":
                model = OPENROUTER_MODEL_MAP.get(agent_name, OPENROUTER_MODEL_MAP["default"])
            elif provider_name == "zai":
                model = ZAI_MODEL_MAP.get(agent_name, ZAI_MODEL_MAP["default"])

            try:
                resp = provider.complete(system, messages, model=model,
                                         max_tokens=max_tokens, temperature=temperature)
                logger.debug(f"[{agent_name}] {provider_name}/{resp.model} "
                             f"in={resp.input_tokens} out={resp.output_tokens}")
                return resp
            except Exception as exc:
                msg = f"{provider_name}: {exc}"
                errors.append(msg)
                logger.warning(f"[{agent_name}] provider failed — {msg}")

        raise RuntimeError(
            f"All providers failed for agent '{agent_name}':\n" + "\n".join(errors)
        )

    @property
    def available(self) -> list[str]:
        return [n for n, p in self._providers.items() if p.is_available()]
