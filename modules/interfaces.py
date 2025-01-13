from dataclasses import dataclass
from decimal import Decimal

from modules import Logger


@dataclass
class BaseModuleInfo:
    name: str
    display_name: str
    priority: int = 0
    module_type: str = "base"


@dataclass
class BridgeModuleInfo(BaseModuleInfo, Logger):
   # сделать некоторые поля необязательными
    source_network: str | None
    destination_network: str | None
    min_amount: Decimal | 0.01
    max_amount: Decimal | 0.02
    module_type: str = "bridge" | None
