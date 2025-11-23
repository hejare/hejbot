"""
Configuration module for the Slack bot application.
Loads environment variables and provides centralized config management.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for Slack bot settings."""

    # Slack API Credentials
    SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
    SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
    SLACK_USER_ID = os.environ.get("SLACK_USER_ID")

    # Open AI Credentials
    OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")

    # Application Settings
    PORT = int(os.environ.get("PORT", 3000))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    SOCKET_MODE = os.environ.get("SOCKET_MODE", "True").lower() == "true"
    DEV = os.environ.get("DEV", "True").lower() == "true"

    # Database Settings (PostgreSQL)
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 5432))
    DB_DATABASE = os.environ.get("DB_DATABASE", "hejbot")
    DB_USERNAME = os.environ.get("DB_USERNAME", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_SSL_MODE = os.environ.get("DB_SSL_MODE", "prefer")

    @classmethod
    def validate(cls):
        """Validate that required configuration values are set."""
        required_vars = {
            "SLACK_BOT_TOKEN": cls.SLACK_BOT_TOKEN,
            "SLACK_SIGNING_SECRET": cls.SLACK_SIGNING_SECRET,
        }

        if cls.SOCKET_MODE:
            required_vars["SLACK_APP_TOKEN"] = cls.SLACK_APP_TOKEN

        missing_vars = [var for var, value in required_vars.items() if not value]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file or environment variables."
            )

        return True


# Validate configuration on import
Config.validate()
