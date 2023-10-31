import os
from configparser import ConfigParser
from pathlib import Path
from typing import Any, Optional

import toml

from src.log import log


class Config:
    parser: ConfigParser

    def __init__(self, config_path: Optional[str] = None):
        self.parser = ConfigParser(
            default_section="app", strict=False, interpolation=None
        )
        self.parser.read(
            config_path
            if config_path
            else os.path.join(os.path.dirname(__file__), "../app.cfg")
        )
        # os.environ can have case-insensitive duplicates
        env_dict = {}
        for k, v in dict(os.environ).items():
           if k.upper() in env_dict.keys():
               continue
           env_dict[k.upper()] = v

        self.parser.read_dict({self.parser.default_section: env_dict})
        self.parser.read_dict({self.parser.default_section: os.environ})

        if "H2O_CLOUD_ENVIRONMENT" in os.environ:
            self.is_cloud = True
        else:
            self.is_cloud = False
        if self.is_cloud:
            self.domain_url = (
                "https://"
                + os.environ.get("H2O_CLOUD_INSTANCE_ID")
                + "."
                + os.environ.get("H2O_CLOUD_ENVIRONMENT").split("/")[-1]
            )
        else:
            self.domain_url = "http://" + "localhost:10101"

    def get(self, key: str, default: Any = None) -> Optional[str]:
        return self.parser.get(self.parser.default_section, key, fallback=default)

    @property
    def local_data_folder(self):
        return self.get_local_data_folder()

    @property
    def cloud_data_folder(self):
        return self.get_cloud_data_folder()

    def get_local_data_folder(self, default: Any = None) -> Optional[str]:
        return self.get_data_folder(default=default, local=True)

    def get_cloud_data_folder(self, default: Any = None) -> Optional[str]:
        return self.get_data_folder(default=default, cloud=True)

    def get_data_folder(
        self,
        default: Any = None,
        **kwargs,
    ) -> Optional[str]:
        local = kwargs.get("local", False)
        cloud = kwargs.get("cloud", False)
        key = "DATA_FOLDER"
        folder = Path(
            self.parser.get(self.parser.default_section, key, fallback=default)
        )
        if (self.is_cloud or cloud) and not local:
            volume_mount = Path(
                toml.load(self.get("APP_TOML_PATH"))["Runtime"]["VolumeMount"]
            )
            folder = volume_mount / folder
        if not folder.exists():
            try:
                folder.mkdir()
            except Exception as e:
                log.error(e)
        return str(folder) + "/"

    def get_local_folder(self, key: str, default: Any = None) -> Optional[str]:
        return self.get_folder(key=key, default=default, local=True)

    def get_cloud_folder(self, key: str, default: Any = None) -> Optional[str]:
        return self.get_folder(key=key, default=default, cloud=True)

    def get_folder(self, key: str, default: Any = None, **kwargs) -> Optional[str]:
        data_folder = self.get_data_folder(**kwargs)
        folder_key_postfix = "_FOLDER"
        if not key.endswith(folder_key_postfix):
            key += folder_key_postfix
        if key == "DATA_FOLDER":
            return data_folder
        if key == "STATIC_FOLDER":
            return self.parser.get(self.parser.default_section, key, fallback=default)

        folder = Path(data_folder) / Path(
            self.parser.get(self.parser.default_section, key, fallback=default)
        )
        if not folder.exists():
            try:
                folder.mkdir()
            except Exception as e:
                log.error(e)
        return str(folder) + "/"

    def getboolean(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        return self.parser.getboolean(
            self.parser.default_section, key, fallback=default
        )

    def getint(self, key: str, default: Optional[int] = None) -> Optional[int]:
        return self.parser.getint(self.parser.default_section, key, fallback=default)

    def getfloat(self, key: str, default: Optional[float] = None) -> Optional[float]:
        return self.parser.getfloat(self.parser.default_section, key, fallback=default)

    def check_cloud(self):
        return self.is_cloud

    def get_url(self):
        return self.domain_url
