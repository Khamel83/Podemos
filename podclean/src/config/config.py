from pydantic import BaseModel, Field
from typing import List, Optional

class DetectorConfig(BaseModel):
    use_chapters: bool = True
    use_text_rules: bool = True
    use_audio_cues: bool = False
    require_signals: int = 2
    padding_seconds: int = 8
    priors: dict = Field(default_factory=dict)

class EncodingConfig(BaseModel):
    codec: str = "mp3"
    bitrate: str = "v4"
    normalize_loudness: bool = False

class RetentionPolicyConfig(BaseModel):
    enabled: bool = True
    max_episodes_per_show: int = 10
    max_days_per_episode: int = 30

class BacklogProcessingConfig(BaseModel):
    strategy: str = "all" # "all", "newest_only", "last_n_episodes"
    last_n_episodes_count: int = 5

class AppConfig(BaseModel):
    # Server settings
    PODCLEAN_BASE_URL: str = "http://localhost:8080"
    PODCLEAN_BIND: str = "0.0.0.0"
    PODCLEAN_PORT: int = 8080
    PODCLEAN_SECRET_TOKEN: str = "change_me"

    # Media storage
    PODCLEAN_MEDIA_BASE_PATH: str = "./data"

    # Performance
    MAX_PARALLEL_DOWNLOADS: int = 3
    MAX_PARALLEL_TRANSCRIBE: int = 2

    # Fast pass transcription
    FAST_MODEL: str = "small"
    FAST_VAD: bool = True
    FAST_BEAM: int = 1
    FAST_WORD_TS: bool = True

    # Full pass transcription
    FULL_MODEL: str = "medium"
    FULL_VAD: bool = True
    FULL_BEAM: int = 2
    FULL_WORD_TS: bool = True

    # Encoding
    encoding: EncodingConfig = Field(default_factory=EncodingConfig)

    # Feed
    MAX_FEED_ITEMS: int = 500

    # Detector
    detector: DetectorConfig = Field(default_factory=DetectorConfig)

    # Ad detection confidence
    MIN_CONFIDENCE: float = 0.70

    # Feature flags
    FULL_PASS_ENABLED: bool = False # New flag to control full pass transcription

    # Retention Policy
    retention_policy: RetentionPolicyConfig = Field(default_factory=RetentionPolicyConfig)

    # Backlog Processing
    backlog_processing: BacklogProcessingConfig = Field(default_factory=BacklogProcessingConfig)

    # Feed Authentication
    feed_auth_enabled: bool = False
    feed_username: str = "podemos_user"
    feed_password: str = "change_this_password"

class ShowRules(BaseModel):
    phrases: List[str] = Field(default_factory=list)
    url_patterns: List[str] = Field(default_factory=list)
    price_patterns: List[str] = Field(default_factory=list)
    jingles: List[str] = Field(default_factory=list)
    time_priors: dict = Field(default_factory=dict)
    aggressiveness: str = "conservative"
