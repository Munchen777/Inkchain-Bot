import asyncio
import random
import aiohttp

from typing import Any, Dict, List
from web3.eth.async_eth import ChecksumAddress
from web3.contract import AsyncContract
from web3.exceptions import TransactionNotFound
from web3 import AsyncHTTPProvider, AsyncWeb3

from .networks import NETWORKS
from utils.networks import *
from modules import Logger
from data.abi import ERC20_ABI
from settings import NETWORK_TOKEN_CONTRACTS, UNISWAP_V2_ROUTER_CONTRACT_ADDRESS
from generall_settings import RANDOM_RANGE, ROUNDING_LEVELS


class BlockchainException(Exception):
    pass


class SoftwareException(Exception):
    pass


class CustomAsyncHTTPProvider(AsyncHTTPProvider):
    def __init__(self, endpoint_uri, *args, **kwargs):
        super().__init__(endpoint_uri, *args, **kwargs)
        self._session = None

    @property
    async def session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def make_request(self, method, params):
        async with await self.session as session:
            async with session.post(self.endpoint_uri, json={"jsonrpc": "2.0", "method": method, "params": params, "id": 1}) as response:
                return await response.json()

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def __del__(self):
        if self._session and not self._session.closed:
            import asyncio
            asyncio.create_task(self.close())


class CustomAsyncWeb3(AsyncWeb3):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.provider, "close") and callable(self.provider.close):
            await self.provider.close()


class Client(Logger):
    def __init__(self, account_name: str, private_key: str, proxy: str = None, source_network: str = None):
        super().__init__()
        self.name: str = account_name
        self.private_key: str = private_key
        self.proxy_init: str = proxy
        self.request_kwargs = {"proxy": f'{self.proxy_init}', "verify_ssl": False} if self.proxy_init else {"verify_ssl": False}
        self.w3 = CustomAsyncWeb3(CustomAsyncHTTPProvider(None, request_kwargs=self.request_kwargs))
        self.address = CustomAsyncWeb3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)

        if source_network:
            self.setup_network(source_network)

    def get_network(self, network_name: str) -> Network | None:
        return NETWORKS.get(network_name) or None

    def setup_network(self, network_name: str):
        network: Network | None = self.get_network(network_name)
        if not network:
            self.logger_msg(self.name, self.address, f"The network named '{network_name}' was not found", "error")
            raise ValueError

        self.network: Network = network
        self.rpc: str = random.choice(self.network.rpc)
        self.request_kwargs: Dict[str, str] | None = {
            "proxy": f'{self.proxy_init}',
            "verify_ssl": False
            } if self.proxy_init else {"verify_ssl": False}
        self.w3 = CustomAsyncWeb3(CustomAsyncHTTPProvider(self.rpc, request_kwargs=self.request_kwargs))

    async def get_value_and_normalized_value(
        self, normalized_fee: float, normalized_min_available_balance: float, 
        normalized_min_amount_out: float, normalized_min_amount_residue: float
        ) -> tuple[int, float] | None:
        """
        Метод для автоматического расчёта value для мостов Л2.
        """
        balance = await self.get_token_balance(check_native=True)

        if not await self._has_sufficient_balance(
            balance, normalized_min_available_balance, "ETH", True
        ):
            return None

        return await self._calculate_value(
            balance, normalized_min_amount_out, normalized_min_amount_residue,
            "ETH", True, normalized_fee
        )

    async def _has_sufficient_balance(
        self, balance: int, normalized_min_available_balance: float,
        token_name: str, check_native: bool
    ) -> bool:
        """
        Проверяет, достаточно ли баланса.
        """
        if balance is None:
            self.logger.warning(
                f"{self.name} | Balance not found for address: {self.address}. "
                f"Most likely, the balance is completely empty."
            )
            return False

        decimals = await self.get_decimals(token_name, check_native)
        min_balance = normalized_min_available_balance / decimals

        if balance < min_balance:
            self.logger.warning(
                f"{self.name} | Insufficient {self.network.token} balance for transaction "
                f"on network {self.network.name}. Address: {self.address}. "
                f"Minimum required: {normalized_min_available_balance} {self.network.token}."
            )
            return False

        return True

    async def _calculate_value(
        self, balance: int, normalized_min_amount_out: float, normalized_min_amount_residue: float,
        token_name: str, check_native: bool, normalized_fee: float,
        random_range: tuple[float, float] = RANDOM_RANGE, 
        rounding_levels: tuple[int, int] = ROUNDING_LEVELS
    ) -> tuple[int, float]:
        """
        Расчёт значений для моста.
        """
        decimals = await self.get_decimals(token_name, check_native)
        
        # Нормализуем минимальные значения для отправки и остатка
        min_out = normalized_min_amount_out + normalized_fee
        min_residue = normalized_min_amount_residue

        # Нормализуем баланс (переводим в читаемое значение)
        free_amount = balance / (10 ** decimals) - min_residue  # Преобразуем balance в читаемое значение

        if free_amount < min_out:
            self.logger.warning(
                f"{self.name} | Insufficient {self.network.token} for the bridge "
                f"Balance: {balance / (10 ** decimals)} {self.network.token} "
                f"on network {self.network.name}. Address: {self.address}. "
                f"Free tokens: {free_amount:.6f} {self.network.token}, "
                f"is required for a transaction: {normalized_min_amount_out:.6f} {self.network.token}"
            )
            return None

        # Генерируем случайное значение в пределах заданного диапазона
        random_percent = random.uniform(*random_range)
        normalized_value = round(
            free_amount * random_percent + normalized_min_amount_out,
            random.randint(*rounding_levels)
        )
        
        # Переводим обратно в минимальные единицы (например, wei для ETH)
        value = int(normalized_value * (10 ** decimals))

        return value, normalized_value
       
    @staticmethod
    def get_normalize_error(error: Exception) -> Exception | str:
        try:
            if isinstance(error.args[0], dict):
                error = error.args[0].get('message', error)
            return error
        except:
            return error
    
    @staticmethod
    def get_user_agent() -> str:
        chrome_version = f"{random.randint(90, 121)}.0.{random.randint(1000, 9999)}.{random.randint(0, 99)}"
        safari_version = f"{random.uniform(600, 610):.2f}"
        return (f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{safari_version} '
                f'(KHTML, like Gecko) Chrome/{chrome_version} Safari/{safari_version}')
    
    async def get_contract(self, contract_address: str, abi: dict = ERC20_ABI) -> AsyncContract:
        return self.w3.eth.contract(
            address=CustomAsyncWeb3.to_checksum_address(contract_address),
            abi=abi
        )
        
    async def get_decimals(self, token_name: str = None, check_native: bool = False) -> int:
        if check_native or token_name == "ETH":
            return 18
        contract: AsyncContract = await self.get_contract(NETWORK_TOKEN_CONTRACTS.get(self.network.name, {}).get(token_name, ""))
        return await contract.functions.decimals().call()
    
    async def get_normalize_amount(self, token_name: str, amount_in_wei: int) -> float:
        decimals = await self.get_decimals(token_name)
        return float(amount_in_wei / 10 ** decimals)

    async def get_token_balance(self, token_name: str = None, check_native: bool = False) -> int | None:
        try:
            if check_native:
                token_balance = await self.w3.eth.get_balance(self.address)
                return token_balance or None

            contract: AsyncContract = await self.get_contract(NETWORK_TOKEN_CONTRACTS.get(self.network.name, {}).get(token_name, ""))
            token_balance = await contract.functions.balanceOf(self.address).call()
            return token_balance or None

        except Exception as error:
            self.logger_msg(self.name, self.address, f"Error while receiving token balance.\nError: {error}", "error")
            return None

    async def get_allowance(self, token_address: str, spender_address: str) -> int:
        contract = await self.get_contract(token_address)
        return await contract.functions.allowance(
            self.address,
            spender_address
        ).call()
    
    async def get_priotiry_fee(self):
        fee_history = await self.w3.eth.fee_history(25, 'latest', [20.0])
        non_empty_block_priority_fees = [fee[0] for fee in fee_history["reward"] if fee[0] != 0]

        if not non_empty_block_priority_fees:
            return 1

        divisor_priority = max(len(non_empty_block_priority_fees), 1)
        priority_fee = int(round(sum(non_empty_block_priority_fees) / divisor_priority))
        return max(priority_fee, 1)

    async def prepare_transaction(self, value: int = 0, eip1559: bool = True):
        try:
            tx_params = {
                'from': self.address,
                'nonce': await self.w3.eth.get_transaction_count(self.address),
                'value': value,
                'chainId': self.network.chain_id
            }
            if self.network.eip1559_support and eip1559:
                base_fee = await self.w3.eth.gas_price
                max_priority_fee_per_gas = max(await self.get_priotiry_fee(), 1)
                max_fee_per_gas = base_fee + max_priority_fee_per_gas

                min_fee = 1_000_000_000
                tx_params['maxPriorityFeePerGas'] = max(max_priority_fee_per_gas, min_fee)
                tx_params['maxFeePerGas'] = max(int(max_fee_per_gas), tx_params['maxPriorityFeePerGas'] + min_fee)
                tx_params['type'] = '0x2'
            else:
                tx_params['gasPrice'] = int(await self.w3.eth.gas_price)

            return tx_params
        except Exception as error:
            raise BlockchainException(f'{self.get_normalize_error(error)}')
        
    async def send_transaction(self, transaction, need_hash: bool = False, without_gas: bool = False,
                            poll_latency: int = 10, timeout: int = 360, test_mode: bool = False):
        if test_mode:
            try:
                result = await self.w3.eth.call(transaction)
                self.logger.info(f"The transaction simulation was successful: {result}")
                return True
            except Exception as error:
                self.logger.error(f"The transaction simulation failed: {self.get_normalize_error(error)}")
                return False
        else:
            try:
                if not without_gas:
                    transaction['gas'] = int(await self.w3.eth.estimate_gas(transaction))
            except Exception as error:
                self.logger.error(f"The transaction simulation failed: {self.get_normalize_error(error)}")
                return False

            try:
                singed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)
                tx_hash = await self.w3.eth.send_raw_transaction(singed_tx.raw_transaction)
            except Exception as error:
                if self.get_normalize_error(error) == 'transaction underpriced':
                    self.logger.warning("The commission is understated. Increase and repeat shipment....")
                    transaction['maxPriorityFeePerGas'] = transaction.get('maxPriorityFeePerGas', 1_000_000_000) + 1_000_000_000
                    transaction['maxFeePerGas'] = transaction['maxPriorityFeePerGas'] + await self.w3.eth.gas_price
                    return await self.send_transaction(transaction, need_hash, without_gas, poll_latency, timeout, test_mode)
                if self.get_normalize_error(error) == 'already known':
                    self.logger.warning(f'RPC received an error, but the tx was sent | {self.address}')
                    return True
                else:
                    self.logger.error(f"Transaction sending error: {self.get_normalize_error(error)}")
                    return False
            try:
                total_time = 0
                timeout = 1200
                while True:
                    try:
                        receipts = await self.w3.eth.get_transaction_receipt(tx_hash)
                        status = receipts.get("status")
                        
                        if status == 1:
                            self.logger.info(f'The transaction was successful: {self.network.explorer}/tx/0x{tx_hash.hex()} | {self.address}')
                            return True
                        elif status is None:
                            await asyncio.sleep(poll_latency)
                        else:
                            self.logger.error(f'The transaction failed: {self.network.explorer}/tx/0x{tx_hash.hex()}')
                            return False

                    except TransactionNotFound:
                        if total_time > timeout:
                            self.logger.error(f"Transaction is missing from the chain after {timeout} seconds")
                            return False
                        
                        total_time += poll_latency
                        await asyncio.sleep(poll_latency)

                    except Exception as error:
                        self.logger.error(f'RPC received an automated response. Error: {error} | {self.address}')
                        total_time += poll_latency
                        await asyncio.sleep(poll_latency)

            except Exception as error:
                self.logger.error(f'Error during transaction processing: {self.get_normalize_error(error)}')
                return False

    async def get_wallet_balance(self, balance_in_eth: bool = False) -> Dict[str, Dict[str, float]]:
        """ Method to get all wallet balances in all networks """
        wallet_balances: Dict[str, Dict[str, float]] = {}

        for network_name, network in NETWORKS.items():
            try:
                provider = CustomAsyncHTTPProvider(random.choice(network.rpc), request_kwargs=self.request_kwargs)

                async with CustomAsyncWeb3(provider) as w3:
                    network_token_contracts: Dict[str, str] | None = NETWORK_TOKEN_CONTRACTS.get(network_name)

                    if not network_token_contracts:
                        token_name: str = "ETH"
                        native_token_balance: float | None = await w3.eth.get_balance(self.address)

                        if not native_token_balance:
                            self.logger_msg(self.name, self.address,
                                            f"Native balance {token_name} not found in {network_name} network.", "warning")
                            continue

                        wallet_balances.setdefault(network_name, {})[token_name] = native_token_balance / (10**18)

                    if network_token_contracts:
                        for token_name, contract_address in network_token_contracts.items():
                            if not contract_address:
                                self.logger_msg(self.name, self.address,
                                    f"{token_name} token contract address not found for token in {network_name} network", "warning")
                                continue

                            contract: AsyncContract = await self.get_contract(contract_address)

                            balance_token = await contract.functions.balanceOf(self.address).call()
                            decimals = await contract.functions.decimals().call()
                            balance_token_readable: float = balance_token / (10 ** decimals)

                            if balance_in_eth:
                                uniswap_v2_router: AsyncContract = w3.eth.contract(
                                    address=AsyncWeb3.to_checksum_address(UNISWAP_V2_ROUTER_CONTRACT_ADDRESS),
                                    abi=ERC20_ABI,
                                )
                                path: List[ChecksumAddress] = [
                                    AsyncWeb3.to_checksum_address(
                                        contract_address
                                    ),
                                    AsyncWeb3.to_checksum_address(
                                        network_token_contracts.get("WETH") or network_token_contracts.get("ETH")
                                    ),
                                ]
                                try:
                                    src_token_amount, amountOut = uniswap_v2_router.functions.getAmountsOut(
                                        balance_token, path
                                    ).call()

                                except Exception as error:
                                    self.logger_msg(self.name, self.address,
                                                    f"Occured an error while getting {token_name} balance it ether\nError: {error}", "warning")
                                    continue

                                wallet_balances.setdefault(network_name, {})[token_name] = amountOut

                            else:
                                wallet_balances.setdefault(network_name, {})[token_name] = balance_token_readable

            except Exception as error:
                self.logger_msg(self.name, self.address,
                                f"Error while making request to find token balances for {self.name} account", "error")
                raise error

        return wallet_balances
