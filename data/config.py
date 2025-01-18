from typing import Callable, Dict

from functions import*
from modules.interfaces import*
from utils.networks import Ethereum, Ink
from utils.tools import get_accounts_data


"""
Available modules:
    - bridge_owlto_op_to_ink
    - bridge_owlto_base_to_ink
    - bridge_owlto_ink_to_op
    - bridge_owlto_ink_to_base
    - bridge_relay_op_to_ink
    - bridge_relay_base_to_ink
    - bridge_relay_ink_to_op
    - bridge_relay_ink_to_base
    - bridge_gg_ethereum_to_ink
    - swap_inkswap_eth_to_iswap
    - swap_inkswap_eth_to_sink
    - swap_inkswap_eth_to_weth
    - swap_inkswap_iswap_to_eth
    - swap_inkswap_sink_to_eth
    - swap_inkswap_weth_to_eth
    - swap_inkswap_iswap_to_sink
    - swap_inkswap_sink_to_iswap
    - swap_inkswap_sink_to_weth
    - swap_inkswap_weth_to_sink
    - swap_inkswap_weth_to_iswap
    - swap_inkswap_iswap_to_weth
    - 
"""

# Mapping of module names to module classes
MODULES_CLASSES: Dict[str, BaseModuleInfo] = {
    "bridge_owlto_op_to_ink": BridgeOwltoOPtoInkModule,
    "bridge_owlto_base_to_ink": BridgeOwltoBasetoInkModule,
    "bridge_owlto_ink_to_op": BridgeOwltoInktoOPModule,
    "bridge_owlto_ink_to_base": BridgeOwltoInktoBaseModule,
    "bridge_relay_op_to_ink": BridgeRelayOPtoInkModule,
    "bridge_relay_base_to_ink": BridgeRelayBasetoInkModule,
    "bridge_relay_ink_to_op": BridgeRelayInktoOPModule,
    "bridge_relay_ink_to_base": BridgeRelayInktoBaseModule,
    "bridge_gg_ethereum_to_ink": BridgGGEthereumtoInkModule,
    "swap_inkswap_eth_to_iswap": SwapInkswapETHtoISWAPModule,
    "swap_inkswap_eth_to_sink": SwapInkswapETHtoSINKModule,
    "swap_inkswap_eth_to_weth": SwapInkswapETHtoWETHModule,
    "swap_inkswap_iswap_to_eth": SwapInkswapISWAPtoETHModule,
    "swap_inkswap_sink_to_eth": SwapInkswapSINKtoETHModule,
    "swap_inkswap_weth_to_eth": SwapInkswapWETHtoETHModule,
    "swap_inkswap_iswap_to_sink": SwapInkswapISWAPtoSINKModule,
    "swap_inkswap_sink_to_iswap": SwapInkswapSINKtoISWAPModule,
    "swap_inkswap_sink_to_weth": SwapInkswapSINKtoWETHModule,
    "swap_inkswap_weth_to_sink": SwapInkswapWETHtoSINKModule,
    "swap_inkswap_weth_to_iswap": SwapInkswapWETHtoISWAPModule,
    "swap_inkswap_iswap_to_weth": SwapInkswapISWAPtoWETHModule
}

CHAIN_NAMES: Dict[int, str] = {
    0: Ethereum.name,
    1: Ink.name,
}

# Mapping of module names to module functions
MODULE_RUNNERS: Dict[str, Callable] = {
    "bridge_owlto_op_to_ink": bridge_owlto_op_to_ink,
    "bridge_owlto_base_to_ink": bridge_owlto_base_to_ink,
    "bridge_owlto_ink_to_op": bridge_owlto_ink_to_op,
    "bridge_owlto_ink_to_base": bridge_owlto_ink_to_base,
    "bridge_relay_op_to_ink": bridge_relay_op_to_ink,
    "bridge_relay_base_to_ink": bridge_relay_base_to_ink,
    "bridge_relay_ink_to_op": bridge_relay_ink_to_op,
    "bridge_relay_ink_to_base": bridge_relay_ink_to_base,
    "bridge_gg_ethereum_to_ink": bridge_gg_ethereum_to_ink,
    "swap_inkswap_eth_to_iswap": swap_inkswap_eth_to_iswap,
    "swap_inkswap_eth_to_sink": swap_inkswap_eth_to_sink,
    "swap_inkswap_eth_to_weth": swap_inkswap_eth_to_weth,
    "swap_inkswap_iswap_to_eth": swap_inkswap_iswap_to_eth,
    "swap_inkswap_sink_to_eth": swap_inkswap_sink_to_eth,
    "swap_inkswap_weth_to_eth": swap_inkswap_weth_to_eth,
    "swap_inkswap_iswap_to_sink": swap_inkswap_iswap_to_sink,
    "swap_inkswap_sink_to_iswap": swap_inkswap_sink_to_iswap,
    "swap_inkswap_sink_to_weth": swap_inkswap_sink_to_weth,
    "swap_inkswap_weth_to_sink": swap_inkswap_weth_to_sink,
    "swap_inkswap_weth_to_iswap": swap_inkswap_weth_to_iswap,
    "swap_inkswap_iswap_to_weth": swap_inkswap_iswap_to_weth
}

ACCOUNT_NAMES, PRIVATE_KEYS, PROXIES = get_accounts_data()

TITLE = """\033[33m
 /$$$$$$           /$$                           /$$                 /$$                 /$$$$$$$              /$$    
|_  $$_/          | $$                          | $$                |__/                | $$__  $$            | $$    
  | $$   /$$$$$$$ | $$   /$$  /$$$$$$   /$$$$$$$| $$$$$$$   /$$$$$$  /$$ /$$$$$$$       | $$  \ $$  /$$$$$$  /$$$$$$  
  | $$  | $$__  $$| $$  /$$/ /$$__  $$ /$$_____/| $$__  $$ |____  $$| $$| $$__  $$      | $$$$$$$  /$$__  $$|_  $$_/  
  | $$  | $$  \ $$| $$$$$$/ | $$  \ $$| $$      | $$  \ $$  /$$$$$$$| $$| $$  \ $$      | $$__  $$| $$  \ $$  | $$    
  | $$  | $$  | $$| $$_  $$ | $$  | $$| $$      | $$  | $$ /$$__  $$| $$| $$  | $$      | $$  \ $$| $$  | $$  | $$ /$$
 /$$$$$$| $$  | $$| $$ \  $$|  $$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$$| $$| $$  | $$      | $$$$$$$/|  $$$$$$/  |  $$$$/
|______/|__/  |__/|__/  \__/ \______/  \_______/|__/  |__/ \_______/|__/|__/  |__/      |_______/  \______/    \___/  
                                                                                                                      
                                                                                                                      
                                                                                                                      

                                                                         
                                                                         
\033[0m                                                                                                        \033[32m@divinus.xyz\033[0m 
"""