from typing import Dict, List


class Network:
    def __init__(
            self,
            name: str,
            rpc: List[str],
            chain_id: int,
            eip1559_support: bool,
            token: str,
            explorer: str,
            decimals: int = 18
    ):
        self.name: str = name
        self.rpc: List[str] = rpc
        self.chain_id: int = chain_id
        self.eip1559_support: bool = eip1559_support
        self.token: str = token
        self.explorer: str = explorer
        self.decimals: int = decimals


Ethereum = Network(
    name='Ethereum Mainnet',
    rpc=[
        'https://eth.llamarpc.com',
        'https://uk.rpc.blxrbdn.com',
        'https://virginia.rpc.blxrbdn.com',
        'https://eth.meowrpc.com',
        'https://singapore.rpc.blxrbdn.com'
    ],
    chain_id=1,
    eip1559_support=True,
    token='ETH',
    explorer='https://etherscan.io/',
)

Ink = Network(
    name='Ink Mainnet',
    rpc=[
        'https://rpc-qnd.inkonchain.com'
    ],
    chain_id=57073,
    eip1559_support=True,
    token='ETH',
    explorer='https://explorer.inkonchain.com/',
)

Base = Network(
    name='Base Mainnet',
    rpc=[
        "https://base.llamarpc.com",
        "https://base.drpc.org",
    ],
    chain_id=8453,
    eip1559_support=True,
    token='ETH',
    explorer='https://basescan.org/',
)

OP = Network(
    name='OP Mainnet',
    rpc=[
        "https://optimism.drpc.org",
    ],
    chain_id=10,
    eip1559_support=True,
    token='ETH',
    explorer='https://optimistic.etherscan.io/',
)
