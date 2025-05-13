import copy

from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional, Literal

from utils.networks import (
    Base,
    Ethereum,
    Ink,
    OP,
    Network,
)


MODULE_TYPES = Literal[
    "swap",
    "bridge",
    "add_liquidity",
    "remove_liquidity",
    "mint_nft",
    "deploy",
    "buy_domen",
    "claim",
]
BRIDGE_TYPE = Literal[
    "L1",
    "L2",
]


class BaseModuleInfo(BaseModel):
    """
    Base module info class for all modules
    
    Attributes:
        module_name: str - имя модуля
        module_display_name: str - отображаемое имя модуля (для вывода в консоль)
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        module_type: MODULE_TYPES - тип модуля
        source_token: Optional[str] - токен, который мы имеем на входе
        dest_token: Optional[str] - токен, который мы имеем на выходе
    
    """
    module_name: str = "BaseModule"
    module_display_name: str = "Base Module"
    source_network: Network | None = None
    destination_network: Network | None = None
    source_token: Optional[str | list] = None
    dest_token: Optional[str | list] = None
    module_type: MODULE_TYPES = "base"

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
    )


class BridgeModuleInfo(BaseModuleInfo):
    """
    Bridge module info class for all bridge modules

    Attributes:
        source_network: Network - объект сети отправления
        source_token: str - токен в сети отправления
        dest_token: str - токен в сети назначения
        module_type: str = "bridge" - тип модуля (дефолтное значение)
    
    """
    module_type: MODULE_TYPES = "bridge"
    source_token: str = "ETH"
    dest_token: str = "ETH"
    bridge_type: BRIDGE_TYPE = "L2"


class BridgeOwltoOPtoInkModule(BridgeModuleInfo):
    """ Bridge Owlto module from OP to Ink  """
    source_network: Network = OP
    destination_network: Network = Ink
    source_network_name: str = OP.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = OP.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_name: str = "bridge_owlto_op_to_ink"
    module_display_name: str = "Bridge Owlto OP to Ink"

class BridgeOwltoBasetoInkModule(BridgeModuleInfo):
    """ Bridge Owlto module from Base to Ink  """
    source_network: Network = Base
    destination_network: Network = Ink
    source_network_name: str = Base.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Base.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_name: str = "bridge_owlto_base_to_ink"
    module_display_name: str = "Bridge Owlto Base to Ink"

class BridgeOwltoInktoOPModule(BridgeModuleInfo):
    """ Bridge Owlto module from Ink to OP """
    source_network: Network = Ink
    destination_network: Network = OP
    source_network_name: str = Ink.name
    destination_network_name: str = OP.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = OP.chain_id
    module_name: str = "bridge_owlto_ink_to_op"
    module_display_name: str = "Bridge Owlto Ink to OP"

class BridgeOwltoInktoBaseModule(BridgeModuleInfo):
    """ Bridge Owlto module from Ink to Base """
    source_network: Network = Ink
    destination_network: Network = Base
    source_network_name: str = Ink.name
    destination_network_name: str = Base.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = Base.chain_id
    module_name: str = "bridge_owlto_ink_to_base"
    module_display_name: str = "Bridge Owlto Ink to Base"

class BridgeRelayOPtoInkModule(BridgeModuleInfo):
    """ Bridge Relay module from OP to Ink  """
    source_network: Network = OP
    destination_network: Network = Ink
    source_network_name: str = OP.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = OP.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_name: str = "bridge_relay_op_to_ink"
    module_display_name: str = "Bridge Relay OP to Ink"

class BridgeRelayBasetoInkModule(BridgeModuleInfo):
    """ Bridge Relay module from Base to Ink  """
    source_network: Network = Base
    destination_network: Network = Ink
    source_network_name: str = Base.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Base.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_name: str = "bridge_relay_base_to_ink"
    module_display_name: str = "Bridge Relay Base to Ink"

class BridgeRelayInktoOPModule(BridgeModuleInfo):
    """ Bridge Relay module from Ink to OP  """
    source_network: Network = Ink
    destination_network: Network = OP
    source_network_name: str = Ink.name
    destination_network_name: str = OP.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = OP.chain_id
    module_name: str = "bridge_relay_ink_to_op"
    module_display_name: str = "Bridge Relay Ink to OP"

class BridgeRelayInktoBaseModule(BridgeModuleInfo):
    """ Bridge Relay module from Ink to Base  """
    source_network: Network = Ink
    destination_network: Network = Base
    source_network_name: str = Ink.name
    destination_network_name: str = Base.name
    source_network_chain_id: int = Ink.chain_id
    destination_network_chain_id: int = Base.chain_id
    module_name: str = "bridge_relay_ink_to_base"
    module_display_name: str = "Bridge Relay Ink to Base"

class BridgGGEthereumtoInkModule(BridgeModuleInfo):
    """ Bridge GG module from Ethereum to Ink  """
    source_network: Network = Ethereum
    destination_network: Network = Ink
    source_network_name: str = Ethereum.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Ethereum.chain_id
    destination_network_chain_id: int = Ink.chain_id
    module_name: str = "bridge_gg_ethereum_to_ink"
    module_display_name: str = "Bridge GG Ethereum to Ink"
    bridge_type: BRIDGE_TYPE = "L1"


class SwapModuleInfo(BaseModuleInfo):
    """
    Swap module info class for all bridge modules
    
    Attributes:
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        source_network_name: str - название сети отправления
        destination_network_name: str - название сети назначения
        source_token: str - токен в сети отправления
        dest_token: str - токен в сети назначения
        source_network_chain_id: str - chain id сети отправления
        module_type: str = "swap" - тип модуля (дефолтное значение)
    
    """
    source_network: Network | None = Ink
    destination_network: Network | None = Ink
    source_network_name: str = Ink.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_type: MODULE_TYPES = "swap"
    source_token: str = "ETH"
    dest_token: str = "ETH"


class SwapInkswapETHtoISWAPModule(SwapModuleInfo):
    """ Swap Inkswap module from ETH to ISWAP """
    module_name: str = "swap_inkswap_eth_to_iswap"
    module_display_name: str = "Swap Inkswap ETH to ISWAP"
    dest_token: str = "ISWAP"

class SwapInkswapETHtoSINKModule(SwapModuleInfo):
    """ Swap Inkswap module from ETH to SINK """
    module_name: str = "swap_inkswap_eth_to_sink"
    module_display_name: str = "Swap Inkswap ETH to SINK"
    dest_token: str = "SINK"

class SwapInkswapETHtoKRAKENModule(SwapModuleInfo):
    """ Swap Inkswap module from ETH to KRAKEN """
    module_name: str = "swap_inkswap_eth_to_kraken"
    module_display_name: str = "Swap Inkswap ETH to KRAKEN"
    dest_token: str = "KRAKEN"

class SwapInkswapISWAPtoETHModule(SwapModuleInfo):
    """ Swap Inkswap module from ISWAP to ETH """
    module_name: str = "swap_inkswap_iswap_to_eth"
    module_display_name: str = "Swap Inkswap ISWAP to ETH"
    source_token: str = "ISWAP"

class SwapInkswapSINKtoETHModule(SwapModuleInfo):
    """ Swap Inkswap module from SINK to ETH """
    module_name: str = "swap_inkswap_sink_to_eth"
    module_display_name: str = "Swap Inkswap SINK to ETH"
    source_token: str = "SINK"

class SwapInkswapKRAKENtoETHModule(SwapModuleInfo):
    """ Swap Inkswap module from KRAKEN to ETH """
    module_name: str = "swap_inkswap_kraken_to_eth"
    module_display_name: str = "Swap Inkswap KRAKEN to ETH"
    source_token: str = "KRAKEN"

class SwapInkswapISWAPtoSINKModule(SwapModuleInfo):
    """ Swap Inkswap module from ISWAP to SINK """
    module_name: str = "swap_inkswap_iswap_to_sink"
    module_display_name: str = "Swap Inkswap ISWAP to SINK"
    source_token: str = "ISWAP"
    dest_token: str = "SINK"

class SwapInkswapSINKtoISWAPModule(SwapModuleInfo):
    """ Swap Inkswap module from SINK to ISWAP """
    module_name: str = "swap_inkswap_sink_to_iswap"
    module_display_name: str = "Swap Inkswap SINK to ISWAP"
    source_token: str = "SINK"
    dest_token: str = "ISWAP"

class SwapInkswapSINKtoKRAKENModule(SwapModuleInfo):
    """ Swap Inkswap module from SINK to KRAKEN """
    module_name: str = "swap_inkswap_sink_to_kraken"
    module_display_name: str = "Swap Inkswap SINK to KRAKEN"
    source_token: str = "SINK"
    dest_token: str = "KRAKEN"

class SwapInkswapKRAKENtoSINKModule(SwapModuleInfo):
    """ Swap Inkswap module from KRAKEN to SINK """
    module_name: str = "swap_inkswap_kraken_to_sink"
    module_display_name: str = "Swap Inkswap KRAKEN to SINK"
    source_token: str = "KRAKEN"
    dest_token: str = "SINK"

class SwapInkswapKRAKENtoISWAPModule(SwapModuleInfo):
    """ Swap Inkswap module from KRAKEN to ISWAP """
    module_name: str = "swap_inkswap_kraken_to_iswap"
    module_display_name: str = "Swap Inkswap KRAKEN to ISWAP"
    source_token: str = "KRAKEN"
    dest_token: str = "ISWAP"

class SwapInkswapISWAPtoKRAKENModule(SwapModuleInfo):
    """ Swap Inkswap module from ISWAP to KRAKEN """
    module_name: str = "swap_inkswap_iswap_to_kraken"
    module_display_name: str = "Swap Inkswap ISWAP to KRAKEN"
    source_token: str = "ISWAP"
    dest_token: str = "KRAKEN"

class SwapDyorETHtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to USDC.e  """
    module_name: str = "swap_dyor_eth_to_usdc"
    module_display_name: str = "Swap Dyor ETH to USDC.e"
    dest_token: str = "USDC"

class SwapDyorETHtoKrakenModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to Kraken  """
    module_name: str = "swap_dyor_eth_to_kraken"
    module_display_name: str = "Swap Dyor ETH to Kraken"
    dest_token: str = "KRAKEN"

class SwapDyorETHtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to USDT  """
    module_name: str = "swap_dyor_eth_to_usdt"
    module_display_name: str = "Swap Dyor ETH to USDT"
    dest_token: str = "USDT"

class SwapDyorETHtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to WETH  """
    module_name: str = "swap_dyor_eth_to_weth"
    module_display_name: str = "Swap Dyor ETH to WETH"
    dest_token: str = "WETH"

class SwapDyorETHtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from ETH to WORM  """
    module_name: str = "swap_dyor_eth_to_worm"
    module_display_name: str = "Swap Dyor ETH to WORM"
    dest_token: str = "WORM"

class SwapDyorWETHtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to ETH  """
    module_name: str = "swap_dyor_weth_to_eth"
    module_display_name: str = "Swap Dyor WETH to ETH"
    source_token: str = "WETH"

class SwapDyorUSDCtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDC.e to ETH  """
    module_name: str = "swap_dyor_usdc_to_eth"
    module_display_name: str = "Swap Dyor USDC.e to ETH"
    source_token: str = "USDC"

class SwapDyorUSDTtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to ETH  """
    module_name: str = "swap_dyor_usdt_to_eth"
    module_display_name: str = "Swap Dyor USDT to ETH"
    source_token: str = "USDT"

class SwapDyorWORMtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to ETH  """
    module_name: str = "swap_dyor_worm_to_eth"
    module_display_name: str = "Swap Dyor WORM to ETH"
    source_token: str = "WORM"

class SwapDyorKRAKENtoETHModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to ETH  """
    module_name: str = "swap_dyor_kraken_to_eth"
    module_display_name: str = "Swap Dyor KRAKEN to ETH"
    source_token: str = "KRAKEN"

class SwapDyorKRAKENtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to WORM  """
    module_name: str = "swap_dyor_kraken_to_worm"
    module_display_name: str = "Swap Dyor KRAKEN to WORM"
    source_token: str = "KRAKEN"
    dest_token: str = "WORM"

class SwapDyorWORMtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to KRAKEN  """
    module_name: str = "swap_dyor_worm_to_kraken"
    module_display_name: str = "Swap Dyor WORM to KRAKEN"
    source_token: str = "WORM"
    dest_token: str = "KRAKEN"

class SwapDyorWORMtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to USDT  """
    module_name: str = "swap_dyor_worm_to_usdt"
    module_display_name: str = "Swap Dyor WORM to USDT"
    source_token: str = "WORM"
    dest_token: str = "USDT"

class SwapDyorWORMtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to USDC  """
    module_name: str = "swap_dyor_worm_to_usdc"
    module_display_name: str = "Swap Dyor WORM to USDC"
    source_token: str = "WORM"
    dest_token: str = "USDC"

class SwapDyorWORMtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from WORM to WETH  """
    module_name: str = "swap_dyor_worm_to_weth"
    module_display_name: str = "Swap Dyor WORM to WETH"
    source_token: str = "WORM"
    dest_token: str = "WETH"

class SwapDyorKRAKENtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to WETH  """
    module_name: str = "swap_dyor_kraken_to_weth"
    module_display_name: str = "Swap Dyor KRAKEN to WETH"
    source_token: str = "KRAKEN"
    dest_token: str = "WETH"

class SwapDyorKRAKENtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to USDC  """
    module_name: str = "swap_dyor_kraken_to_usdc"
    module_display_name: str = "Swap Dyor KRAKEN to USDC"
    source_token: str = "KRAKEN"
    dest_token: str = "USDC"

class SwapDyorUSDCtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to KRAKEN  """
    module_name: str = "swap_dyor_usdc_to_kraken"
    module_display_name: str = "Swap Dyor USDC to KRAKEN"
    source_token: str = "USDC"
    dest_token: str = "KRAKEN"

class SwapDyorUSDCtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to WORM  """
    module_name: str = "swap_dyor_usdc_to_worm"
    module_display_name: str = "Swap Dyor USDC to WORM"
    source_token: str = "USDC"
    dest_token: str = "WORM"

class SwapDyorUSDCtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to USDT  """
    module_name: str = "swap_dyor_usdc_to_usdt"
    module_display_name: str = "Swap Dyor USDC to USDT"
    source_token: str = "USDC"
    dest_token: str = "USDT"

class SwapDyorUSDCtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDC to WETH  """
    module_name: str = "swap_dyor_usdc_to_weth"
    module_display_name: str = "Swap Dyor USDC to WETH"
    source_token: str = "USDC"
    dest_token: str = "WETH"

class SwapDyorWETHtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to USDC  """
    module_name: str = "swap_dyor_weth_to_usdc"
    module_display_name: str = "Swap Dyor WETH to USDC"
    source_token: str = "WETH"
    dest_token: str = "USDC"

class SwapDyorWETHtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to USDT  """
    module_name: str = "swap_dyor_weth_to_usdt"
    module_display_name: str = "Swap Dyor WETH to USDT"
    source_token: str = "WETH"
    dest_token: str = "USDT"

class SwapDyorWETHtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to WORM  """
    module_name: str = "swap_dyor_weth_to_worm"
    module_display_name: str = "Swap Dyor WETH to WORM"
    source_token: str = "WETH"
    dest_token: str = "WORM"

class SwapDyorUSDTtoWETHModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to WETH  """
    module_name: str = "swap_dyor_usdt_to_weth"
    module_display_name: str = "Swap Dyor USDT to WETH"
    source_token: str = "USDT"
    dest_token: str = "WETH"

class SwapDyorWETHtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from WETH to KRAKEN  """
    module_name: str = "swap_dyor_weth_to_kraken"
    module_display_name: str = "Swap Dyor WETH to KRAKEN"
    source_token: str = "WETH"
    dest_token: str = "KRAKEN"

class SwapDyorUSDTtoUSDCModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to USDC  """
    module_name: str = "swap_dyor_usdt_to_usdc"
    module_display_name: str = "Swap Dyor USDT to USDC"
    source_token: str = "USDT"
    dest_token: str = "USDC"

class SwapDyorUSDTtoWORMModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to WORM  """
    module_name: str = "swap_dyor_usdt_to_worm"
    module_display_name: str = "Swap Dyor USDT to WORM"
    source_token: str = "USDT"
    dest_token: str = "WORM"

class SwapDyorUSDTtoKRAKENModule(SwapModuleInfo):
    """ Swap Dyor module from USDT to KRAKEN  """
    module_name: str = "swap_dyor_usdt_to_kraken"
    module_display_name: str = "Swap Dyor USDT to KRAKEN"
    source_token: str = "USDT"
    dest_token: str = "KRAKEN"

class SwapDyorKRAKENtoUSDTModule(SwapModuleInfo):
    """ Swap Dyor module from KRAKEN to USDT  """
    module_name: str = "swap_dyor_kraken_to_usdt"
    module_display_name: str = "Swap Dyor KRAKEN to USDT"
    source_token: str = "KRAKEN"
    dest_token: str = "USDT"


class AddLiquidityModuleInfo(BaseModuleInfo):
    """
    Add Liquidity module info class for all add liquidity modules
    
    Attributes:
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        source_network_name: str - название сети отправления
        destination_network_name: str - название сети назначения
        source_token: str - токен в сети отправления
        dest_token: str - токен в сети назначения
        source_network_chain_id: str - chain id сети отправления
        module_type: str = "add_liquidity" - тип модуля (дефолтное значение)
    
    """
    source_network: Network | None = Ink
    destination_network: Network | None = Ink
    source_network_name: str = Ink.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_type: MODULE_TYPES = "add_liquidity"
    source_token: str = "ETH"
    dest_token: str = "ETH"


class AddLiquidityDineroiETHandETHModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dinero module iETH on the Ink network and ETH on the Ethereum network """
    module_name: str = "add_liquidity_dinero_ieth_and_eth"
    module_display_name: str = "Add Liquidity Dinero iETH on the Ink network and ETH on the Ethereum network"
    source_token: list = ["ETH"]
    destination_network: Network = Ethereum
    destination_network_name: str = Ethereum.name

class AddLiquidityDyorETHtoUSDCModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and USDC  """
    module_name: str = "add_liquidity_dyor_eth_and_usdc"
    module_display_name: str = "Add Liquidity Dyor ETH and USDC"
    source_token: list = ["ETH", "USDC"]

class AddLiquidityDyorETHtoUSDTModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and USDT  """
    module_name: str = "add_liquidity_dyor_eth_and_usdt"
    module_display_name: str = "Add Liquidity Dyor ETH and USDT"
    source_token: list = ["ETH", "USDT"]

class AddLiquidityDyorETHtoKRAKENModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and KRAKEN  """
    module_name: str = "add_liquidity_dyor_eth_and_kraken"
    module_display_name: str = "Add Liquidity Dyor ETH and KRAKEN"
    source_token: list = ["ETH", "KRAKEN"]

class AddLiquidityDyorETHtoWORMModule(AddLiquidityModuleInfo):
    """ Add Liquidity Dyor module from ETH and WORM  """
    module_name: str = "add_liquidity_dyor_eth_and_worm"
    module_display_name: str = "Add Liquidity Dyor ETH and WORM"
    source_token: list = ["ETH", "WORM"]

class MintNFTModuleInfo(BaseModuleInfo):
    """
    Mint NFT module info class for all mint nft modules
    
    Attributes:
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        source_network_name: str - название сети отправления
        destination_network_name: str - название сети назначения
        source_token: str - токен в сети отправления
        module_type: str = "mint_nft" - тип модуля (дефолтное значение)
    
    """
    source_network: Network | None = Ink
    destination_network: Network | None = Ink
    source_network_name: str = Ink.name
    destination_network_name: str = Ink.name
    module_type: MODULE_TYPES = "mint_nft"
    source_token: str = "ETH"

class MintNFTParagrafModule(MintNFTModuleInfo):
    """ Mint Paragraf NFT module  """
    source_network: Network = OP
    destination_network: Network = OP
    source_network_name: str = OP.name
    destination_network_name: str = OP.name
    source_network_chain_id: int = OP.chain_id
    module_name: str = "mint_paragraf_nft"
    module_display_name: str = "Mint Paragraf NFT"

class MintNFTOGModule(MintNFTModuleInfo):
    """ Mint OG NFT module  """
    source_network: Network = OP
    destination_network: Network = OP
    source_network_name: str = OP.name
    destination_network_name: str = OP.name
    source_network_chain_id: int = OP.chain_id
    module_name: str = "mint_og_nft"
    module_display_name: str = "Mint OG NFT"

class MintNFTGuildModule(MintNFTModuleInfo):
    """ Mint Guild NFT module  """
    source_network: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_name: str = "mint_guild_nft"
    module_display_name: str = "Mint Guild NFT"


class DeployContractModule(BaseModuleInfo):
    """
    Deployment of the contract module info class for all deployment contract modules
    
    Attributes:
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        source_network_name: str - название сети отправления
        destination_network_name: str - название сети назначения
        source_token: str - токен в сети отправления
        source_network_chain_id: str - chain id сети отправления
        module_type: str = "deploy" - тип модуля (дефолтное значение)
    
    """
    source_network: Network = Ink
    destination_network: Network = Ink.name
    source_network_name: str = Ink.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_type: MODULE_TYPES = "deploy"
    source_token: str = "ETH"

class DeployContractInkModule(DeployContractModule):
    """ Deployment of the contract in the Ink network """
    module_name: str = "deploy_contract_ink_network"
    module_display_name: str = "Deployment of the contract in the Ink network"


class BuyZNCDomenModule(BaseModuleInfo):
    """
    Buy ZNC domen module info class for all buy ZNC domen modules
    
    Attributes:
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        source_network_name: str - название сети отправления
        destination_network_name: str - название сети назначения
        source_token: str - токен в сети отправления
        source_network_chain_id: str - chain id сети отправления
        module_type: str = "buy_domen" - тип модуля (дефолтное значение)
    
    """
    source_network: Network = Ink
    destination_network: Network = source_network
    source_network_name: str = Ink.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_type: MODULE_TYPES = "buy_domen"
    source_token: str = "ETH"


class BuyZNCDomenInkModule(BuyZNCDomenModule):
    """ Buy ZNC domen in the Ink network """

    module_name: str = "buy_znc_domen_ink_network"
    module_display_name: str = "Buy ZNC domen in the Ink network"


class ClaimDailyGMModule(BaseModuleInfo):
    """
    Claim Daily module info class for all claim daily modules
    
    Attributes:
        source_network: Network - объект сети отправления
        destination_network: Network - объект сети назначения
        source_network_name: str - название сети отправления
        destination_network_name: str - название сети назначения
        source_token: str - токен в сети отправления
        source_network_chain_id: str - chain id сети отправления
        module_type: str = "claim" - тип модуля (дефолтное значение)
    
    """
    source_network: Network | None = Ink
    destination_network: Network | None = Ink
    module_type: MODULE_TYPES = "claim"
    source_token: str = "ETH"


class ClaimDailyGMModule(ClaimDailyGMModule):
    """ Claim Daily GM in the Ink network """
    source_network_name: str = Ink.name
    destination_network_name: str = Ink.name
    source_network_chain_id: int = Ink.chain_id
    module_name: str = "claim_daily_gm"
    module_display_name: str = "Claim Daily GM in the Ink network"
