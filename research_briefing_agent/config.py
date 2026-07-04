import os
from dataclasses import dataclass


DEFAULT_MODEL = "gpt-5.5"
DEFAULT_PROVIDER = "openai"
DEFAULT_MAX_FINDINGS = 5
DEFAULT_MIN_SOURCE_BACKED_FINDINGS = 3
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
OPENAI_CHAT_BASE_URL = "https://api.openai.com/v1"
LLM_PROVIDERS = (
    "openai",
    "openai-chat",
    "deepseek",
    "qwen",
    "moonshot",
    "zhipu",
    "custom-chat",
)
CHAT_PROVIDER_PRESETS = {
    "openai-chat": {
        "api_key_env": "OPENAI_API_KEY",
        "base_url": OPENAI_CHAT_BASE_URL,
        "model": DEFAULT_MODEL,
    },
    "deepseek": {
        "api_key_env": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-v4-pro",
    },
    "qwen": {
        "api_key_env": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "moonshot": {
        "api_key_env": "MOONSHOT_API_KEY",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-128k",
    },
    "zhipu": {
        "api_key_env": "ZHIPU_API_KEY",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-plus",
    },
    "custom-chat": {
        "api_key_env": "LLM_API_KEY",
        "base_url": "",
        "model": "",
    },
}
OUTPUT_FORMATS = (
    "markdown",
    "ppt-outline",
    "speaker-notes",
    "qa",
    "docx",
    "pdf",
    "pptx",
)


@dataclass
class AppConfig:
    llm_provider: str = DEFAULT_PROVIDER
    openai_api_key: str = ""
    openai_model: str = DEFAULT_MODEL
    chat_api_key: str = ""
    chat_api_key_env: str = ""
    chat_base_url: str = ""
    chat_model: str = ""
    max_findings: int = DEFAULT_MAX_FINDINGS
    min_source_backed_findings: int = DEFAULT_MIN_SOURCE_BACKED_FINDINGS
    openai_responses_url: str = OPENAI_RESPONSES_URL
    llm_timeout_seconds: int = 60

    def use_provider(self, provider: str) -> None:
        self.llm_provider = provider
        if provider == "openai":
            return
        preset = CHAT_PROVIDER_PRESETS.get(provider, CHAT_PROVIDER_PRESETS["custom-chat"])
        self.chat_api_key_env = preset["api_key_env"]
        self.chat_api_key = os.environ.get(self.chat_api_key_env, "")
        self.chat_base_url = preset["base_url"]
        self.chat_model = preset["model"]

    @classmethod
    def from_env(cls) -> "AppConfig":
        provider = os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER)
        preset = CHAT_PROVIDER_PRESETS.get(provider, CHAT_PROVIDER_PRESETS["custom-chat"])
        chat_api_key_env = os.environ.get("LLM_API_KEY_ENV", preset["api_key_env"])
        chat_model = os.environ.get("LLM_MODEL", os.environ.get("OPENAI_MODEL", preset["model"]))
        return cls(
            llm_provider=provider,
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
            openai_model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
            chat_api_key=os.environ.get(chat_api_key_env, ""),
            chat_api_key_env=chat_api_key_env,
            chat_base_url=os.environ.get("LLM_BASE_URL", preset["base_url"]),
            chat_model=chat_model,
            max_findings=_int_from_env("MAX_FINDINGS", DEFAULT_MAX_FINDINGS),
            min_source_backed_findings=_int_from_env(
                "MIN_SOURCE_BACKED_FINDINGS",
                DEFAULT_MIN_SOURCE_BACKED_FINDINGS,
            ),
            openai_responses_url=os.environ.get(
                "OPENAI_RESPONSES_URL",
                OPENAI_RESPONSES_URL,
            ),
            llm_timeout_seconds=_int_from_env("LLM_TIMEOUT_SECONDS", 60),
        )


def _int_from_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default
