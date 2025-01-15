from pydantic import BaseModel
from typing import Any, Dict, Optional, Literal

from utils.networks import*


MODULE_TYPES = Literal[
    "swap",
    "bridge",
    "add_liquidity",
    "remove_liquidity"
]

class BaseModuleInfo(BaseModel):
    """ Base module info class for all modules"""
    module_name: str = "BaseModule"
    module_display_name: str = "BaseModule"
    module_priority: int = 0
    module_type: MODULE_TYPES = "base"


class BridgeModuleInfo(BaseModuleInfo):
    """ Bridge module info class for all bridge modules """
    min_amount: float = 0.01
    max_amount: float = 0.02
    source_network: Optional[str] = None
    destination_network: Optional[str] = None
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

class BridgeOwltoOPtoInkModule(BridgeModuleInfo):
    """ Bridge native Owlto module for bridging native tokens from OP to Ink """
    source_network: str = OP.name
    destination_network: str = Ink.name
    source_network_chain_id: int = OP.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 1
    module_name: str = "bridge_owlto_op_to_ink"
    module_display_name: str = "Bridge Owlto OP to Ink"
