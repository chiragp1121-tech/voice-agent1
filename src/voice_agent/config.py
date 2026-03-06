from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Multi-Platform Voice AI Agent"
    database_url: str = "sqlite:///./voice_agent.db"


settings = Settings()
