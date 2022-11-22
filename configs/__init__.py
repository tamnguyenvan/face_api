import os
import yaml
from easydict import EasyDict


def load_config(config_file: str ='dev.yml') -> EasyDict:
    """Load config from given config file.

    Parameters
    ----------
    config_file : str, optional
        Config file.

    Returns
    -------
    EasyDict
        Config object
    """
    with open(config_file) as f:
        config = EasyDict(yaml.safe_load(f))
    return config


env = os.getenv('STAGE', 'dev')
config_dir = os.path.abspath(os.path.dirname(__file__))
config_file = 'prod.yml' if env == 'prod' else 'dev.yml'
config_path = os.path.join(config_dir, config_file)
cfg = load_config(config_path)