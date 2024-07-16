import os
import yaml

CONFIG_FILE_PATH = os.path.join(os.path.expanduser("~"), ".config", "pm", "config.yml")


class Config:
    provider: str = None
    max_changes: int = 500
    max_chars: int = 50
    github_token: str = ""
    openai: str = None

    def set_option(self, option: str, value: str):
        """
        Helper function to set configuration options
        """
        self.read_config()
        setattr(Config, option, value)
        self.write_config()

    def get_option(self, option: str):
        """
        Helper function to get configuration option
        """
        self.read_config()
        return getattr(Config, option)

    def get_options(self):
        """
        Helper function to get all configuration options
        """
        return {
            k: v
            for k, v in vars(Config).items()
            if not k.startswith("__") and not callable(v)
        }

    def check_config(self):
        """
        Check if configuration file exists
        """
        return os.path.exists(CONFIG_FILE_PATH)

    def write_config(self, path: str = CONFIG_FILE_PATH):
        """
        Write configuration to file
        """
        config_dir = os.path.dirname(CONFIG_FILE_PATH)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        config_data = self.get_options()
        with open(path, "w") as file:
            yaml.dump(config_data, file)

    def read_config(self, path: str = CONFIG_FILE_PATH):
        """
        Read configuration from file
        """
        if not self.check_config():
            self.write_config()
        with open(path, "r") as file:
            config_data = yaml.safe_load(file)
            for k, v in config_data.items():
                setattr(Config, k, v)
