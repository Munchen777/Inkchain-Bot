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
    explorer='https://explorer-sepolia.inkonchain.com',
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
    explorer='ttps://explorer.inkonchain.com/',
)
