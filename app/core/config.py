
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     APP_NAME: str = "AI Lead Management System"
#     APP_VERSION: str = "1.0.0"
#     DATABASE_URL: str = "sqlite:///./data/leads.db"

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         extra="ignore"
#     )


# settings = Settings()


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Lead Management System"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./data/leads.db"

    # Authentication for trusted Hermes Agent integrations.
    HERMES_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
