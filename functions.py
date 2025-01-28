from utils.client import Client
from modules.bridges import *
from modules.swaps import *
from modules.add_liquidity import *
from modules.mint_nfts import *
from modules.others import *
from modules.interfaces import *


def get_client(account_name, private_key, proxy, source_network: str) -> Client:
    return Client(account_name, private_key, proxy, source_network)

async def bridge_owlto_op_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoOPtoInkModule):
    worker = BridgeOwltoOPtoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_base_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoBasetoInkModule):
    worker = BridgeOwltoBasetoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_ink_to_op(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoInktoOPModule):
    worker = BridgeOwltoInktoOPWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_owlto_ink_to_base(account_name: str, private_key: str, proxy: str | None, module_info: BridgeOwltoInktoBaseModule):
    worker = BridgeOwltoInktoBaseWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_relay_op_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgeRelayOPtoInkModule):
    worker = BridgeRelayOPtoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_relay_base_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgeRelayBasetoInkModule):
    worker = BridgeRelayBasetoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_relay_ink_to_op(account_name: str, private_key: str, proxy: str | None, module_info: BridgeRelayInktoOPModule):
    worker = BridgeRelayInktoOPWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_relay_ink_to_base(account_name: str, private_key: str, proxy: str | None, module_info: BridgeRelayInktoBaseModule):
    worker = BridgeRelayInktoBaseWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def bridge_gg_ethereum_to_ink(account_name: str, private_key: str, proxy: str | None, module_info: BridgGGEthereumtoInkModule):
    worker = BridGGEthereumtoInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_eth_to_iswap(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapETHtoISWAPModule):
    worker = SwapInkswapETHtoISWAPWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_eth_to_sink(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapETHtoSINKModule):
    worker = SwapInkswapETHtoSINKWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_eth_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapETHtoKRAKENModule):
    worker = SwapInkswapETHtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_iswap_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapISWAPtoETHModule):
    worker = SwapInkswapISWAPtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_sink_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapSINKtoETHModule):
    worker = SwapInkswapSINKtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_kraken_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapKRAKENtoETHModule):
    worker = SwapInkswapKRAKENtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_iswap_to_sink(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapISWAPtoSINKModule):
    worker = SwapInkswapISWAPtoSINKWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_sink_to_iswap(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapSINKtoISWAPModule):
    worker = SwapInkswapSINKtoISWAPWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_sink_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapSINKtoKRAKENModule):
    worker = SwapInkswapSINKtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_kraken_to_sink(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapKRAKENtoSINKModule):
    worker = SwapInkswapKRAKENtoSINKWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_kraken_to_iswap(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapKRAKENtoISWAPModule):
    worker = SwapInkswapKRAKENtoISWAPWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_inkswap_iswap_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapInkswapISWAPtoKRAKENModule):
    worker = SwapInkswapISWAPtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_eth_to_usdc(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorETHtoUSDCModule):
    worker = SwapDyorETHtoUSDCWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_eth_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorETHtoKrakenModule):
    worker = SwapDyorETHtoKrakenWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_eth_to_usdt(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorETHtoUSDTModule):
    worker = SwapDyorETHtoUSDTWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_eth_to_weth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorETHtoWETHModule):
    worker = SwapDyorETHtoWETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_eth_to_worm(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorETHtoWORMModule):
    worker = SwapDyorETHtoWORMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_weth_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWETHtoETHModule):
    worker = SwapDyorWETHtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdc_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDCtoETHModule):
    worker = SwapDyorUSDCtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdt_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDTtoETHModule):
    worker = SwapDyorUSDTtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_worm_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWORMtoETHModule):
    worker = SwapDyorWORMtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_kraken_to_eth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorKRAKENtoETHModule):
    worker = SwapDyorKRAKENtoETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_kraken_to_worm(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorKRAKENtoWORMModule):
    worker = SwapDyorKRAKENtoWORMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_worm_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWORMtoKRAKENModule):
    worker = SwapDyorWORMtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_worm_to_usdt(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWORMtoUSDTModule):
    worker = SwapDyorWORMtoUSDTWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_worm_to_usdc(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWORMtoUSDCModule):
    worker = SwapDyorWORMtoUSDCWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_worm_to_weth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWORMtoWETHModule):
    worker = SwapDyorWORMtoWETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_kraken_to_weth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorKRAKENtoWETHModule):
    worker = SwapDyorKRAKENtoWETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_kraken_to_usdc(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorKRAKENtoUSDCModule):
    worker = SwapDyorKRAKENtoUSDCWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdc_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDCtoKRAKENModule):
    worker = SwapDyorUSDCtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdc_to_worm(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDCtoWORMModule):
    worker = SwapDyorUSDCtoWORMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdc_to_usdt(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDCtoUSDTModule):
    worker = SwapDyorUSDCtoUSDTWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdc_to_weth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDCtoWETHModule):
    worker = SwapDyorUSDCtoWETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_weth_to_usdc(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWETHtoUSDCModule):
    worker = SwapDyorWETHtoUSDCWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_weth_to_usdt(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWETHtoUSDTModule):
    worker = SwapDyorWETHtoUSDTWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_weth_to_worm(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWETHtoWORMModule):
    worker = SwapDyorWETHtoWORMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdt_to_weth(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDTtoWETHModule):
    worker = SwapDyorUSDTtoWETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_weth_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorWETHtoKRAKENModule):
    worker = SwapDyorWETHtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdt_to_usdc(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDTtoUSDCModule):
    worker = SwapDyorUSDTtoUSDCWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdt_to_worm(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDTtoWORMModule):
    worker = SwapDyorUSDTtoWORMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_usdt_to_kraken(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorUSDTtoKRAKENModule):
    worker = SwapDyorUSDTtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def swap_dyor_kraken_to_usdt(account_name: str, private_key: str, proxy: str | None, module_info: SwapDyorKRAKENtoUSDTModule):
    worker = SwapDyorKRAKENtoUSDTWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def add_liquidity_dinero_eth_and_ieth(account_name: str, private_key: str, proxy: str | None, module_info: AddLiquidityDineroETHandiETHModule):
    worker = AddLiquidityDineroETHandiETHWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def add_liquidity_dyor_eth_and_usdc(account_name: str, private_key: str, proxy: str | None, module_info: AddLiquidityDyorETHtoUSDCModule):
    worker = AddLiquidityDyorETHtoUSDCWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def add_liquidity_dyor_eth_and_usdt(account_name: str, private_key: str, proxy: str | None, module_info: AddLiquidityDyorETHtoUSDTModule):
    worker = AddLiquidityDyorETHtoUSDTWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def add_liquidity_dyor_eth_and_kraken(account_name: str, private_key: str, proxy: str | None, module_info: AddLiquidityDyorETHtoKRAKENModule):
    worker = AddLiquidityDyorETHtoKRAKENWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def add_liquidity_dyor_eth_and_worm(account_name: str, private_key: str, proxy: str | None, module_info: AddLiquidityDyorETHtoWORMModule):
    worker = AddLiquidityDyorETHtoWORMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def mint_paragraf_nft(account_name: str, private_key: str, proxy: str | None, module_info: MintNFTParagrafModule):
    worker = MintNFTParagrafWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def mint_og_nft(account_name: str, private_key: str, proxy: str | None, module_info: MintNFTOGModule):
    worker = MintNFTOGWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def mint_guild_nft(account_name: str, private_key: str, proxy: str | None, module_info: MintNFTGuildModule):
    worker = MintNFTGuildWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def deploy_contract_ink_network(account_name: str, private_key: str, proxy: str | None, module_info: DeployContractInkModule):
    worker = DeployContractInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def buy_znc_domen_ink_network(account_name: str, private_key: str, proxy: str | None, module_info: BuyZNCDomenInkModule):
    worker = BuyZNCDomenInkWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()

async def claim_daily_gm(account_name: str, private_key: str, proxy: str | None, module_info: ClaimDailyGMModule):
    worker = ClaimDailyGMWorker(
        client=get_client(account_name, private_key, proxy, module_info.source_network),
        module_info=module_info
    )
    return await worker.run()