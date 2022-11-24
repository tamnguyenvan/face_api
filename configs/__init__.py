import os
import json

from easydict import EasyDict
# from configparser import ConfigParser


__all__ = ['cfg', 'translate']


class ConfigManager:
    def __init__(self, config_file=None):
        super().__init__()
        self.config_file = config_file
        self.cfg = self.reload()
        # self.cfg_translator = ConfigTranslator(self.cfg)
        self.ignore_params = ('save', 'endpoint')

    def __getitem__(self, key):
        return self.cfg[key]

    def reload(self):
        with open(self.config_file) as f:
            return json.load(f)

    def _get_available_params(self, endpoint):
        return tuple(self.cfg['endpoints'][endpoint].keys())

    def _get_available_values(self, endpoint, param):
        return tuple(self.cfg['options'][endpoint][param])

    def _validate_param_key(self, endpoint, param):
        return param in self._get_available_params(endpoint)

    def _validate_param_value(self, endpoint, param, value):
        return value in self._get_available_values(endpoint, param)

    def update_cfg(self, settings: dict):
        settings = dict(settings)
        ret_msg = {'info': []}
        if 'endpoint' in settings:
            endpoint_name = settings['endpoint']

            if endpoint_name in self.cfg['endpoints']:
                # settings = self.cfg_translator.translate_settings(settings)

                curr_endpoint_settings = self.cfg['endpoints'][endpoint_name]
                ret_msg['info'].append(f'Endpoint `{endpoint_name}`.')
                for param, value in settings.items():
                    if param in self.ignore_params:
                        continue

                    if not self._validate_param_key(endpoint_name, param):
                        av_params = self._get_available_params(endpoint_name)
                        av_params = ', '.join(map(str, av_params))
                        ret_msg['info'].append(f'Invalid param `{param}`. Available params: `{av_params}`.')
                        continue

                    if not self._validate_param_value(endpoint_name, param, value):
                        av_values = self._get_available_values(endpoint_name, param)
                        av_values = ', '.join(map(str, av_values))
                        ret_msg['info'].append(f'Invalid value `{value}` for param `{param}`. Available values: `{av_values}`.')
                        continue

                    curr_endpoint_settings[param] = value
                    ret_msg['info'].append(f'Set `{param}={value}`.')

                ret_msg['info'] = '\n'.join(ret_msg['info'])
            else:
                ret_msg['info'] = f'Not found endpoint `{endpoint_name}`'
        else:
            ret_msg['info'] = 'You must specify an endpoint. e.g endpoint=face-verification. ' \
                'Available endpoints: face-verification, face-recognition, face-detection'
        return ret_msg

    def save(self):
        if self.config_file is not None:
            with open(self.config_file, 'w') as f:
                json.dump(self.cfg, f, indent=4)

# class ConfigTranslator:
#     def __init__(self, cfg) -> None:
#         self.cfg = cfg

#     def _get_available_params(self, endpoint):
#         return tuple(self.cfg['endpoints'][endpoint].keys())

#     def _get_available_values(self, endpoint, param):
#         return tuple(self.cfg['options'][endpoint][param])

#     def translate_settings(self, settings):
#         new_settings = dict(settings)
#         endpoint = settings['endpoint']
#         for key, value in settings.items():
#             if (key in self._get_available_params(endpoint)
#                 and value in self._get_available_values(endpoint, key)
#                 and value in self.cfg['translation'][endpoint][key]):
#                 new_settings[key] = self.cfg['translation'][endpoint][key][value]
#         return new_settings


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
config_file = 'prod.json' if env == 'prod' else 'dev.json'
config_path = os.path.join(config_dir, config_file)
default_config_path = os.path.join(config_dir, 'default.json')
try:
    cfg = load_config(config_path)
except Exception as e:
    import traceback
    print('Failed when loading config file')
    cfg = load_config(default_config_path)
# cfg_translator = ConfigTranslator(cfg)