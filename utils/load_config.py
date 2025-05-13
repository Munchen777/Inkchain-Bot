import yaml
import os
import random

from better_proxy import Proxy
from dataclasses import dataclass
from itertools import cycle
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import Any, Dict, Generator, List

from core.exceptions import ConfigurationError
from models import Account, Config
from logger import log


@dataclass
class FileData:
    path: Path
    required: bool = True
    allow_empty: bool = False


class ConfigLoader:
    def __init__(self, base_path: str | Path | None = None) -> None:
        self.base_path: Path = Path(base_path or Path(__file__).parent.parent)
        self.config_path: Path = self.base_path / "config"
        self.data_client_path: Path = self.config_path / "data" / "client"
        self.settings_path: Path = self.config_path / "settings.yaml"
        self.file_path: Dict[str, FileData] = {
            "private_keys": FileData(
                self.data_client_path / "private_keys.txt"
            ),
            "proxies": FileData(
                self.data_client_path / "proxies.txt",
            ),
        }

    def _read_file(self, file_data: FileData) -> List[str] | None:
        try:
            if not file_data.path.exists():
                if file_data.required:
                    raise ConfigurationError(
                        f"Required file not found: {file_data.path}"
                    )
                return []

            content: str = file_data.path.read_text(encoding="utf-8").strip()

            if not content and not file_data.allow_empty and file_data.required:
                raise ConfigurationError(
                    f"Required file is empty: {file_data.path}"
                )

            return [
                row.strip()
                for row in content.splitlines()
                if row.strip()
            ]

        except Exception as error:
            if file_data.required:
                raise ConfigurationError(
                    f"Error reading {file_data.path}: {error}"
                )
            log.warning(
                f"Non-critical error reading {file_data.path}: {error}"
            )
            return []

    def _load_yaml(self) -> Dict:
        try:
            with open(self.settings_path, "r", encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.SafeLoader)

            if not isinstance(config, dict):
                raise ConfigurationError(
                    f"Configuration must be a dictionary"
                )

            if "delay_between_tasks" not in config:
                config["delay_between_tasks"] = {
                    "min": 30,
                    "max": 120,
                }

            return config

        except Exception as error:
            raise ConfigurationError(
                f"Error loading configuration: {error}"
            )

    def _parse_proxies(self) -> list[Proxy]:
        proxy_lines = self._read_file(self.file_path['proxies'])

        def validate_proxy(proxy_str: str) -> Proxy | None:
            try: 
                return Proxy.from_str(proxy_str)
            except ValueError:
                return None

        with ThreadPool(processes=os.cpu_count()) as pool:
            results = list(pool.map(validate_proxy, proxy_lines))

        return [
            proxy
            for proxy in results
            if proxy is not None
        ]

    def _get_accounts(self) -> Generator[Account, None, None]:
        proxies: List[Proxy] = self._parse_proxies()
        proxy_cycle = cycle(proxies) if proxies else None

        with ThreadPool(processes=os.cpu_count()) as pool:
            private_keys = pool.apply(
                self._read_file,
                [
                    self.file_path["private_keys"],
                ]
            )

        for index, private_key in enumerate(private_keys):
            try:
                yield Account(
                    private_key=private_key,
                    proxy=next(proxy_cycle) if proxy_cycle else None,
                )

            except Exception as error:
                log.error(
                    f"Failed to create account for {private_key} private key: {error}"
                )

    def load(self) -> Config:
        try:
            config: Dict[str, Any] = self._load_yaml()
            accounts: List[Account] = list(self._get_accounts())

            if not accounts:
                raise ConfigurationError(
                    f"No valid accounts found"
                )

            if config.get("shuffle_flag"):
                random.shuffle(accounts)

            return Config(accounts=accounts, **config)

        except ConfigurationError as error:
            log.error(f"Configuration error: {error}")
            exit(1)

        except Exception as error:
            log.error(f"Unexpected error during configuration loading: {error}")
            exit(1)


def load_config() -> Config:
    return ConfigLoader().load()
