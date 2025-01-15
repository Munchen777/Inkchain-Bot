class Network:
    def __init__(
            self,
            name: str,
            rpc: list,
            chain_id: int,
            eip1559_support: bool,
            token: str,
            explorer: str,
            decimals: int = 18
    ):
        self.name = name
        self.rpc = rpc
        self.chain_id = chain_id
        self.eip1559_support = eip1559_support
        self.token = token
        self.explorer = explorer
        self.decimals = decimals

    def __repr__(self):
        return f'{self.name}'


Ethereum = Network(
    name='Ethereum Mainnet',
    rpc=[
        'wss://eth.drpc.org',
        'https://eth.llamarpc.com',
        'https://uk.rpc.blxrbdn.com',
        'https://virginia.rpc.blxrbdn.com',
        'https://rpc.ankr.com/eth',
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
        'wss://rpc-qnd.inkonchain.com',
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
        'https://base.llamarpc.com',
        'wss://base.callstaticrpc.com',
        'https://base-mainnet.public.blastapi.io',
        'wss://base.gateway.tenderly.co',
        'https://base.blockpi.network/v1/rpc/public'
    ],
    chain_id=8453,
    eip1559_support=True,
    token='ETH',
    explorer='https://basescan.org/',
)

OP = Network(
    name='OP Mainnet',
    rpc=[
        'https://optimism.llamarpc.com',
        'wss://optimism.drpc.org',
        'wss://optimism-rpc.publicnode.com',
        'https://optimism-mainnet.public.blastapi.io',
        'https://rpc.ankr.com/optimism'
    ],
    chain_id=10,
    eip1559_support=True,
    token='ETH',
    explorer='https://optimistic.etherscan.io/',
)