import yaml
import os

def load_config(config_path: str) -> dict:
    """
    Loads a YAML configuration file.
    """
    if not os.path.exists(config_path):
        return {}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_show_rules(show_slug: str = None) -> dict:
    """
    Loads default and optionally show-specific rules, merging them.
    """
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'shows')
    default_rules_path = os.path.join(base_dir, 'default.rules.yaml')
    
default_rules = load_config(default_rules_path)
    
    if show_slug:
        show_rules_path = os.path.join(base_dir, f'{show_slug}.rules.yaml')
        show_rules = load_config(show_rules_path)
        
        # Simple merge: show-specific rules override default rules
        merged_rules = default_rules.copy()
        for key, value in show_rules.items():
            if isinstance(value, list) and key in merged_rules and isinstance(merged_rules[key], list):
                merged_rules[key] = list(set(merged_rules[key] + value)) # Merge lists, remove duplicates
            elif isinstance(value, dict) and key in merged_rules and isinstance(merged_rules[key], dict):
                merged_rules[key].update(value) # Update dictionaries
            else:
                merged_rules[key] = value # Override other types
        return merged_rules
    
    return default_rules

def load_app_config() -> dict:
    """
    Loads the main application configuration.
    """
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config', 'app.yaml')
    return load_config(config_path)

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
        f.write("phrases:\n  - \"test phrase\"\nurl_patterns:\n  - \"test.com\"
aggressiveness: aggressive\n")

    print("\nLoading show rules for 'test_show':")
    test_show_cfg = load_show_rules(show_slug="test_show")
    print(test_show_cfg)

    # Clean up dummy file
    os.remove(dummy_show_rules_path)
