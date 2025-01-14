from pydantic import BaseModel
from typing import Any, Dict, Optional, Literal

from utils.networks import Ethereum, Ink


MODULE_TYPES = Literal[
    "swap",
    "bridge",
    "add_liquidity",
    "remove_liquidity"
]

class BaseModuleInfo(BaseModel):
    """
    Base module info class for all modules
    
    Attributes:
        module_name: str - имя модуля
        module_display_name: str - отображаемое имя модуля (для вывода в консоль и Telegram)
        module_priority: int - приоритет модуля
        module_type: MODULE_TYPES - тип модуля
    
    """
    module_name: str = "BaseModule"
    module_display_name: str = "BaseModule"
    module_priority: int = 0
    module_type: MODULE_TYPES = "base"


class BridgeModuleInfo(BaseModuleInfo):
    """
    Bridge module info class for all bridge modules

    Attributes:
        fee: float - 0.005 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "bridge" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0005
    min_available_balance: float = 0.008
    min_amount_residue: float = 0.005
    min_amount_out: float = 0.002
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: str = None
    module_type: str = "bridge"


class BridgeNativeModule(BridgeModuleInfo):
    """ Bridge native module info class for bridge native tokens from Ethereum to Ink """
    source_network: str = Ethereum.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Ethereum.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 1
    module_name: str = "bridge_native"
    module_display_name: str = "Bridge Native"

class BridgeOwltoModule(BridgeModuleInfo):
    """ Bridge Owlto module from Ethereum to Ink  """
    source_network: str = Ethereum.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Ethereum.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto"
    module_display_name: str = "Bridge Owlto"

class BridgeGGModule(BridgeModuleInfo):
    """ Bridge GG module from Ethereum to Ink """
    source_network: str = Ethereum.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Ethereum.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 3
    module_name: str = "bridge_gg"
    module_display_name: str = "Bridge GG"
