from dataclasses import dataclass
from typing import Dict

from interfaces import *
from models import ERC20Contract


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
    "mint_guild_nft": MintNFTGuildModule,
    "deploy_contract_ink_network": DeployContractInkModule,
    "buy_znc_domen_ink_network": BuyZNCDomenInkModule,
    "claim_daily_gm": ClaimDailyGMModule,
    "add_liquidity_dinero_ieth_and_eth": AddLiquidityDineroiETHandETHModule
}

@dataclass(slots=True)
class BridgeGGContract(ERC20Contract):
    address: str = "0x88ff1e5b602916615391f55854588efcbb7663f0"
    abi_file: str = "bridge_gg.json"

@dataclass(slots=True)
class OwltoContract(ERC20Contract):
    address: str = "0x0e83ded9f80e1c92549615d96842f5cb64a08762"
    abi_file: str = "owlto.json"

@dataclass(slots=True)
class ParagraphContract(ERC20Contract):
    address: str = "0x69086dDd87cb58709540f784c32740a6f9a49CFF"
    abi_file: str = "paragraph.json"

@dataclass(slots=True)
class DailyGMContract(ERC20Contract):
    address: str = "0x9F500d075118272B3564ac6Ef2c70a9067Fd2d3F"
    abi_file: str = "daily_gm.json"
