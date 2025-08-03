import yaml
import os
from src.config.config import AppConfig, ShowRules, DetectorConfig, EncodingConfig, RetentionPolicyConfig, BacklogProcessingConfig

def load_config(config_path: str) -> dict:
    """
    Loads a YAML configuration file.
    """
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_env_config() -> dict:
    """
    Loads configuration from environment variables.
    """
    env_config = {}
    # Iterate through common expected env vars and load them
    for key in AppConfig.__fields__.keys():
        if key in os.environ:
            env_config[key] = os.environ[key]
    return env_config

def load_show_rules(show_slug: str = None) -> ShowRules:
    """
    Loads default and optionally show-specific rules, merging them.
    """
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'shows')
    default_rules_path = os.path.join(base_dir, 'default.rules.yaml')
    
    default_rules_data = load_config(default_rules_path)
    
    if show_slug:
        show_rules_path = os.path.join(base_dir, f'{show_slug}.rules.yaml')
        show_rules_data = load_config(show_rules_path)
        
        # Simple merge: show-specific rules override default rules
        merged_rules_data = default_rules_data.copy()
        for key, value in show_rules_data.items():
            if isinstance(value, list) and key in merged_rules_data and isinstance(merged_rules_data[key], list):
                merged_rules_data[key] = list(set(merged_rules_data[key] + value)) # Merge lists, remove duplicates
            elif isinstance(value, dict) and key in merged_rules_data and isinstance(merged_rules_data[key], dict):
                merged_rules_data[key].update(value) # Update dictionaries
            else:
                merged_rules_data[key] = value # Override other types
        return ShowRules(**merged_rules_data)
    
    return ShowRules(**default_rules_data)

def save_show_rules(show_slug: str, backlog_strategy: str, last_n_episodes_count: int, aggressiveness: str):
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'shows')
    show_rules_path = os.path.join(base_dir, f'{show_slug}.rules.yaml')

    # Load existing rules if any, otherwise start with an empty dict
    current_rules = load_config(show_rules_path)

    # Update the specific fields
    if 'backlog_processing' not in current_rules:
        current_rules['backlog_processing'] = {}
    current_rules['backlog_processing']['strategy'] = backlog_strategy
    current_rules['backlog_processing']['last_n_episodes_count'] = last_n_episodes_count
    current_rules['aggressiveness'] = aggressiveness

    with open(show_rules_path, 'w') as f:
        yaml.safe_dump(current_rules, f, sort_keys=False)
    logger.info(f"Saved settings for show {show_slug} to {show_rules_path}")

def load_app_config() -> AppConfig:
    """
    Loads the main application configuration.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'app.yaml')
    app_config_data = load_config(config_path)
    env_config_data = load_env_config()
    
    # Environment variables override app.yaml settings
    app_config_data.update(env_config_data)

    # Handle nested Pydantic models
    detector_data = app_config_data.pop('detector', {})
    encoding_data = app_config_data.pop('encoding', {})
    retention_policy_data = app_config_data.pop('retention_policy', {})
    backlog_processing_data = app_config_data.pop('backlog_processing', {})

    # Create Pydantic models
    app_config_data['detector'] = DetectorConfig(**detector_data)
    app_config_data['encoding'] = EncodingConfig(**encoding_data)
    app_config_data['retention_policy'] = RetentionPolicyConfig(**retention_policy_data)
    app_config_data['backlog_processing'] = BacklogProcessingConfig(**backlog_processing_data)

    # Ensure PODCLEAN_MEDIA_BASE_PATH has a default value if not set
    if 'PODCLEAN_MEDIA_BASE_PATH' not in app_config_data:
        app_config_data['PODCLEAN_MEDIA_BASE_PATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

    return AppConfig(**app_config_data)

def _get_app_config_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'app.yaml')

def add_feed_to_config(feed_url: str):
    config_path = _get_app_config_path()
    with open(config_path, 'r+') as f:
        config = yaml.safe_load(f)
        if 'feeds' not in config or config['feeds'] is None:
            config['feeds'] = []
        if feed_url not in config['feeds']:
            config['feeds'].append(feed_url)
            f.seek(0) # Rewind to the beginning of the file
            yaml.safe_dump(config, f, sort_keys=False)
            f.truncate() # Truncate any remaining old content
            logger.info(f"Added feed: {feed_url} to app.yaml")
        else:
            logger.warning(f"Feed already exists in app.yaml: {feed_url}")

def remove_feed_from_config(feed_url: str):
    config_path = _get_app_config_path()
    with open(config_path, 'r+') as f:
        config = yaml.safe_load(f)
        if 'feeds' in config and config['feeds'] is not None and feed_url in config['feeds']:
            config['feeds'].remove(feed_url)
            f.seek(0) # Rewind to the beginning of the file
            yaml.safe_dump(config, f, sort_keys=False)
            f.truncate() # Truncate any remaining old content
            logger.info(f"Removed feed: {feed_url} from app.yaml")
        else:
            logger.warning(f"Feed not found in app.yaml: {feed_url}")

if __name__ == "__main__":
    # Example Usage
    print("Loading app config:")
    app_cfg = load_app_config()
    print(app_cfg)

    print("\nLoading default show rules:")
    default_show_cfg = load_show_rules()
    print(default_show_cfg)

    # Create a dummy show-specific rule file for testing
    dummy_show_rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'shows', 'test_show.rules.yaml')
    with open(dummy_show_rules_path, 'w') as f:
        f.write("phrases:\n  - \"test phrase\"\nurl_patterns:\n  - \"test.com\"\naggressiveness: aggressive\n")

    print("\nLoading show rules for 'test_show':")
    test_show_cfg = load_show_rules(show_slug="test_show")
    print(test_show_cfg)

    # Clean up dummy file
    os.remove(dummy_show_rules_path)

    # Test add/remove feed
    test_feed_url = "http://example.com/test_feed.xml"
    print(f"\nAdding test feed: {test_feed_url}")
    add_feed_to_config(test_feed_url)
    app_cfg_after_add = load_app_config()
    print(f"Feeds after add: {app_cfg_after_add.feeds}")

    print(f"\nRemoving test feed: {test_feed_url}")
    remove_feed_from_config(test_feed_url)
    app_cfg_after_remove = load_app_config()
    print(f"Feeds after remove: {app_cfg_after_remove.feeds}")
