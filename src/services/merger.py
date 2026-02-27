from typing import List, Dict, Any, Tuple
import logging
import yaml

logger = logging.getLogger(__name__)

def safe_load_yaml(content: str) -> Dict[str, Any]:
    try:
        return yaml.safe_load(content) or {}
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML: {e}")
        return {}

def merge_clash_configs(configs: List[Tuple[str, str]], custom_rules: List[str] = None) -> str:
    """
    Merge multiple Clash configurations.
    configs: List of (content, prefix_name)
    custom_rules: Optional list of custom rules strings
    """
    if not configs:
        return yaml.dump({}, allow_unicode=True)

    # Use the first config as the base
    base_content, base_name = configs[0]
    base_config = safe_load_yaml(base_content)
    
    # Helper to apply prefix
    def apply_prefix(name: str, prefix: str) -> str:
        if name in ["DIRECT", "REJECT", "GLOBAL", "Final"] or name.startswith("Expire:") or name.startswith("Traffic:"):
            return name
        return f"{prefix}_{name}"

    # Initialize collections
    all_proxies = []
    all_groups = []
    all_rules = []
    
    existing_proxy_names = set()
    existing_group_names = set()

    # Pre-process custom rules if any
    if custom_rules:
        for r in custom_rules:
            if r.strip():
                all_rules.append(r.strip())

    for content, prefix in configs:
        config = safe_load_yaml(content)
        
        # 1. Merge Proxies
        current_sub_proxies = []
        proxies = config.get("proxies", []) or []
        for proxy in proxies:
            name = proxy.get("name")
            if not name: continue
            
            # Apply prefix
            prefixed_name = apply_prefix(name, prefix)
            
            # Deduplication
            original_prefixed = prefixed_name
            counter = 1
            while prefixed_name in existing_proxy_names:
                prefixed_name = f"{original_prefixed}_{counter}"
                counter += 1
            
            proxy["name"] = prefixed_name
            existing_proxy_names.add(prefixed_name)
            all_proxies.append(proxy)
            current_sub_proxies.append(prefixed_name)

        # 2. Merge Proxy Groups
        groups = config.get("proxy-groups", []) or []
        for group in groups:
            original_name = group.get("name")
            if not original_name: continue
            
            # Prefix group name
            prefixed_group_name = apply_prefix(original_name, prefix)
            
            # Prefix member proxies
            # Only prefix if member is NOT a reserved keyword (DIRECT, REJECT, etc)
            # AND if it was likely a proxy from THIS subscription.
            # But wait, if a group refers to another group, we should prefix that too?
            # Yes, usually groups refer to proxies or other groups within the same file.
            # So applying prefix to all members (except keywords) is correct.
            members = group.get("proxies", []) or []
            new_members = []
            for m in members:
                new_members.append(apply_prefix(m, prefix))
            
            group["name"] = prefixed_group_name
            group["proxies"] = new_members
            
            # Deduplication for groups
            if prefixed_group_name not in existing_group_names:
                all_groups.append(group)
                existing_group_names.add(prefixed_group_name)

        # 3. Merge Rules
        rules = config.get("rules", []) or []
        for r in rules:
            parts = r.split(',')
            if len(parts) >= 3:
                # Check for no-resolve which appears at the end of IP-CIDR/IP-CIDR6
                if parts[-1].strip() == 'no-resolve':
                    # Target is the second to last element
                    target = parts[-2]
                    parts[-2] = apply_prefix(target, prefix)
                else:
                    target = parts[-1]
                    parts[-1] = apply_prefix(target, prefix)
                all_rules.append(','.join(parts))
            else:
                all_rules.append(r)

    # Deduplicate rules based on key (Type + Value)
    unique_rules = []
    seen_keys = set()
    
    for rule in all_rules:
        parts = rule.split(',')
        if not parts: continue
        
        rule_type = parts[0].strip().upper()
        if rule_type == 'MATCH':
            key = 'MATCH'
        elif len(parts) >= 2:
            key = f"{rule_type},{parts[1].strip()}"
        else:
            key = rule # Fallback for unknown formats
            
        if key not in seen_keys:
            unique_rules.append(rule)
            seen_keys.add(key)

    # Update the base config with merged data
    # We use base_config for global settings, but override structure
    base_config["proxies"] = all_proxies
    base_config["proxy-groups"] = all_groups
    base_config["rules"] = unique_rules

    return yaml.dump(base_config, allow_unicode=True, sort_keys=False)
