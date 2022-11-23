import os

from easydict import EasyDict
from configparser import ConfigParser


__all__ = ['cfg', 'translate']


class ConfigManager(ConfigParser):
    def __init__(self, config_file=None):
        super().__init__()
        self.config_file = config_file
        self.read(config_file)

    def reload(self):
        self.read(self.config_file)

    def to_easydict(self):
        return EasyDict({s:dict(self.items(s)) for s in self.sections()})

    def update_cfg(self, settings: dict):
        ret_msg = {'info': []}
        if 'endpoint' in settings:
            raw_endpoint = settings['endpoint']
            endpoint = raw_endpoint.replace('-', '_')
            for raw_param, value in settings.items():
                param = raw_param.replace('-', '_')
                if self.get(endpoint, param):
                    self.set(endpoint, param, value)
                    ret_msg['info'].append(f'Endpoint `{raw_endpoint}` - changed `{raw_param}` to `{value}`.')
                else:
                    ret_msg['info'].append(f'Endpoint `{raw_endpoint}` has no param named `{raw_param}`.')
            ret_msg['info'] = '\n'.join(ret_msg['info'])
        else:
            ret_msg['info'] = 'You must specify an endpoint. e.g endpoint=face-verification. ' \
                'Available endpoints: face-verification, face-recognition, face-detection'
        return ret_msg

    def save(self):
        if self.config_file is not None:
            with open(self.config_file, 'w') as f:
                self.write(f)


def translate(cfg: ConfigManager, name: str):
    return cfg['translation'][name]


def load_config(config_file: str ='dev.cfg'):
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
        config = ConfigManager(config_file)
    return config


env = os.getenv('STAGE', 'dev')
config_dir = os.path.abspath(os.path.dirname(__file__))
config_file = 'prod.cfg' if env == 'prod' else 'dev.cfg'
config_path = os.path.join(config_dir, config_file)
cfg = load_config(config_path)