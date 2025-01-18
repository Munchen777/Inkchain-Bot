from typing import Dict

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

    ***Swaps InkSwap https://dex.inkswap.io/#/swap***

    ["swap_inkswap_eth_to_iswap"],
    ["swap_inkswap_eth_to_sink"],
    ["swap_inkswap_eth_to_weth"],
    ["swap_inkswap_iswap_to_eth"],
    ["swap_inkswap_sink_to_eth"],
    ["swap_inkswap_weth_to_eth"],
    ["swap_inkswap_iswap_to_sink"],
    ["swap_inkswap_sink_to_iswap"],
    ["swap_inkswap_sink_to_weth"],
    ["swap_inkswap_weth_to_sink"],
    ["swap_inkswap_weth_to_iswap"],
    ["swap_inkswap_iswap_to_weth"]
]

"""

CLASSIC_WITHDRAW_DEPENDENCIES = True # if True, then it would be possible to withdraw from the bridge where we made adding liquidity

CLASSIC_ROUTES_MODULES_USING = [
    ["swap_inkswap_iswap_to_weth"]
]

NETWORK_TOKEN_CONTRACTS: Dict[str, Dict[str, str]] = {
    "Base Mainnet": {
        "ETH": "0x4200000000000000000000000000000000000006",
    },
    "OP Mainnet": {
        "ETH": "0x4200000000000000000000000000000000000006",
    },
    "Ink Mainnet": {
        "ISWAP": "0x6814B9C5dae3DD05A8dBE9bF2b4E4FbB9Cef5302",
        "SINK": "0xD43e76fF8f95035E220070BdDFD3C0C2bdD3051B",
        "WETH": "0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"
    },
}
