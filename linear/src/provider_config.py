from dataclasses import dataclass
import os


@dataclass
class ProviderConfig:
    llm_provider: str = "openai"
    llm_model: str = "gpt-5"
    memory_backend: str = "memory"  # memory|kv|d1|external


def load_provider_config() -> ProviderConfig:
    return ProviderConfig(
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_model=os.getenv("LLM_MODEL", "gpt-5"),
        memory_backend=os.getenv("MEMORY_BACKEND", "memory"),
    )
