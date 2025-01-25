import time
import random

from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client, CustomAsyncWeb3
from data.abi import DYOR_ABI, FACTORY_DYOR_ABI, SWAP_TOKEN_ABI
from modules.interfaces import *
from settings import NETWORK_TOKEN_CONTRACTS

logger: Logger = Logger().get_logger()


address_contract_dyor: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
    '0x9b17690de96fcfa80a3acaefe11d936629cd7a77'
)

address_contract_dyor_factory: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(
    '0x6c86ab200661512fDBd27Da4Bb87dF15609A2806'
)

async def approve(
        client: Client, token_out_name: str, amount_out: int, address_contract: ChecksumAddress = None,
        spender_address: ChecksumAddress = address_contract_dyor
    ):
    address_contract = CustomAsyncWeb3.to_checksum_address(NETWORK_TOKEN_CONTRACTS.get(client.network.name, {}).get(token_out_name, ""))

    contract: AsyncContract = client.w3.eth.contract(
        address=address_contract,
        abi=SWAP_TOKEN_ABI
    )

    allowance = await contract.functions.allowance(client.address, spender_address).call()

    if allowance > amount_out: return True

    contract: AsyncContract = client.w3.eth.contract(
        address=address_contract,
        abi=SWAP_TOKEN_ABI
    )

    try:
        tx_params = await client.prepare_transaction()
        transaction = await contract.functions.approve(
            CustomAsyncWeb3.to_checksum_address(spender_address),
            115792089237316195423570985008687907853269984665640564039457584007913129639935                           
        ).build_transaction(tx_params)
        await client.send_transaction(transaction, need_hash=True)
    except Exception as error:
        logger.error(
            f'{client.name} Failed approve {token_out_name}. Error: {error}'
        )

async def canculate_amount_token_desired(
        client: Client, token_desired_name: str, min_available_balance_out_token: float, min_clearance: float
    ):
    balance = await client.get_token_balance(token_name=token_desired_name)      
    decimals = await client.get_decimals(token_name=token_desired_name)

    value = 0 if balance is None else balance / 10 ** decimals

    if value < min_available_balance_out_token or value - min_available_balance_out_token < min_clearance:
        logger.warning(
            f'{client.name} Skip the add liquidity {token_desired_name} and ETH on the Ink network, because you have a minimum number of {token_desired_name} tokens '
            f'Needed: {min_available_balance_out_token} you have: {value}'
        )
        return None
        
    free_amount = value - min_available_balance_out_token

    if free_amount < min_clearance:
        percent = 100
    else:
        percent = random.randint(50, 100)

    amount_out = round(free_amount * (1 - percent / 100), random.randint(2, 4))

    if amount_out < min_clearance:
        amount_out = (random.randint(int(min_clearance * 10 ** decimals), int(free_amount * 10 ** decimals)) / 10 ** decimals)

    return amount_out, decimals

async def parameter_calculation(
        client: Client, amount_token_desired: int, token_a_name: str, token_b_name: str = "WETH",  
    ):
    contract_factory: AsyncContract = client.w3.eth.contract(
        address=address_contract_dyor_factory,
        abi=FACTORY_DYOR_ABI
    )
    contract_a: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(NETWORK_TOKEN_CONTRACTS.get(client.network.name, {}).get(token_a_name, ""))
    contract_b: ChecksumAddress = CustomAsyncWeb3.to_checksum_address(NETWORK_TOKEN_CONTRACTS.get(client.network.name, {}).get(token_b_name, ""))
    pair_address = await contract_factory.functions.getPair(contract_a, contract_b).call()

    pair_contract = client.w3.eth.contract(
        address=CustomAsyncWeb3.to_checksum_address(pair_address),
        abi=FACTORY_DYOR_ABI
    )
    reserves_a, reserves_b, _ = await pair_contract.functions.getReserves().call()

    contract: AsyncContract = client.w3.eth.contract(
        address=address_contract_dyor,
        abi=DYOR_ABI
    )
    
    amount_eth_min = await contract.functions.quote(
        int(amount_token_desired),
        int(reserves_b),
        int(reserves_a)
    ).call()

    decimals = await client.get_decimals(token_name=token_b_name)
    
    amount_eth_min_float = float(amount_eth_min / 10 ** decimals)

    return amount_eth_min, amount_eth_min_float


class AddLiquidityDyorETHtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: AddLiquidityDyorETHtoUSDCModule):
        super().__init__()

        self.client: Client = client
        self.module_info: AddLiquidityDyorETHtoUSDCModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_token_desired(
            client=self.client, token_desired_name="USDC", min_available_balance_out_token=1.0, min_clearance=0.5
        )

        if result is None: return 

        amount_token_desired_float, decimals = result

        await approve(
            client=self.client, token_out_name='USDC', amount_out=int(amount_token_desired_float * 10 ** decimals)
        )       

        amount_token_desired = int(amount_token_desired_float * 10 ** decimals)

        slippage_tolerance = 0.005
        amount_token_min = int(amount_token_desired * (1 - slippage_tolerance))

        amount_eth_min, amount_eth_min_float = await parameter_calculation(
            client=self.client, amount_token_desired=amount_token_desired, token_a_name="USDC"
        )

        self.logger.info(
            f'{self.client.name} Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} USDC.e on the Ink network'
        )

        address_token: ChecksumAddress = CustomAsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14")

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor,
            abi=DYOR_ABI
        )
        try:
            tx_params = await self.client.prepare_transaction(value=amount_eth_min)
            transaction = await contract.functions.addLiquidityETH(
                address_token,
                amount_token_desired,
                amount_token_min,
                amount_eth_min,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} USDC.e on the Ink network. Error: {error} '
            )


class AddLiquidityDyorETHtoUSDTWorker(Logger):
    def __init__(self, client: Client, module_info: AddLiquidityDyorETHtoUSDTModule):
        super().__init__()

        self.client: Client = client
        self.module_info: AddLiquidityDyorETHtoUSDTModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_token_desired(
            client=self.client, token_desired_name="USDT", min_available_balance_out_token=1.0, min_clearance=0.5
        )

        if result is None: return 

        amount_token_desired_float, decimals = result

        await approve(
            client=self.client, token_out_name='USDT', amount_out=int(amount_token_desired_float * 10 ** decimals)
        )       

        amount_token_desired = int(amount_token_desired_float * 10 ** decimals)

        slippage_tolerance = 0.005
        amount_token_min = int(amount_token_desired * (1 - slippage_tolerance))

        amount_eth_min, amount_eth_min_float = await parameter_calculation(
            client=self.client, amount_token_desired=amount_token_desired, token_a_name="USDT"
        )

        self.logger.info(
            f'{self.client.name} Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} USDT on the Ink network'
        )

        address_token: ChecksumAddress = CustomAsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1")

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor,
            abi=DYOR_ABI
        )
        try:
            tx_params = await self.client.prepare_transaction(value=amount_eth_min)
            transaction = await contract.functions.addLiquidityETH(
                address_token,
                amount_token_desired,
                amount_token_min,
                amount_eth_min,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} USDT on the Ink network. Error: {error} '
            )


class AddLiquidityDyorETHtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: AddLiquidityDyorETHtoKRAKENModule):
        super().__init__()

        self.client: Client = client
        self.module_info: AddLiquidityDyorETHtoKRAKENModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_token_desired(
            client=self.client, token_desired_name="KRAKEN", min_available_balance_out_token=100_000.0, min_clearance=20_000.0
        )

        if result is None: return 

        amount_token_desired_float, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_token_desired_float * 10 ** decimals)
        )       

        amount_token_desired = int(amount_token_desired_float * 10 ** decimals)

        slippage_tolerance = 0.005
        amount_token_min = int(amount_token_desired * (1 - slippage_tolerance))

        amount_eth_min, amount_eth_min_float = await parameter_calculation(
            client=self.client, amount_token_desired=amount_token_desired, token_a_name="KRAKEN"
        )

        self.logger.info(
            f'{self.client.name} Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} KRAKEN on the Ink network'
        )

        address_token: ChecksumAddress = CustomAsyncWeb3.to_checksum_address("")

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor,
            abi=DYOR_ABI
        )
        try:
            tx_params = await self.client.prepare_transaction(value=amount_eth_min)
            transaction = await contract.functions.addLiquidityETH(
                address_token,
                amount_token_desired,
                amount_token_min,
                amount_eth_min,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} KRAKEN on the Ink network. Error: {error} '
            )


class AddLiquidityDyorETHtoWORMWorker(Logger):
    def __init__(self, client: Client, module_info: AddLiquidityDyorETHtoWORMModule):
        super().__init__()

        self.client: Client = client
        self.module_info: AddLiquidityDyorETHtoWORMModule = module_info
        self.destination_network: str | None = module_info.destination_network
        self.source_network: str | None = module_info.source_network
        self.source_network_chain_id: int | None = module_info.source_network_chain_id
        self.destination_network_chain_id: int | None = module_info.destination_network_chain_id
        self.module_priority: int | None = module_info.module_priority
        self.module_name: str | None = module_info.module_name
        self.module_display_name: str | None = module_info.module_display_name

        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_token_desired(
            client=self.client, token_desired_name="WORM", min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )

        if result is None: return 

        amount_token_desired_float, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_token_desired_float * 10 ** decimals)
        )       

        amount_token_desired = int(amount_token_desired_float * 10 ** decimals)

        slippage_tolerance = 0.005
        amount_token_min = int(amount_token_desired * (1 - slippage_tolerance))

        amount_eth_min, amount_eth_min_float = await parameter_calculation(
            client=self.client, amount_token_desired=amount_token_desired, token_a_name="WORM"
        )

        self.logger.info(
            f'{self.client.name} Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} WORM on the Ink network'
        )

        address_token: ChecksumAddress = CustomAsyncWeb3.to_checksum_address("")

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor,
            abi=DYOR_ABI
        )
        try:
            tx_params = await self.client.prepare_transaction(value=amount_eth_min)
            transaction = await contract.functions.addLiquidityETH(
                address_token,
                amount_token_desired,
                amount_token_min,
                amount_eth_min,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the Add Liquidity {amount_eth_min_float} ETH and {amount_token_desired_float} WORM on the Ink network. Error: {error} '
            )