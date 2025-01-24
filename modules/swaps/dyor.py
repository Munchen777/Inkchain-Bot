import time
import random

from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.contract.async_contract import AsyncContract
from web3.eth.async_eth import ChecksumAddress

from modules import *
from utils.client import Client
from data.abi import DYOR_ABI, WRAPED_ETH_ABI, SWAP_TOKEN_ABI
from modules.interfaces import *
from settings import NETWORK_TOKEN_CONTRACTS


logger: Logger = Logger().get_logger()


address_contract_dyor_swap: ChecksumAddress = AsyncWeb3.to_checksum_address(
    '0x9b17690de96fcfa80a3acaefe11d936629cd7a77'
)

async def approve(
        client: Client, token_out_name: str, amount_out: int, address_contract: ChecksumAddress = None,
        spender_address: ChecksumAddress = address_contract_dyor_swap
    ):
    address_contract = AsyncWeb3.to_checksum_address(NETWORK_TOKEN_CONTRACTS.get(client.network.name, {}).get(token_out_name, ""))

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
            AsyncWeb3.to_checksum_address(spender_address),
            115792089237316195423570985008687907853269984665640564039457584007913129639935                           
        ).build_transaction(tx_params)
        await client.send_transaction(transaction, need_hash=True)
    except Exception as error:
        logger.error(
            f'{client.name} Failed approve {token_out_name}. Error: {error}'
        )

async def canculate_amount_out_swaps(
        client: Client, token_out_name: str, token_get_name: str, min_available_balance_out_token: float,
        min_clearance: float, from_weth: bool = False
    ):
    balance = await client.get_token_balance(token_name=token_out_name)      
    decimals = await client.get_decimals(token_name=token_out_name)

    value = 0 if balance is None else balance / 10 ** decimals

    if value < min_available_balance_out_token or value - min_available_balance_out_token < min_clearance:
        logger.warning(
            f'{client.name} Skip the swap {token_out_name} to {token_get_name} on the Ink network, because you have a minimum number of {token_out_name} tokens '
            f'Needed: {min_available_balance_out_token} you have: {value}'
        )
        return None
        
    free_amount = value - min_available_balance_out_token

    if free_amount < min_clearance:
        percent = 100
    else:
        percent = random.randint(50, 100)

    if from_weth:
        amount_out = round(free_amount * (1 - percent / 100), random.randint(4, 6))
    else:
        amount_out = round(free_amount * (1 - percent / 100), random.randint(2, 4))

    if amount_out < min_clearance:
        amount_out = (random.randint(int(min_clearance * 10 ** decimals), int(free_amount * 10 ** decimals)) / 10 ** decimals)

    return amount_out, decimals


class SwapDyorETHtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorETHtoUSDCModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorETHtoUSDCModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        balance = await self.client.get_token_balance(token_name='USDC')
        decimals = await self.client.get_decimals(token_name='USDC')

        if balance is not None:
            if balance / 10 ** decimals > 1: 
                self.logger.warning(
                    f"{self.client.name} The balance is over 1 USDC.e which is enough for the job, so I'll swap out"
                )
                return

        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None: return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Swap {balance} ETH to USDC.e on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14")
        ]
        slippage_tolerance = 0.005

        amounts_out = await contract.functions.getAmountsOut(value, path).call()

        amount_out_min = int(amounts_out[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to USDC.e on the Ink network. Error: {error} '
            )


class SwapDyorETHtoKrakenWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorETHtoKrakenModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorETHtoKrakenModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None: return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Swap {balance} ETH to Kraken on the Ink network'
        )      

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.005

        amounts_out = await contract.functions.getAmountsOut(value, path).call()

        amount_out_min = int(amounts_out[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to Kraken on the Ink network. Error: {error} '
            )


class SwapDyorETHtoUSDTWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorETHtoUSDTModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorETHtoUSDTModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None: return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Swap {balance} ETH to USDT on the Ink network'
        )      

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1")
        ]
        slippage_tolerance = 0.005

        amounts_out = await contract.functions.getAmountsOut(value, path).call()

        amount_out_min = int(amounts_out[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to USDT on the Ink network. Error: {error} '
            )


class SwapDyorETHtoWETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorETHtoWETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorETHtoWETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None: return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Swap {balance} ETH to WETH on the Ink network'
        )      

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0x4200000000000000000000000000000000000006'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=WRAPED_ETH_ABI
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.deposit().build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to WETH on the Ink network. Error: {error} '
            )


class SwapDyorETHtoWORMWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorETHtoWORMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorETHtoWORMModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await self.client.get_value_and_normalized_value(
            normalized_fee=self.module_info.fee,
            normalized_min_available_balance=self.module_info.min_available_balance,
            normalized_min_amount_out=self.module_info.min_amount_out,
            normalized_min_amount_residue=self.module_info.min_amount_residue
        )

        if result is None: return

        value, balance = result

        self.logger.info(
            f'{self.client.name} Swap {balance} ETH to WORM on the Ink network'
        )      

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01")
        ]
        slippage_tolerance = 0.005

        amounts_out = await contract.functions.getAmountsOut(value, path).call()

        amount_out_min = int(amounts_out[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction(value=value)
            transaction = await contract.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap ETH to WORM on the Ink network. Error: {error} '
            )


class SwapDyorWETHtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWETHtoETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWETHtoETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WETH', token_get_name='ETH',
            min_available_balance_out_token=0.0003, min_clearance=0.00001, from_weth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WETH to ETH on the Ink network'
        )      
        
        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0x4200000000000000000000000000000000000006'
        )

        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract,
            abi=WRAPED_ETH_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.withdraw(
                amount_out
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WETH to ETH on the Ink network. Error: {error} '
            )


class SwapDyorUSDCtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDCtoETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDCtoETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDC', token_get_name='ETH',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDC', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDC.e to ETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDC.e to ETH on the Ink network. Error: {error} '
            )


class SwapDyorUSDTtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDTtoETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDTtoETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDT', token_get_name='ETH',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDT', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDT to ETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDT to ETH on the Ink network. Error: {error} '
            )


class SwapDyorWORMtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWORMtoETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWORMtoETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WORM', token_get_name='ETH',
            min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WORM to ETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WORM to ETH on the Ink network. Error: {error} '
            )


class SwapDyorKRAKENtoETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorKRAKENtoETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorKRAKENtoETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='ETH',
            min_available_balance_out_token=100_000.0, min_clearance=20_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to ETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to ETH on the Ink network. Error: {error} '
            )


class SwapDyorKRAKENtoWORMWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorKRAKENtoWORMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorKRAKENtoWORMModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='WORM',
            min_available_balance_out_token=100_000.0, min_clearance=20_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to WORM on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to WORM on the Ink network. Error: {error} '
            )


class SwapDyorWORMtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWORMtoKRAKENModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWORMtoKRAKENModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WORM', token_get_name='KRAKEN',
            min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WORM to KRAKEN on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WORM to KRAKEN on the Ink network. Error: {error} '
            )


class SwapDyorWORMtoUSDTWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWORMtoUSDTModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWORMtoUSDTModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WORM', token_get_name='USDT',
            min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WORM to USDT on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WORM to USDT on the Ink network. Error: {error} '
            )


class SwapDyorWORMtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWORMtoUSDCModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWORMtoUSDCModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WORM', token_get_name='USDC',
            min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WORM to USDC on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xf1815bd50389c46847f0bda824ec8da914045d14")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WORM to USDC on the Ink network. Error: {error} '
            )


class SwapDyorWORMtoWETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWORMtoWETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWORMtoWETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WORM', token_get_name='WETH',
            min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WORM to WETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WORM to WETH on the Ink network. Error: {error} '
            )


class SwapDyorKRAKENtoWETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorKRAKENtoWETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorKRAKENtoWETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='WETH',
            min_available_balance_out_token=100_000.0, min_clearance=20_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to WETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to WETH on the Ink network. Error: {error} '
            )


class SwapDyorKRAKENtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorKRAKENtoUSDCModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorKRAKENtoUSDCModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='USDC',
            min_available_balance_out_token=100_000.0, min_clearance=20_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to USDC on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to USDC on the Ink network. Error: {error} '
            )


class SwapDyorUSDCtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDCtoKRAKENModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDCtoKRAKENModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDC', token_get_name='KRAKEN',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDC', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDC to KRAKEN on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDC to KRAKEN on the Ink network. Error: {error} '
            )


class SwapDyorUSDCtoWORMWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDCtoWORMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDCtoWORMModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDC', token_get_name='WORM',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDC', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDC to WORM on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDC to WORM on the Ink network. Error: {error} '
            )


class SwapDyorUSDCtoUSDTWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDCtoUSDTModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDCtoUSDTModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDC', token_get_name='USDT',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDC', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDC to USDT on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDC to USDT on the Ink network. Error: {error} '
            )


class SwapDyorUSDCtoWETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDCtoWETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDCtoWETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDC', token_get_name='WETH',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDC', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDC to WETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDC to WETH on the Ink network. Error: {error} '
            )


class SwapDyorWETHtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWETHtoUSDCModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWETHtoUSDCModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WETH', token_get_name='USDC',
            min_available_balance_out_token=0.0003, min_clearance=0.00001, from_weth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WETH', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WETH to USDC on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WETH to USDC on the Ink network. Error: {error} '
            )


class SwapDyorWETHtoUSDTWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWETHtoUSDTModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWETHtoUSDTModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WETH', token_get_name='USDT',
            min_available_balance_out_token=0.0003, min_clearance=0.00001, from_weth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WETH', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WETH to USDT on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WETH to USDT on the Ink network. Error: {error} '
            )


class SwapDyorWETHtoWORMWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWETHtoWORMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWETHtoWORMModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WETH', token_get_name='WORM',
            min_available_balance_out_token=0.0003, min_clearance=0.00001, from_weth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WETH', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WETH to WORM on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WETH to WORM on the Ink network. Error: {error} '
            )


class SwapDyorUSDTtoWETHWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDTtoWETHModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDTtoWETHModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDT', token_get_name='WETH',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDT', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDT to WETH on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDT to WETH on the Ink network. Error: {error} '
            )


class SwapDyorWETHtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWETHtoKRAKENModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorWETHtoKRAKENModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WETH', token_get_name='KRAKEN',
            min_available_balance_out_token=0.0003, min_clearance=0.00001, from_weth=True
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WETH', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WETH to KRAKEN on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WETH to KRAKEN on the Ink network. Error: {error} '
            )


class SwapDyorUSDTtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDTtoUSDCModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDTtoUSDCModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDT', token_get_name='USDC',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDT', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDT to USDC on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDT to USDC on the Ink network. Error: {error} '
            )


class SwapDyorWORMtoUSDCWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorWORMtoUSDCModule):
        super().__init__()
        self.client: Client = client
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='WORM', token_get_name='USDC',
            min_available_balance_out_token=350_000.0, min_clearance=100_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='WORM', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} WORM to USDC on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xF1815bd50389c46847f0Bda824eC8da914045D14")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap WORM to USDC on the Ink network. Error: {error} '
            )


class SwapDyorUSDTtoWORMWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDTtoWORMModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDTtoWORMModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDT', token_get_name='WORM',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDT', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDT to WORM on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x2dC2b752F4C6dFfe2dbcf60b848B8357a8879A01")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDT to WORM on the Ink network. Error: {error} '
            )


class SwapDyorUSDTtoKRAKENWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorUSDTtoKRAKENModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorUSDTtoKRAKENModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='USDT', token_get_name='KRAKEN',
            min_available_balance_out_token=1.0, min_clearance=0.5
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='USDT', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} USDT to KRAKEN on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap USDT to KRAKEN on the Ink network. Error: {error} '
            )


class SwapDyorKRAKENtoUSDTWorker(Logger):
    def __init__(self, client: Client, module_info: SwapDyorKRAKENtoUSDTModule):
        super().__init__()
        self.client: Client = client
        self.module_info: SwapDyorKRAKENtoUSDTModule = module_info
        self.deadline = int(time.time()) + 20 * 60

    async def run(self):            
        result = await canculate_amount_out_swaps(
            client=self.client, token_out_name='KRAKEN', token_get_name='USDT',
            min_available_balance_out_token=100_000.0, min_clearance=20_000.0
        )
        
        if result is None: return

        amount_out, decimals = result

        await approve(
            client=self.client, token_out_name='KRAKEN', amount_out=int(amount_out * 10 ** decimals)
        )

        self.logger.info(
            f'{self.client.name} Swap {amount_out} KRAKEN to USDT on the Ink network'
        )
        
        contract: AsyncContract = self.client.w3.eth.contract(
            address=address_contract_dyor_swap,
            abi=DYOR_ABI
        )

        amount_out = int(amount_out * 10 ** decimals)
        path = [
            AsyncWeb3.to_checksum_address("0xCa5f2cCBD9C40b32657dF57c716De44237f80F05"),
            AsyncWeb3.to_checksum_address("0x4200000000000000000000000000000000000006"),
            AsyncWeb3.to_checksum_address("0x0200C29006150606B650577BBE7B6248F58470c1")
        ]
        slippage_tolerance = 0.005

        amounts_in = await contract.functions.getAmountsOut(amount_out, path).call()
        amount_out_min = int(amounts_in[-1] * (1 - slippage_tolerance))
        
        try:
            tx_params = await self.client.prepare_transaction()
            transaction = await contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
                amount_out,
                amount_out_min,
                path,
                self.client.address,
                self.deadline
            ).build_transaction(tx_params)
            return await self.client.send_transaction(transaction, need_hash=True)
        except Exception as error:
            self.logger.error(
                f'{self.client.name} Failed the swap KRAKEN to USDT on the Ink network. Error: {error} '
            )