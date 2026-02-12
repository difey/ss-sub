import json
import os
from typing import List, Optional
from pathlib import Path
from src.models.subscription import Subscription

DATA_DIR = Path("data")

class StorageService:
    def __init__(self):
        # Create data directory if not exists
        if not DATA_DIR.exists():
            DATA_DIR.mkdir(parents=True)
            
        self.subs_file = DATA_DIR / "subscriptions.json"
        self.merged_file = DATA_DIR / "merged.yaml"
        self.custom_rules_file = DATA_DIR / "custom_rules.txt"
        
        # Initialize empty subs file if not exists
        if not self.subs_file.exists():
            with open(self.subs_file, "w") as f:
                json.dump([], f)

    def get_all_subscriptions(self) -> List[Subscription]:
        with open(self.subs_file, "r") as f:
            data = json.load(f)
            return [Subscription(**item) for item in data]

    def add_subscription(self, sub: Subscription):
        subs = self.get_all_subscriptions()
        subs.append(sub)
        self._save_subscriptions(subs)

    def remove_subscription(self, sub_id: str):
        subs = self.get_all_subscriptions()
        subs = [s for s in subs if s.id != sub_id]
        self._save_subscriptions(subs)

    def _save_subscriptions(self, subs: List[Subscription]):
        data = [sub.dict() for sub in subs]
        with open(self.subs_file, "w") as f:
            json.dump(data, f, indent=2)

    def save_merged_config(self, content: str):
        self.merged_file.write_text(content, encoding="utf-8")

    def get_merged_config(self) -> str:
        if self.merged_file.exists():
            return self.merged_file.read_text(encoding="utf-8")
        return ""
        
    def save_custom_rules(self, new_rules_text: str):
        """
        Upsert custom rules. New rules overwrite existing ones if Type+Value match.
        """
        existing_text = self.get_custom_rules()
        existing_rules = [r.strip() for r in existing_text.splitlines() if r.strip()]
        
        # Helper to get key
        def get_key(rule):
            parts = rule.split(',')
            if not parts: return rule
            rule_type = parts[0].strip().upper()
            if rule_type == 'MATCH':
                return 'MATCH'
            elif len(parts) >= 2:
                return f"{rule_type},{parts[1].strip()}"
            return rule

        # Build map of Key -> Rule (preserve order for existing)
        rule_map = {}
        ordered_keys = []
        
        for rule in existing_rules:
            key = get_key(rule)
            if key not in rule_map:
                ordered_keys.append(key)
            rule_map[key] = rule
            
        # Process new rules
        new_rules = [r.strip() for r in new_rules_text.splitlines() if r.strip()]
        for rule in new_rules:
            key = get_key(rule)
            if key not in rule_map:
                ordered_keys.append(key)
            rule_map[key] = rule # Overwrite
            
        # Reconstruct content
        final_rules = [rule_map[key] for key in ordered_keys]
        self.custom_rules_file.write_text("\n".join(final_rules), encoding="utf-8")
        
    def get_custom_rules(self) -> str:
        if self.custom_rules_file.exists():
            return self.custom_rules_file.read_text(encoding="utf-8")
        return ""

storage_service = StorageService()
