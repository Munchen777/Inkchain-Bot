from better_proxy import Proxy
from pathlib import Path
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    ValidationError
)
from typing import Any, Dict, List

from core.exceptions import ConfigurationError
from logger import log


class Account:
    __slots__ = (
        "private_key",
        "proxy",
        "auth_tokens_twitter",
        "auth_tokens_discord",
        "telegram_session",
    )

    def __init__(
        self,
        private_key: str,
        proxy: Proxy | None = None,
        # auth_tokens_twitter: str | None = None,
        # auth_tokens_discord: str | None = None,
        # telegram_session: Path | None = None,
    ) -> None:
        self.private_key: str = private_key
        self.proxy: Proxy | None = proxy
        # self.auth_tokens_twitter: str | None = auth_tokens_twitter
        # self.auth_tokens_discord: str | None = auth_tokens_discord
        # self.telegram_session: Path | None = telegram_session


class DelayRange(BaseModel):
    min: int
    max: int

    @field_validator('max')
    @classmethod
    def validate_max(cls, value: int, info: ValidationInfo) -> int:
        if value < info.data['min']:
            raise ConfigurationError('max must be greater than or equal to min')
        return value

    model_config = ConfigDict(frozen=True)


class PersentRange(BaseModel):
    min: int
    max: int

    @field_validator('max')
    @classmethod
    def validate_max(cls, value: int, info: ValidationInfo) -> int:
        if value < info.data['min']:
            raise ConfigurationError('max must be greater than or equal to min')
        return value


class AmountRange(BaseModel):
    min: float | int
    max: float | int

    @field_validator('max')
    @classmethod
    def validate_max(cls, value: int, info: ValidationInfo) -> int:
        if value < info.data['min']:
            raise ConfigurationError('max must be greater than or equal to min')
        return value


class ModuleConfig(BaseModel):
    percent_range: PersentRange | None = None
    save_amount: AmountRange | None = None
    save_range: PersentRange | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )

    def get(self, key, default=None) -> Any | None:
        return getattr(self, key, default)


class Config(BaseModel):
    accounts: List[Account] = Field(default_factory=list)
    threads: int
    delay_before_start: DelayRange
    delay_between_tasks: DelayRange
    shuffle_flag: bool = False
    module: str = ""

    percent_range: PersentRange | None = None
    save_amount: AmountRange | None = None
    save_range: PersentRange | None = None

    modules_settings: Dict[str, ModuleConfig] = Field(default_factory=dict)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='allow',
    )

    async def _get_module_settings(self, module_name: str) -> ModuleConfig:
        try:
            module_settings: ModuleConfig | None = self.modules_settings.get(module_name, None)
            if not module_settings:

                percent_range: PersentRange | None = None
                save_amount: AmountRange | None = None
                save_range: PersentRange | None = None

                if self.percent_range:
                    percent_range: PersentRange = PersentRange(**self.percent_range.model_dump())

                if self.save_amount:
                    save_amount: AmountRange = AmountRange(**self.save_amount.model_dump())

                if self.save_range:
                    save_range: PersentRange = PersentRange(**self.save_range.model_dump())

                module_config: ModuleConfig = ModuleConfig(
                    percent_range=percent_range,
                    save_amount=save_amount,
                    save_range=save_range,
                )
                self.modules_settings: Dict[str, ModuleConfig] = {
                    module_name: module_config,
                }

            return self.modules_settings.get(module_name)

        except ValidationError as error:
            log.error(f"{error}", exc_info=True)
            raise error
