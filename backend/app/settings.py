"""应用配置：从环境变量 / .env 读取，勿将密钥提交到仓库。"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenAI 或兼容接口（如部分国内代理）共用
    openai_api_key: str | None = None
    openai_base_url: str | None = None

    petcare_text_model: str = "gpt-4o-mini"
    petcare_vision_model: str = "gpt-4o-mini"


@lru_cache
def get_settings() -> Settings:
    return Settings()
