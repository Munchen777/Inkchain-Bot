"""
Handle installation of classic route.
You can specify modules that will be used in the classic route.

CLASSIC_ROUTES_MODULES_USING = [
    ["bridge_native"],
]

"""

CLASSIC_WITHDRAW_DEPENDENCIES = True # if True, then it would be possible to withdraw from the bridge where we made adding liquidity

CLASSIC_ROUTES_MODULES_USING = [
    ["bridge_native"],
    ["bridge_owlto_op_to_ink"],
    
]

NETWORK_TOKEN_CONTRACTS = {
    "": ""
}
