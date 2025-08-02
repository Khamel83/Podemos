import yaml
import os
from src.config.config import AppConfig, ShowRules, DetectorConfig, EncodingConfig

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

    # Create Pydantic models
    app_config_data['detector'] = DetectorConfig(**detector_data)
    app_config_data['encoding'] = EncodingConfig(**encoding_data)

    # Ensure PODCLEAN_MEDIA_BASE_PATH has a default value if not set
    if 'PODCLEAN_MEDIA_BASE_PATH' not in app_config_data:
        app_config_data['PODCLEAN_MEDIA_BASE_PATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))

    return AppConfig(**app_config_data)

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