from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List, Literal, Set

from utils.networks import *


MODULE_TYPES = Literal[
    "swap",
    "bridge",
    "add_liquidity",
    "remove_liquidity",
    "mint_nft",
    "deploy",
    "buy_domen"
]

class ModuleDependency(BaseModel):
    """ Module for describing dependencies between modules """
    required_modules: Set[str] = Field(
        default_factory=set,
        description="Имена модулей, которые должны быть выполнены до этого",
        exclude=True
    )


class RequiredModulesToExecute(BaseModel):
    required_modules: List[str] = Field(
        default=[
            "swap_inkswap_eth_to_sink",
            "bridge_gg_ethereum_to_ink",
            "swap_inkswap_sink_to_eth",
            "bridge_relay_op_to_ink",
            "bridge_relay_base_to_ink",
            "bridge_owlto_op_to_ink",
            "bridge_owlto_base_to_ink",
        ],
        description="Список модулей, которые должны быть обязательно выполнены",
    )


class BaseModuleInfo(BaseModel):
    """
    Base module info class for all modules
    
    Attributes:
        module_name: str - имя модуля
        module_display_name: str - отображаемое имя модуля (для вывода в консоль и Telegram)
        module_priority: int - приоритет модуля
        module_type: MODULE_TYPES - тип модуля
        count_of_operations: int - количество успешных действий в модуле
    
    """
    module_name: str = "BaseModule"
    module_display_name: str = "BaseModule"
    module_priority: int = 0
    module_type: MODULE_TYPES = "base"
    count_of_operations: int = 0

    required_on_first_run: bool = False
    
    # dependencies
    dependencies: ModuleDependency = Field(default_factory=ModuleDependency)


class BridgeModuleInfo(BaseModuleInfo):
    """
    Bridge module info class for all bridge modules

    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "bridge" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "bridge"

class BridgeOwltoOPtoInkModule(BridgeModuleInfo):
    """ Bridge Owlto module from OP to Ink  """
    fee: float = 0.0005
    source_network: str = OP.name
    destination_network: str = Ink.name
    source_network_chain_id: int = OP.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto_op_to_ink"
    module_display_name: str = "Bridge Owlto OP to Ink"

    dependencies: ModuleDependency = ModuleDependency(
        required_modules=set(),
    )

class BridgeOwltoBasetoInkModule(BridgeModuleInfo):
    """ Bridge Owlto module from Base to Ink  """
    fee: float = 0.0005
    source_network: str = Base.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Base.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "bridge_owlto_base_to_ink"
    module_display_name: str = "Bridge Owlto Base to Ink"

    dependencies: ModuleDependency = ModuleDependency(
        required_modules=set(),
    )

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
    
    dependencies: ModuleDependency = ModuleDependency(
        required_modules={
            "bridge_owlto_base_to_ink",
            "bridge_owlto_op_to_ink",
            "bridge_relay_op_to_ink",
            "bridge_relay_base_to_ink",
        }
    )

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

    dependencies: ModuleDependency = ModuleDependency(
        required_modules={
            "bridge_owlto_base_to_ink",
            "bridge_owlto_op_to_ink",
            "bridge_relay_op_to_ink",
            "bridge_relay_base_to_ink",
        }
    )

class BridgeRelayOPtoInkModule(BridgeModuleInfo):
    """ Bridge Relay module from OP to Ink  """
    source_network: str = OP.name
    destination_network: str = Ink.name
    source_network_chain_id: int = OP.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 1
    module_name: str = "bridge_relay_op_to_ink"
    module_display_name: str = "Bridge Relay OP to Ink"
    
    dependencies: ModuleDependency = ModuleDependency(
        required_modules=set(),
    )

class BridgeRelayBasetoInkModule(BridgeModuleInfo):
    """ Bridge Relay module from Base to Ink  """
    source_network: str = Base.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Base.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 1
    module_name: str = "bridge_relay_base_to_ink"
    module_display_name: str = "Bridge Relay Base to Ink"
    
    dependencies: ModuleDependency = ModuleDependency(
        required_modules=set(),
    )

class BridgeRelayInktoOPModule(BridgeModuleInfo):
    """ Bridge Relay module from Ink to OP  """
    source_network: str = Ink.name
    destination_network: str = OP.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = OP.chain_id
    module_priority: int = 1
    module_name: str = "bridge_relay_ink_to_op"
    module_display_name: str = "Bridge Relay Ink to OP"
    
    dependencies: ModuleDependency = ModuleDependency(
        required_modules={
            "bridge_owlto_base_to_ink",
            "bridge_owlto_op_to_ink",
            "bridge_relay_op_to_ink",
            "bridge_relay_base_to_ink",
        }
    )

class BridgeRelayInktoBaseModule(BridgeModuleInfo):
    """ Bridge Relay module from Ink to Base  """
    source_network: str = Ink.name
    destination_network: str = Base.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = Base.chain_id
    module_priority: int = 2
    module_name: str = "bridge_relay_ink_to_base"
    module_display_name: str = "Bridge Relay Ink to Base"

    dependencies: ModuleDependency = ModuleDependency(
        required_modules={
            "bridge_owlto_base_to_ink",
            "bridge_owlto_op_to_ink",
            "bridge_relay_op_to_ink",
            "bridge_relay_base_to_ink",
        }
    )

class BridgGGEthereumtoInkModule(BridgeModuleInfo):
    """ Bridge GG module from Ethereum to Ink  """
    min_available_balance: float = 0.01
    min_amount_residue: float = 0.005
    min_amount_out: float = 0.003
    max_amount_out: float = 0.005
    source_network: str = Ethereum.name
    destination_network: str = Ink.name
    source_network_chain_id: int = Ethereum.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "bridge_gg_ethereum_to_ink"
    module_display_name: str = "Bridge GG Ethereum to Ink"

    required_on_first_run: bool = True

    dependencies: ModuleDependency = ModuleDependency(
        required_modules=set(),
    )


class SwapModuleInfo(BaseModuleInfo):
    """
    Swap module info class for all bridge modules
    
    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "swap"
    
    dependencies: ModuleDependency = ModuleDependency(
        required_modules={
            "bridge_gg_ethereum_to_ink",
            "bridge_relay_base_to_ink",
            "bridge_relay_op_to_ink",
            "bridge_owlto_op_to_ink",
            "bridge_owlto_base_to_ink",
        }
    )

class SwapInkswapETHtoISWAPModule(SwapModuleInfo):
    """ Swap Inkswap module from ETH to ISWAP """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_eth_to_iswap"
    module_display_name: str = "Swap Inkswap ETH to ISWAP"
    
    dependencies: ModuleDependency = ModuleDependency()

class SwapInkswapETHtoSINKModule(SwapModuleInfo):
    """ Swap Inkswap module from ETH to SINK """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_eth_to_sink"
    module_display_name: str = "Swap Inkswap ETH to SINK"

class SwapInkswapETHtoKRAKENModule(SwapModuleInfo):
    """ Swap Inkswap module from ETH to KRAKEN """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_eth_to_kraken"
    module_display_name: str = "Swap Inkswap ETH to KRAKEN"

    dependencies: ModuleDependency = ModuleDependency()

class SwapInkswapISWAPtoETHModule(SwapModuleInfo):
    """ Swap Inkswap module from ISWAP to ETH """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_iswap_to_eth"
    module_display_name: str = "Swap Inkswap ISWAP to ETH"

    dependencies: ModuleDependency = ModuleDependency()

class SwapInkswapSINKtoETHModule(SwapModuleInfo):
    """ Swap Inkswap module from SINK to ETH """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_sink_to_eth"
    module_display_name: str = "Swap Inkswap SINK to ETH"

class SwapInkswapKRAKENtoETHModule(SwapModuleInfo):
    """ Swap Inkswap module from KRAKEN to ETH """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_kraken_to_eth"
    module_display_name: str = "Swap Inkswap KRAKEN to ETH"

    dependencies: ModuleDependency = ModuleDependency()

class SwapInkswapISWAPtoSINKModule(SwapModuleInfo):
    """ Swap Inkswap module from ISWAP to SINK """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_iswap_to_sink"
    module_display_name: str = "Swap Inkswap ISWAP to SINK"

    dependencies: ModuleDependency = ModuleDependency()

class SwapInkswapSINKtoISWAPModule(SwapModuleInfo):
    """ Swap Inkswap module from SINK to ISWAP """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_sink_to_iswap"
    module_display_name: str = "Swap Inkswap SINK to ISWAP"

class SwapInkswapSINKtoKRAKENModule(SwapModuleInfo):
    """ Swap Inkswap module from SINK to KRAKEN """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_sink_to_kraken"
    module_display_name: str = "Swap Inkswap SINK to KRAKEN"

class SwapInkswapKRAKENtoSINKModule(SwapModuleInfo):
    """ Swap Inkswap module from KRAKEN to SINK """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_kraken_to_sink"
    module_display_name: str = "Swap Inkswap KRAKEN to SINK"

class SwapInkswapKRAKENtoISWAPModule(SwapModuleInfo):
    """ Swap Inkswap module from KRAKEN to ISWAP """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_kraken_to_iswap"
    
class SwapInkswapISWAPtoKRAKENModule(SwapModuleInfo):
    """ Swap Inkswap module from ISWAP to KRAKEN """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_inkswap_iswap_to_kraken"
    module_display_name: str = "Swap Inkswap ISWAP to KRAKEN"

class SwapDyorETHtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to USDC.e  """
    min_amount_out: float = 0.00035
    max_amount_out: float = 0.001
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_eth_to_usdc"
    module_display_name: str = "Swap Dyor ETH to USDC.e"

class SwapDyorETHtoKrakenModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to Kraken  """
    min_amount_out: float = 0.00035
    max_amount_out: float = 0.001
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_eth_to_kraken"
    module_display_name: str = "Swap Dyor ETH to Kraken"

class SwapDyorETHtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to USDT  """
    min_amount_out: float = 0.00035
    max_amount_out: float = 0.001
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_eth_to_usdt"
    module_display_name: str = "Swap Dyor ETH to USDT"

class SwapDyorETHtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to WETH  """
    min_amount_out: float = 0.00035
    max_amount_out: float = 0.001
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_eth_to_weth"
    module_display_name: str = "Swap Dyor ETH to WETH"

class SwapDyorETHtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to WORM  """
    min_amount_out: float = 0.00035
    max_amount_out: float = 0.001
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_eth_to_worm"
    module_display_name: str = "Swap Dyor ETH to WORM"

class SwapDyorWETHtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to ETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_weth_to_eth"
    module_display_name: str = "Swap Dyor WETH to ETH"

class SwapDyorUSDCtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDC.e to ETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdc_to_eth"
    module_display_name: str = "Swap Dyor USDC.e to ETH"

class SwapDyorUSDTtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to ETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdt_to_eth"
    module_display_name: str = "Swap Dyor USDT to ETH"

class SwapDyorWORMtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to ETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_worm_to_eth"
    module_display_name: str = "Swap Dyor WORM to ETH"

class SwapDyorKRAKENtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to ETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_kraken_to_eth"
    module_display_name: str = "Swap Dyor KRAKEN to ETH"

class SwapDyorKRAKENtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to WORM  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_kraken_to_worm"
    module_display_name: str = "Swap Dyor KRAKEN to WORM"

class SwapDyorWORMtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to KRAKEN  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_worm_to_kraken"
    module_display_name: str = "Swap Dyor WORM to KRAKEN"

class SwapDyorWORMtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to USDT  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_worm_to_usdt"
    module_display_name: str = "Swap Dyor WORM to USDT"

class SwapDyorWORMtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to USDC  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_worm_to_usdc"
    module_display_name: str = "Swap Dyor WORM to USDC"

class SwapDyorWORMtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to WETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_worm_to_weth"
    module_display_name: str = "Swap Dyor WORM to WETH"

class SwapDyorKRAKENtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to WETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_kraken_to_weth"
    module_display_name: str = "Swap Dyor KRAKEN to WETH"

class SwapDyorKRAKENtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to USDC  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_kraken_to_usdc"
    module_display_name: str = "Swap Dyor KRAKEN to USDC"

class SwapDyorUSDCtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to KRAKEN  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdc_to_kraken"
    module_display_name: str = "Swap Dyor USDC to KRAKEN"

class SwapDyorUSDCtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to WORM  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdc_to_worm"
    module_display_name: str = "Swap Dyor USDC to WORM"

class SwapDyorUSDCtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to USDT  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdc_to_usdt"
    module_display_name: str = "Swap Dyor USDC to USDT"

class SwapDyorUSDCtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to WETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdc_to_weth"
    module_display_name: str = "Swap Dyor USDC to WETH"

class SwapDyorWETHtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to USDC  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_weth_to_usdc"
    module_display_name: str = "Swap Dyor WETH to USDC"

class SwapDyorWETHtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to USDT  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_weth_to_usdt"
    module_display_name: str = "Swap Dyor WETH to USDT"

class SwapDyorWETHtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to WORM  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_weth_to_worm"
    module_display_name: str = "Swap Dyor WETH to WORM"

class SwapDyorUSDTtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to WETH  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdt_to_weth"
    module_display_name: str = "Swap Dyor USDT to WETH"

class SwapDyorWETHtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to KRAKEN  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_weth_to_kraken"
    module_display_name: str = "Swap Dyor WETH to KRAKEN"

class SwapDyorUSDTtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to USDC  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdt_to_usdc"
    module_display_name: str = "Swap Dyor USDT to USDC"

class SwapDyorUSDTtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to WORM  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdt_to_worm"
    module_display_name: str = "Swap Dyor USDT to WORM"

class SwapDyorUSDTtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to KRAKEN  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_usdt_to_kraken"
    module_display_name: str = "Swap Dyor USDT to KRAKEN"

class SwapDyorKRAKENtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to USDT  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "swap_dyor_kraken_to_usdt"
    module_display_name: str = "Swap Dyor KRAKEN to USDT"


class AddLiquidityModuleInfo(BaseModuleInfo):
    """
    Add Liquidity module info class for all add liquidity modules
    
    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "add_liquidity"

class AddLiquidityDyorETHtoUSDCModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and USDC  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "add_liquidity_dyor_eth_and_usdc"
    module_display_name: str = "Add Liquidity Dyor ETH and USDC"

class AddLiquidityDyorETHtoUSDTModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and USDT  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "add_liquidity_dyor_eth_and_usdt"
    module_display_name: str = "Add Liquidity Dyor ETH and USDT"

class AddLiquidityDyorETHtoKRAKENModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and KRAKEN  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "add_liquidity_dyor_eth_and_kraken"
    module_display_name: str = "Add Liquidity Dyor ETH and KRAKEN"

class AddLiquidityDyorETHtoWORMModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and WORM  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "add_liquidity_dyor_eth_and_worm"
    module_display_name: str = "Add Liquidity Dyor ETH and WORM"


class MintNFTModuleInfo(BaseModuleInfo):
    """
    Mint NFT module info class for all mint nft modules
    
    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "mint_nft"

class MintNFTParagrafModule(MintNFTModuleInfo):
    """ Mint Paragraf NFT module  """
    source_network: str = OP.name
    source_network_chain_id: int = OP.chain_id
    module_priority: int = 2
    module_name: str = "mint_paragraf_nft"
    module_display_name: str = "Mint Paragraf NFT"

class MintNFTOGModule(MintNFTModuleInfo):
    """ Mint OG NFT module  """
    source_network: str = OP.name
    source_network_chain_id: int = OP.chain_id
    module_priority: int = 2
    module_name: str = "mint_og_nft"
    module_display_name: str = "Mint OG NFT"

class MintNFTGuildModule(MintNFTModuleInfo):
    """ Mint Guild NFT module  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "mint_guild_nft"
    module_display_name: str = "Mint Guild NFT"


class DeployContractModule(BaseModuleInfo):
    """
    Deployment of the contract module info class for all deployment contract modules
    
    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "deploy"

class DeployContractInkModule(DeployContractModule):
    """ Deployment of the contract in the Ink network """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "deploy_contract_ink_network"
    module_display_name: str = "Deployment of the contract in the Ink network"


class BuyZNCDomenModule(BaseModuleInfo):
    """
    Buy ZNC domen module info class for all buy ZNC domen modules
    
    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "buy_domen"

class BuyZNCDomenInkModule(BuyZNCDomenModule):
    """ Buy ZNC domen in the Ink network """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "buy_znc_domen_ink_network"
    module_display_name: str = "Buy ZNC domen in the Ink network"


class ClaimDailyGMModule(BaseModuleInfo):
    """
    Claim Daily module info class for all claim daily modules
    
    Attributes:
        fee: float - 0.0 комиссия за транзакцию (дефолтное значение)
        min_available_balance: float - минимальный доступный баланс для транзакции (дефолтное значение)
        min_amount_residue: float - минимальный остаток на счете после транзакции, который будет оставлен на счете (дефолтное значение)
        min_amount_out: float - минимальная сумма для вывода (дефолтное значение)
        max_amount_out: float - максимальная сумма для вывода (дефолтное значение)
        source_network: Optional[str] - сеть, с которой происходит транзакция (опциональное значение)
        destination_network: Optional[str] - сеть, на которую происходит транзакция (опциональное значение)
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    fee: float = 0.0
    min_available_balance: float = 0.005
    min_amount_residue: float = 0.003
    min_amount_out: float = 0.001
    max_amount_out: float = 0.003
    source_network: str = None
    destination_network: Optional[str] = None
    module_type: str = "buy_domen"

class ClaimDailyGMModule(ClaimDailyGMModule):
    """ Claim Daily GM in the Ink network """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_priority: int = 2
    module_name: str = "calim_daily_gm"
    module_display_name: str = "Claim Daily GM in the Ink network"