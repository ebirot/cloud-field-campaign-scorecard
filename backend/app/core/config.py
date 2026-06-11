"""
Configuration Management
Using Pydantic Settings for environment variables
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/scorecard_db"

    # Tableau
    TABLEAU_SERVER_URL: str
    TABLEAU_SITE_ID: str
    TABLEAU_TOKEN_NAME: str
    TABLEAU_TOKEN_VALUE: str
    TABLEAU_API_VERSION: str = "3.19"

    # Tableau Workbook IDs
    TABLEAU_WORKBOOK_MDP_SCORECARD: str = "1534752"
    TABLEAU_WORKBOOK_LEAD_PERFORMANCE: str = ""
    TABLEAU_WORKBOOK_CAMPAIGN_PERFORMANCE: str = ""

    # Lead Scorecard Workbook IDs
    TABLEAU_WORKBOOK_LEAD_LEADERBOARD_CLOUD: str = ""
    TABLEAU_WORKBOOK_LEAD_LEADERBOARD_OU: str = ""
    TABLEAU_WORKBOOK_LEAD_CORE_NONCORE: str = ""
    TABLEAU_WORKBOOK_LEAD_SOURCE: str = ""
    TABLEAU_WORKBOOK_LEAD_SCORE: str = ""
    TABLEAU_WORKBOOK_LEAD_TRAFFIC_FLAG: str = ""

    # Slack
    SLACK_BOT_TOKEN: str
    SLACK_CHANNEL_ID: str
    SLACK_APP_TOKEN: str = ""

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS: str = "./credentials/google-service-account.json"
    GOOGLE_SLIDES_TEMPLATE_ID: str = ""

    # API Security
    API_SECRET_KEY: str
    API_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS (will be parsed from comma-separated string in .env)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
