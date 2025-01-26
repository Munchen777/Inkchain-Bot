from typing import Dict, List, Set

"""
Handle installation of classic route.
You can specify modules that will be used in the classic route.

CLASSIC_ROUTES_MODULES_USING = [
    ***Bridges from L2 to L2***                                             Brief description of the modules

    ["bridge_owlto_op_to_ink"]                          Bridge on the website Owlto from the Optimism Network to the Ink network
    ["bridge_owlto_base_to_ink"]                        Bridge on the website Owlto from the Base Network to the Ink network
    ["bridge_owlto_ink_to_op"]                          Bridge on the website Owlto from the Ink Network to the Optimism network
    ["bridge_owlto_ink_to_base"]                        Bridge on the website Owlto from the Ink Network to the Base network
    ["bridge_relay_op_to_ink"]                          Bridge on the website Relay from the Optimism Network to the Ink network
    ["bridge_relay_base_to_ink"]                        Bridge on the website Relay from the Base Network to the Ink network
    ["bridge_relay_ink_to_op"]                          Bridge on the website Relay from the Ink Network to the Optimism network
    ["bridge_relay_ink_to_base"]                        Bridge on the website Relay from the Ink Network to the Base network
    
    ***Bridges from L1 to L2***

    ["bridge_gg_ethereum_to_ink"]                       Bridge on the website BridGG from the Ethereum Network to the Ink network

    ***Swaps InkSwap https://dex.inkswap.io/#/swap ***

    ["swap_inkswap_eth_to_iswap"]                       Swap on the website InkSwap from the ETH token to ISWAP token on the Ink network
    ["swap_inkswap_eth_to_sink"]                        Swap on the website InkSwap from the ETH token to SINK token on the Ink network
    ["swap_inkswap_eth_to_kraken"]                      Swap on the website InkSwap from the ETH token to KRAKEN token on the Ink network
    ["swap_inkswap_iswap_to_eth"]                       Swap on the website InkSwap from the ISWAP token to ETH token on the Ink network
    ["swap_inkswap_sink_to_eth"]                        Swap on the website InkSwap from the SINK token to ETH token on the Ink network
    ["swap_inkswap_kraken_to_eth"]                      Swap on the website InkSwap from the KRAKEN token to ETH token on the Ink network
    ["swap_inkswap_iswap_to_sink"]                      Swap on the website InkSwap from the ISWAP token to SINK token on the Ink network
    ["swap_inkswap_sink_to_iswap"]                      Swap on the website InkSwap from the SINK token to ISWAP token on the Ink network
    ["swap_inkswap_sink_to_kraken"]                     Swap on the website InkSwap from the SINK token to KRAKEN token on the Ink network
    ["swap_inkswap_kraken_to_sink"]                     Swap on the website InkSwap from the KRAKEN token to SINK token on the Ink network
    ["swap_inkswap_kraken_to_iswap"]                    Swap on the website InkSwap from the KRAKEN token to ISWAP token on the Ink network
    ["swap_inkswap_iswap_to_kraken"]                    Swap on the website InkSwap from the ISWAP token to KRAKEN token on the Ink network

    ***Swaps DyorSwap https://dyorswap.finance/swap ***

    ["swap_dyor_eth_to_usdc"]                           Swap on the website Dyor from the ETH token to USDC token on the Ink network
    ["swap_dyor_eth_to_kraken"]                         Swap on the website Dyor from the ETH token to KRAKEN token on the Ink network
    ["swap_dyor_eth_to_usdt"]                           Swap on the website Dyor from the ETH token to USDT token on the Ink network
    ["swap_dyor_eth_to_weth"]                           Swap on the website Dyor from the ETH token to WETH token on the Ink network
    ["swap_dyor_eth_to_worm"]                           Swap on the website Dyor from the ETH token to WORM token on the Ink network
    ["swap_dyor_weth_to_eth"]                           Swap on the website Dyor from the WETH token to ETH token on the Ink network
    ["swap_dyor_usdc_to_eth"]                           Swap on the website Dyor from the USDC token to ETH token on the Ink network
    ["swap_dyor_usdt_to_eth"]                           Swap on the website Dyor from the USDT token to ETH token on the Ink network
    ["swap_dyor_worm_to_eth"]                           Swap on the website Dyor from the WORM token to ETH token on the Ink network
    ["swap_dyor_kraken_to_eth"]                         Swap on the website Dyor from the KRAKEN token to ETH token on the Ink network
    ["swap_dyor_kraken_to_worm"]                        Swap on the website Dyor from the KRAKEN token to WORM token on the Ink network
    ["swap_dyor_worm_to_kraken"]                        Swap on the website Dyor from the WORM token to KRAKEN token on the Ink network
    ["swap_dyor_worm_to_usdt"]                          Swap on the website Dyor from the WORM token to USDT token on the Ink network
    ["swap_dyor_worm_to_usdc"]                          Swap on the website Dyor from the WORM token to USDC token on the Ink network
    ["swap_dyor_worm_to_weth"]                          Swap on the website Dyor from the WORM token to WETH token on the Ink network
    ["swap_dyor_kraken_to_weth"]                        Swap on the website Dyor from the KRAKEN token to WETH token on the Ink network
    ["swap_dyor_kraken_to_usdc"]                        Swap on the website Dyor from the KRAKEN token to USDC token on the Ink network
    ["swap_dyor_usdc_to_kraken"]                        Swap on the website Dyor from the USDC token to KRAKEN token on the Ink network
    ["swap_dyor_usdc_to_worm"]                          Swap on the website Dyor from the USDC token to WORM token on the Ink network
    ["swap_dyor_usdc_to_usdt"]                          Swap on the website Dyor from the USDC token to USDT token on the Ink network
    ["swap_dyor_usdc_to_weth"]                          Swap on the website Dyor from the USDC token to WETH token on the Ink network
    ["swap_dyor_weth_to_usdt"]                          Swap on the website Dyor from the WETH token to USDT token on the Ink network
    ["swap_dyor_weth_to_usdc"]                          Swap on the website Dyor from the WETH token to USDC token on the Ink network
    ["swap_dyor_weth_to_worm"]                          Swap on the website Dyor from the WETH token to WORM token on the Ink network
    ["swap_dyor_usdt_to_weth"]                          Swap on the website Dyor from the USDT token to WETH token on the Ink network
    ["swap_dyor_weth_to_kraken"]                        Swap on the website Dyor from the WETH token to KRAKEN token on the Ink network
    ["swap_dyor_usdt_to_usdc"]                          Swap on the website Dyor from the USDT token to USDC token on the Ink network
    ["swap_dyor_usdt_to_worm"]                          Swap on the website Dyor from the USDT token to WORM token on the Ink network
    ["swap_dyor_usdt_to_kraken"]                        Swap on the website Dyor from the USDT token to KRAKEN token on the Ink network
    ["swap_dyor_kraken_to_usdt"]                        Swap on the website Dyor from the KRAKEN token to USDT token on the Ink network

    *** Add Liquidity DyorSwap https://dyorswap.finance/liquidity ***

    ["add_liquidity_dyor_eth_and_usdc"]                 Add Liquidity on the website Dyor from the ETH token and USDC token on the Ink network
    ["add_liquidity_dyor_eth_and_usdt"]                 Add Liquidity on the website Dyor from the ETH token and USDT token on the Ink network
    ["add_liquidity_dyor_eth_and_kraken"]               Add Liquidity on the website Dyor from the ETH token and KRAKEN token on the Ink network
    ["add_liquidity_dyor_eth_and_worm"]                 Add Liquidity on the website Dyor from the ETH token and WORM token on the Ink network

    *** Mint NFTs ***

    ["mint_paragraf_nft"]                               Mint nft "Paragraf" on the Ink network
    ["mint_og_nft"]                                     Mint nft "OG" on the Ink network
    ["mint_guild_nft"]                                  Mint nft "Guild Pin" on the Ink network    

    ["deploy_contract_ink_network"]                     Deploy contract on the Ink network

    ["buy_znc_domen_ink_network"]                       Buy ZNC domen on the Ink network
    
    ["claim_daily_gm"]                                  Claim Daily GM on the Ink network

]

"""

CLASSIC_WITHDRAW_DEPENDENCIES = True # if True, then it would be possible to withdraw from the bridge where we made adding liquidity


CLASSIC_ROUTES_MODULES_USING: List[List[str]] = [
    "swap_dyor_eth_to_usdc",
    "mint_paragraf_nft",
    "mint_og_nft",
    "mint_guild_nft",
    "deploy_contract_ink_network",
    "buy_znc_domen_ink_network",
    "claim_daily_gm",
]

ROUTES_MODULES_GENERALS_SWAPS: List[List[str]] = [
    "swap_dyor_eth_to_kraken",
    "swap_dyor_eth_to_usdt",
    "swap_dyor_eth_to_weth",
    "swap_dyor_eth_to_usdc",
    "swap_dyor_eth_to_worm"
]

""" Networks which we work with """
PRIORITY_NETWORK_NAMES: Set[str] = {
    "Ink Mainnet",
}

NETWORK_TOKEN_CONTRACTS: Dict[str, Dict[str, str]] = {
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