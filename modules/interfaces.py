from pydantic import BaseModel
from typing import Any, Dict, Optional, Literal

from utils.networks import *


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
        min_operation_amount: float - минимальная сумма для операции
        max_operation_amount: float - максимальная сумма для операции
        min_balance_save: float - минимальный остаток на счете после операции
        max_balance_save: float - максимальный остаток на счете после операции
        count_of_operations: int - количество успешных действий в модуле
    
    """
    module_name: str = "BaseModule"
    module_display_name: str = "BaseModule"
    module_priority: int = 0
    module_type: MODULE_TYPES = "base"
    min_operation_amount: float = 0.0035
    max_operation_amount: float = 0.01
    min_balance_save: float = 0.0
    max_balance_save: float = 0.15
    count_of_operations: int = 0


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

class BridgeOwltoOPtoInkModule(BridgeModuleInfo):
    """ Bridge Owlto module from OP to Ink  """
    source_network: str = OP.name
    destination_network: str = Ink.name
    source_network_chain_id: int = OP.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto_op_to_ink"
    module_display_name: str = "Bridge Owlto OP to Ink"

class BridgeOwltoBasetoInkModule(BridgeModuleInfo):
    """ Bridge Owlto module from Base to Ink  """
    source_network: str = Base.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Base.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto_base_to_ink"
    module_display_name: str = "Bridge Owlto Base to Ink"

class BridgeOwltoInktoOPModule(BridgeModuleInfo):
    """ Bridge Owlto module from Ink to OP """
    fee: float = 0.00065
    source_network: str = Ink.name
    destination_network: str = OP.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = OP.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto_ink_to_op"
    module_display_name: str = "Bridge Owlto Ink to OP"

class BridgeOwltoInktoBaseModule(BridgeModuleInfo):
    """ Bridge Owlto module from Ink to Base """
    fee: float = 0.00065
    source_network: str = Ink.name
    destination_network: str = Base.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = Base.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto_ink_to_base"
    module_display_name: str = "Bridge Owlto Ink to Base"