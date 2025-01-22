from typing import Dict, Set

"""
Handle installation of classic route.
You can specify modules that will be used in the classic route.

CLASSIC_ROUTES_MODULES_USING = [
    ***Bridges from L2 to L2***

    ["bridge_owlto_op_to_ink"],
    ["bridge_owlto_base_to_ink"],
    ["bridge_owlto_ink_to_op"],
    ["bridge_owlto_ink_to_base"],
    ["bridge_relay_op_to_ink"],
    ["bridge_relay_base_to_ink"],
    ["bridge_relay_ink_to_op"],
    ["bridge_relay_ink_to_base"],
    ["bridge_rhino_op_to_ink"],
    
    ***Bridges from L1 to L2***

    ["bridge_gg_ethereum_to_ink"],

    ***Swaps InkSwap https://dex.inkswap.io/#/swap ***

    ["swap_inkswap_eth_to_iswap"],
    ["swap_inkswap_eth_to_sink"],
    ["swap_inkswap_eth_to_kraken"],
    ["swap_inkswap_iswap_to_eth"],
    ["swap_inkswap_sink_to_eth"],
    ["swap_inkswap_kraken_to_eth"],
    ["swap_inkswap_iswap_to_sink"],
    ["swap_inkswap_sink_to_iswap"],
    ["swap_inkswap_sink_to_kraken"],
    ["swap_inkswap_kraken_to_sink"],
    ["swap_inkswap_kraken_to_iswap"],
    ["swap_inkswap_iswap_to_kraken"]

    ***Swaps DyorSwap https://dyorswap.finance/swap ***

    ["swap_dyor_eth_to_usdc"],
    ["swap_dyor_eth_to_kraken"],
    ["swap_dyor_eth_to_usdt"],
    ["swap_dyor_eth_to_weth"],
    ["swap_dyor_eth_to_worm"],
    ["swap_dyor_weth_to_eth"],
    ["swap_dyor_usdc_to_eth"],
    ["swap_dyor_usdt_to_eth"],
    ["swap_dyor_worm_to_eth"],
    ["swap_dyor_kraken_to_eth"],
    ["swap_dyor_kraken_to_worm"],
    ["swap_dyor_worm_to_kraken"],
    ["swap_dyor_worm_to_usdt"],
    ["swap_dyor_worm_to_usdc"],
    ["swap_dyor_worm_to_weth"],
    ["swap_dyor_kraken_to_weth"],
    ["swap_dyor_kraken_to_usdc"],
    ["swap_dyor_usdc_to_kraken"],
    ["swap_dyor_usdc_to_worm"],
    ["swap_dyor_usdc_to_usdt"],
    ["swap_dyor_usdc_to_weth"],
    ["swap_dyor_weth_to_usdt"],
    ["swap_dyor_weth_to_usdc"],
    ["swap_dyor_weth_to_worm"],
    ["swap_dyor_usdt_to_weth"],
    ["swap_dyor_weth_to_kraken"],
    ["swap_dyor_usdt_to_usdc"],
    ["swap_dyor_usdt_to_worm"],
    ["swap_dyor_usdt_to_kraken"],
    ["swap_dyor_kraken_to_usdt"]

    ***Add Liquidity DyorSwap https://dyorswap.finance/liquidity ***

    ["add_liquidity_dyor_eth_and_usdc"],
    ["add_liquidity_dyor_eth_and_usdt"],
    ["add_liquidity_dyor_eth_and_kraken"],
    ["add_liquidity_dyor_eth_and_worm"]
]

"""

CLASSIC_WITHDRAW_DEPENDENCIES = True # if True, then it would be possible to withdraw from the bridge where we made adding liquidity

CLASSIC_ROUTES_MODULES_USING = [
    ["swap_dyor_eth_to_kraken"],
]

PRIORITY_NETWORK_NAMES: Set[str] = { # Priority Network names to work with
    "Ink Mainnet",
}

NETWORK_TOKEN_CONTRACTS: Dict[str, Dict[str, str]] = {
    "Base Mainnet": {
        "": "",
    },
    "OP Mainnet": {
        "": "",
    },
    "Ink Mainnet": {
        "WETH": "0x4200000000000000000000000000000000000006",
        "ISWAP": "0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302",
        "SINK": "0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B",
        "KRAKEN": "0xCa5f2cCBD9C40b32657dF57c716De44237f80F05",
        "USDC": "0xf1815bd50389c46847f0bda824ec8da914045d14",
        "USDT": "0x0200C29006150606B650577BBE7B6248F58470c1",
        "WORM": "0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"
    },
}
