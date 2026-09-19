"""
⚙️ Settings Models - Type-safe Configuration Structures

Pydantic-based settings models for type-safe configuration management
with validation, environment variable support, and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from pathlib import Path
import os


class DatabaseSettings(BaseModel):
    """Database configuration settings"""
    url: str = Field(default="sqlite:///mova.db", description="Database connection URL")
    pool_size: int = Field(default=5, ge=1, le=100, description="Connection pool size")
    echo: bool = Field(default=False, description="Enable SQL query logging")
    pool_timeout: int = Field(default=30, ge=1, description="Pool timeout in seconds")
    pool_recycle: int = Field(default=3600, ge=1, description="Pool recycle time in seconds")

    @validator('url')
    def validate_url(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Database URL cannot be empty")
        return v.strip()


class ServerSettings(BaseModel):
    """Server configuration settings"""
    host: str = Field(default="localhost", description="Server host address")
    port: int = Field(default=8094, ge=1, le=65535, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    workers: int = Field(default=1, ge=1, le=32, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload in development")
    access_log: bool = Field(default=True, description="Enable access logging")

    @validator('host')
    def validate_host(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Server host cannot be empty")
        return v.strip()


class LoggingSettings(BaseModel):
    """Logging configuration settings"""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file: Optional[str] = Field(default=None, description="Log file path")
    max_bytes: int = Field(default=10485760, ge=1024, description="Max log file size in bytes")
    backup_count: int = Field(default=5, ge=0, description="Number of backup log files")

    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid logging level. Must be one of: {valid_levels}")
        return v.upper()


class TTSSettings(BaseModel):
    """Text-to-Speech configuration settings"""
    default_engine: str = Field(default="gtts", description="Default TTS engine")
    default_language: str = Field(default="en", description="Default language code")
    cache_enabled: bool = Field(default=True, description="Enable TTS caching")
    cache_dir: Optional[str] = Field(default=None, description="TTS cache directory")
    voice_speed: float = Field(default=1.0, ge=0.1, le=3.0, description="Voice speed multiplier")
    volume: float = Field(default=1.0, ge=0.0, le=2.0, description="Audio volume")

    @validator('default_language')
    def validate_language(cls, v):
        # Basic language code validation
        if not v or len(v) < 2:
            raise ValueError("Language code must be at least 2 characters")
        return v.lower()


class STTSettings(BaseModel):
    """Speech-to-Text configuration settings"""
    default_engine: str = Field(default="whisper", description="Default STT engine")
    default_language: str = Field(default="en", description="Default language code")
    model: str = Field(default="base", description="STT model size")
    energy_threshold: int = Field(default=300, ge=0, description="Voice detection energy threshold")
    pause_threshold: float = Field(default=0.8, ge=0.1, description="Pause detection threshold")
    timeout: float = Field(default=30.0, ge=1.0, description="Recognition timeout")

    @validator('default_language')
    def validate_language(cls, v):
        if not v or len(v) < 2:
            raise ValueError("Language code must be at least 2 characters")
        return v.lower()


class AudioSettings(BaseModel):
    """Audio processing configuration settings"""
    sample_rate: int = Field(default=44100, description="Audio sample rate")
    channels: int = Field(default=2, ge=1, le=8, description="Number of audio channels")
    buffer_size: int = Field(default=1024, ge=64, description="Audio buffer size")
    input_device: Optional[str] = Field(default=None, description="Input audio device")
    output_device: Optional[str] = Field(default=None, description="Output audio device")
    noise_reduction: bool = Field(default=True, description="Enable noise reduction")

    @validator('sample_rate')
    def validate_sample_rate(cls, v):
        valid_rates = [8000, 16000, 22050, 44100, 48000, 96000]
        if v not in valid_rates:
            raise ValueError(f"Invalid sample rate. Must be one of: {valid_rates}")
        return v


class VoiceUISettings(BaseModel):
    """Voice UI configuration settings"""
    wake_word: str = Field(default="mova", description="Wake word for activation")
    sensitivity: float = Field(default=0.7, ge=0.1, le=1.0, description="Wake word sensitivity")
    timeout: int = Field(default=30, ge=5, description="Session timeout in seconds")
    continuous_mode: bool = Field(default=False, description="Enable continuous listening")
    beep_on_start: bool = Field(default=True, description="Play beep when starting")
    beep_on_end: bool = Field(default=True, description="Play beep when ending")

    @validator('wake_word')
    def validate_wake_word(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError("Wake word must be at least 2 characters")
        return v.strip().lower()


class SecuritySettings(BaseModel):
    """Security configuration settings"""
    enable_cors: bool = Field(default=True, description="Enable CORS")
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")
    api_key_required: bool = Field(default=False, description="Require API key authentication")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    rate_limit_enabled: bool = Field(default=False, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, ge=1, description="Requests per minute limit")

    @validator('api_key')
    def validate_api_key(cls, v):
        if v is not None and len(v.strip()) < 8:
            raise ValueError("API key must be at least 8 characters")
        return v


class MovaSettings(BaseModel):
    """Main Mova configuration settings"""

    # Core settings
    app_name: str = Field(default="Mova Voice System", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development/production)")

    # Component settings
    server: ServerSettings = Field(default_factory=ServerSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    stt: STTSettings = Field(default_factory=STTSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    voice_ui: VoiceUISettings = Field(default_factory=VoiceUISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)

    # Additional settings
    data_dir: str = Field(default="~/.mova", description="Data directory path")
    temp_dir: str = Field(default="/tmp/mova", description="Temporary directory path")
    max_file_size: int = Field(default=100*1024*1024, ge=1024, description="Max file size in bytes")

    class Config:
        """Pydantic configuration"""
        env_prefix = "MOVA_"
        case_sensitive = False
        validate_assignment = True
        use_enum_values = True

    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'production', 'testing']
        if v.lower() not in valid_envs:
            raise ValueError(f"Invalid environment. Must be one of: {valid_envs}")
        return v.lower()

    @validator('data_dir', 'temp_dir')
    def expand_paths(cls, v):
        """Expand user paths like ~/.mova"""
        return str(Path(v).expanduser().resolve())

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'MovaSettings':
        """
        Create settings from dictionary

        Args:
            config_dict: Configuration dictionary

        Returns:
            MovaSettings instance
        """
        return cls(**config_dict)

    @classmethod
    def from_env(cls) -> 'MovaSettings':
        """
        Create settings from environment variables

        Returns:
            MovaSettings instance with environment overrides
        """
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary

        Returns:
            Settings as dictionary
        """
        return self.dict()

    def get_data_path(self, *parts: str) -> Path:
        """
        Get path within data directory

        Args:
            *parts: Path components

        Returns:
            Complete path within data directory
        """
        path = Path(self.data_dir)
        for part in parts:
            path = path / part
        return path

    def get_temp_path(self, *parts: str) -> Path:
        """
        Get path within temporary directory

        Args:
            *parts: Path components

        Returns:
            Complete path within temporary directory
        """
        path = Path(self.temp_dir)
        for part in parts:
            path = path / part
        return path

    def ensure_directories(self) -> bool:
        """
        Ensure required directories exist

        Returns:
            True if successful
        """
        try:
            # Create data directory
            data_path = Path(self.data_dir)
            data_path.mkdir(parents=True, exist_ok=True)

            # Create temp directory
            temp_path = Path(self.temp_dir)
            temp_path.mkdir(parents=True, exist_ok=True)

            # Create subdirectories
            subdirs = ['logs', 'cache', 'models', 'config', 'audio']
            for subdir in subdirs:
                (data_path / subdir).mkdir(exist_ok=True)
                (temp_path / subdir).mkdir(exist_ok=True)

            return True

        except Exception:
            return False

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == 'development'

    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == 'testing'
