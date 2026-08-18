from .base import BaseProvider, LLMResponse
from .anthropic_provider import AnthropicProvider
from .openai_compat import (
    OpenAIProvider, OpenRouterProvider,
    DeepSeekProvider, GroqProvider, KimiProvider, ZaiProvider,
)
from .google_provider import GoogleProvider
from .router import LLMRouter


def build_router(cfg: "Config") -> LLMRouter:  # type: ignore[name-defined]
    router = LLMRouter()

    if cfg.ANTHROPIC_API_KEY:
        router.register(AnthropicProvider(cfg.ANTHROPIC_API_KEY))
    if cfg.OPENROUTER_API_KEY:
        router.register(OpenRouterProvider(cfg.OPENROUTER_API_KEY))
    if cfg.OPENAI_API_KEY:
        router.register(OpenAIProvider(cfg.OPENAI_API_KEY))
    if cfg.GOOGLE_API_KEY:
        try:
            router.register(GoogleProvider(cfg.GOOGLE_API_KEY))
        except Exception:
            pass
    if cfg.DEEPSEEK_API_KEY:
        router.register(DeepSeekProvider(cfg.DEEPSEEK_API_KEY))
    if cfg.GROQ_API_KEY:
        router.register(GroqProvider(cfg.GROQ_API_KEY))
    if cfg.KIMI_API_KEY:
        router.register(KimiProvider(cfg.KIMI_API_KEY))
    if cfg.ZAI_API_KEY:
        router.register(ZaiProvider(cfg.ZAI_API_KEY))

    return router
