"""
MCP Code Analyzer 設定管理
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """アプリケーション設定"""

    app_name: str = "MCP Code Analyzer"
    debug: bool = Field(default=False, env="DEBUG")

    # AI API設定
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # 解析設定
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    analysis_timeout: int = Field(default=300, env="ANALYSIS_TIMEOUT")
    
    # MCP設定
    mcp_server_name: str = Field(default="code-analyzer", env="MCP_SERVER_NAME")
    mcp_server_version: str = Field(default="1.0.0", env="MCP_SERVER_VERSION")

    class Config:
        env_file = ".env"
        case_sensitive = False

# グローバル設定インスタンス
settings = Settings()