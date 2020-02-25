import yaml
import os
from . import constants


class Config:
    def __init__(self, config_path):
        config_path = config_path or self._get_default_config_path()
        if config_path:
            self.config = yaml.load(open(config_path, encoding="UTF-8").read())
        else:
            self.config = {}

    def get_profile(self, profile_name):
        if not self.config and profile_name is None:
            return {}
        profile_name = profile_name or constants.DEFAULT_PROFILE
        profile = self.config.get(profile_name)
        if profile is None:
            raise RuntimeError(f"not exists profile => [{profile_name}]")
        return profile

    def _get_default_config_path(self):
        for config_path in constants.DEFAULT_CONFIGS:
            if os.path.exists(config_path):
                return config_path
        return None
