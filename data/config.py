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
    - swap_inkswap_eth_to_kraken
    - swap_inkswap_iswap_to_eth
    - swap_inkswap_sink_to_eth
    - swap_inkswap_kraken_to_eth
    - swap_inkswap_iswap_to_sink
    - swap_inkswap_sink_to_iswap
    - swap_inkswap_sink_to_kraken
    - swap_inkswap_kraken_to_sink
    - swap_inkswap_kraken_to_iswap
    - swap_inkswap_iswap_to_kraken
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
    "swap_inkswap_eth_to_kraken": SwapInkswapETHtoKRAKENModule,
    "swap_inkswap_iswap_to_eth": SwapInkswapISWAPtoETHModule,
    "swap_inkswap_sink_to_eth": SwapInkswapSINKtoETHModule,
    "swap_inkswap_kraken_to_eth": SwapInkswapKRAKENtoETHModule,
    "swap_inkswap_iswap_to_sink": SwapInkswapISWAPtoSINKModule,
    "swap_inkswap_sink_to_iswap": SwapInkswapSINKtoISWAPModule,
    "swap_inkswap_sink_to_kraken": SwapInkswapSINKtoKRAKENModule,
    "swap_inkswap_kraken_to_sink": SwapInkswapKRAKENtoSINKModule,
    "swap_inkswap_kraken_to_iswap": SwapInkswapKRAKENtoISWAPModule,
    "swap_inkswap_iswap_to_kraken": SwapInkswapISWAPtoKRAKENModule,
    "swap_dyor_eth_to_usdc": SwapDyorETHtoUSDCModule,
    "swap_dyor_eth_to_kraken": SwapDyorETHtoKrakenModule,
    "swap_dyor_eth_to_usdt": SwapDyorETHtoUSDTModule,
    "swap_dyor_eth_to_weth": SwapDyorETHtoWETHModule,
    "swap_dyor_eth_to_worm": SwapDyorETHtoWORMModule,
    "swap_dyor_weth_to_eth": SwapDyorWETHtoETHModule,
    "swap_dyor_usdc_to_eth": SwapDyorUSDCtoETHModule,   
    "swap_dyor_usdt_to_eth": SwapDyorUSDTtoETHModule,
    "swap_dyor_worm_to_eth": SwapDyorWORMtoETHModule,
    "swap_dyor_kraken_to_eth": SwapDyorKRAKENtoETHModule,
    "swap_dyor_kraken_to_worm": SwapDyorKRAKENtoWORMModule,
    "swap_dyor_worm_to_kraken": SwapDyorWORMtoKRAKENModule,
    "swap_dyor_worm_to_usdt": SwapDyorWORMtoUSDTModule,
    "swap_dyor_worm_to_usdc": SwapDyorWORMtoUSDCModule,
    "swap_dyor_worm_to_weth": SwapDyorWORMtoWETHModule,
    "swap_dyor_kraken_to_weth": SwapDyorKRAKENtoWETHModule,
    "swap_dyor_kraken_to_usdc": SwapDyorKRAKENtoUSDCModule,
    "swap_dyor_usdc_to_kraken": SwapDyorUSDCtoKRAKENModule,
    "swap_dyor_usdc_to_worm": SwapDyorUSDCtoWORMModule,
    "swap_dyor_usdc_to_usdt": SwapDyorUSDCtoUSDTModule,
    "swap_dyor_usdc_to_weth": SwapDyorUSDCtoWETHModule,
    "swap_dyor_weth_to_usdc": SwapDyorWETHtoUSDCModule,
    "swap_dyor_weth_to_usdt": SwapDyorWETHtoUSDTModule,
    "swap_dyor_weth_to_worm": SwapDyorWETHtoWORMModule,
    "swap_dyor_usdt_to_weth": SwapDyorUSDTtoWETHModule,
    "swap_dyor_weth_to_kraken": SwapDyorWETHtoKRAKENModule,
    "swap_dyor_usdt_to_usdc": SwapDyorUSDTtoUSDCModule,
    "swap_dyor_usdt_to_worm": SwapDyorUSDTtoWORMModule,
    "swap_dyor_usdt_to_kraken": SwapDyorUSDTtoKRAKENModule,
    "swap_dyor_kraken_to_usdt": SwapDyorKRAKENtoUSDTModule,
    "add_liquidity_dyor_eth_and_usdc": AddLiquidityDyorETHtoUSDCModule,
    "add_liquidity_dyor_eth_and_usdt": AddLiquidityDyorETHtoUSDTModule,
    "add_liquidity_dyor_eth_and_kraken": AddLiquidityDyorETHtoKRAKENModule,
    "add_liquidity_dyor_eth_and_worm": AddLiquidityDyorETHtoWORMModule,
    "mint_paragraf_nft": MintNFTParagrafModule,
    "mint_og_nft": MintNFTOGModule,
    "mint_guild_nft": MintNFTGuildModule
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
    "swap_inkswap_eth_to_kraken": swap_inkswap_eth_to_kraken,
    "swap_inkswap_iswap_to_eth": swap_inkswap_iswap_to_eth,
    "swap_inkswap_sink_to_eth": swap_inkswap_sink_to_eth,
    "swap_inkswap_kraken_to_eth": swap_inkswap_kraken_to_eth,
    "swap_inkswap_iswap_to_sink": swap_inkswap_iswap_to_sink,
    "swap_inkswap_sink_to_iswap": swap_inkswap_sink_to_iswap,
    "swap_inkswap_sink_to_kraken": swap_inkswap_sink_to_kraken,
    "swap_inkswap_kraken_to_sink": swap_inkswap_kraken_to_sink,
    "swap_inkswap_kraken_to_iswap": swap_inkswap_kraken_to_iswap,
    "swap_inkswap_iswap_to_kraken": swap_inkswap_iswap_to_kraken,
    "swap_dyor_eth_to_usdc": swap_dyor_eth_to_usdc,
    "swap_dyor_eth_to_kraken": swap_dyor_eth_to_kraken,
    "swap_dyor_eth_to_usdt": swap_dyor_eth_to_usdt,
    "swap_dyor_eth_to_weth": swap_dyor_eth_to_weth,
    "swap_dyor_eth_to_worm": swap_dyor_eth_to_worm,
    "swap_dyor_weth_to_eth": swap_dyor_weth_to_eth,
    "swap_dyor_usdc_to_eth": swap_dyor_usdc_to_eth,
    "swap_dyor_usdt_to_eth": swap_dyor_usdt_to_eth,
    "swap_dyor_worm_to_eth": swap_dyor_worm_to_eth,
    "swap_dyor_kraken_to_eth": swap_dyor_kraken_to_eth,
    "swap_dyor_kraken_to_worm": swap_dyor_kraken_to_worm,
    "swap_dyor_worm_to_kraken": swap_dyor_worm_to_kraken,
    "swap_dyor_worm_to_usdt": swap_dyor_worm_to_usdt,
    "swap_dyor_worm_to_usdc": swap_dyor_worm_to_usdc,
    "swap_dyor_worm_to_weth": swap_dyor_worm_to_weth,
    "swap_dyor_kraken_to_weth": swap_dyor_kraken_to_weth,
    "swap_dyor_kraken_to_usdc": swap_dyor_kraken_to_usdc,
    "swap_dyor_usdc_to_kraken": swap_dyor_usdc_to_kraken,
    "swap_dyor_usdc_to_worm": swap_dyor_usdc_to_worm,
    "swap_dyor_usdc_to_usdt": swap_dyor_usdc_to_usdt,
    "swap_dyor_usdc_to_weth": swap_dyor_usdc_to_weth,
    "swap_dyor_weth_to_usdc": swap_dyor_weth_to_usdc,
    "swap_dyor_weth_to_usdt": swap_dyor_weth_to_usdt,
    "swap_dyor_weth_to_worm": swap_dyor_weth_to_worm,
    "swap_dyor_usdt_to_weth": swap_dyor_usdt_to_weth,
    "swap_dyor_weth_to_kraken": swap_dyor_weth_to_kraken,
    "swap_dyor_usdt_to_usdc": swap_dyor_usdt_to_usdc,
    "swap_dyor_usdt_to_worm": swap_dyor_usdt_to_worm,
    "swap_dyor_usdt_to_kraken": swap_dyor_usdt_to_kraken,
    "swap_dyor_kraken_to_usdt": swap_dyor_kraken_to_usdt,
    "add_liquidity_dyor_eth_and_usdc": add_liquidity_dyor_eth_and_usdc,
    "add_liquidity_dyor_eth_and_usdt": add_liquidity_dyor_eth_and_usdt,
    "add_liquidity_dyor_eth_and_kraken": add_liquidity_dyor_eth_and_kraken,
    "add_liquidity_dyor_eth_and_worm": add_liquidity_dyor_eth_and_worm,
    "mint_paragraf_nft": mint_paragraf_nft,
    "mint_og_nft": mint_og_nft,
    "mint_guild_nft": mint_guild_nft
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