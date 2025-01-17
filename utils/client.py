import asyncio
import random

from typing import Dict, Set
from web3.contract import AsyncContract
from web3.exceptions import TransactionNotFound, TimeExhausted
from web3 import AsyncHTTPProvider, AsyncWeb3

from .networks import NETWORKS
from utils.networks import*
from modules import Logger
from data.abi import ERC20_ABI
from settings import NETWORK_TOKEN_CONTRACTS
from generall_settings import RANDOM_RANGE, ROUNDING_LEVELS


class BlockchainException(Exception):
    pass

class SoftwareException(Exception):
    pass


class Client(Logger):
    def __init__(self, account_name: str, private_key: str, proxy: str = None, source_network: str = None):
        super().__init__()
        self.name: str = account_name
        self.private_key: str = private_key
        self.proxy_init: str = proxy
        self.request_kwargs = {"proxy": f'{proxy}', "verify_ssl": False} if proxy else {"verify_ssl": False}
        self.w3 = AsyncWeb3(AsyncHTTPProvider(None, request_kwargs=self.request_kwargs))
        self.address = AsyncWeb3.to_checksum_address(self.w3.eth.account.from_key(private_key).address)

        if source_network:
            self.setup_network(source_network)

    def get_network(self, network_name: str) -> Network | None:
        network: Network | None = NETWORKS.get(network_name)
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
        self.w3 = AsyncWeb3(AsyncHTTPProvider(self.rpc, request_kwargs=self.request_kwargs))

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
            address=AsyncWeb3.to_checksum_address(contract_address),
            abi=abi
        )
        
    async def get_decimals(self, token_name: str = None, check_native: bool = False) -> int:
        if check_native:
            return 18
        contract = await self.get_contract(NETWORK_TOKEN_CONTRACTS[token_name])
        return await contract.functions.decimals().call()
    
    async def get_normalize_amount(self, token_name: str, amount_in_wei: int) -> float:
        decimals = await self.get_decimals(token_name)
        return float(amount_in_wei / 10 ** decimals)

    async def get_token_balance(self, token: str = None, check_native: bool = False) -> int | None:
        try:
            if check_native:
                token_balance = await self.w3.eth.get_balance(self.address)
                return token_balance or None

            contract: AsyncContract = await self.get_contract(NETWORK_TOKEN_CONTRACTS.get(self.network.name, {}).get(token, ""))
            token_balance = await contract.functions.balanceOf(self.address).call()
            return token_balance or None

        except Exception as error:
            self.logger_msg(self.name, self.address, f"Error while receiving token balance.\nError: {error}", "error")
            return None

    async def get_allowance(self, token_address: str, spender_address: str) -> int:
        contract = self.get_contract(token_address)
        return await contract.functions.allowance(
            self.address,
            spender_address
        ).call()
    
    async def get_priotiry_fee(self):
        fee_history = await self.w3.eth.fee_history(25, 'latest', [20.0])
        non_empty_block_priority_fees = [fee[0] for fee in fee_history["reward"] if fee[0] != 0]

        divisor_priority = max(len(non_empty_block_priority_fees), 1)

        priority_fee = int(round(sum(non_empty_block_priority_fees) / divisor_priority))

        return priority_fee
    
    async def prepare_transaction(self, value: int = 0):
        try:
            tx_params = {
                'from': self.address,
                'nonce': await self.w3.eth.get_transaction_count(self.address),
                'value': value,
                'chainId': self.network.chain_id
            }
            if self.network.eip1559_support:
                base_fee = await self.w3.eth.gas_price
                max_priority_fee_per_gas = await self.get_priotiry_fee()
                max_fee_per_gas = base_fee + max_priority_fee_per_gas
                tx_params['maxPriorityFeePerGas'] = max_priority_fee_per_gas
                tx_params['maxFeePerGas'] = int(max_fee_per_gas)
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
                self.logger.info(f"Симуляция транзакции прошла успешно: {result}")
                return True
            except Exception as error:
                self.logger.error(f"Симуляция транзакции не удалась: {self.get_normalize_error(error)}")
                raise BlockchainException(f"Ошибка симуляции: {self.get_normalize_error(error)}")
        else:
            try:
                if not without_gas:
                    transaction['gas'] = int(await self.w3.eth.estimate_gas(transaction))
            except Exception as error:
                raise BlockchainException(f'{self.get_normalize_error(error)}')

            try:
                singed_tx = self.w3.eth.account.sign_transaction(transaction, self.private_key)
                tx_hash = await self.w3.eth.send_raw_transaction(singed_tx.raw_transaction)
            except Exception as error:
                if self.get_normalize_error(error) == 'already known':
                    self.logger.warning(f'RPC получил ошибку, но tx был отправлен | {self.address}')
                    return True
                else:
                    raise BlockchainException(f'{self.get_normalize_error(error)}')

            try:
                total_time = 0
                timeout = 1200

                while True:
                    try:
                        receipts = await self.w3.eth.get_transaction_receipt(tx_hash) 
                        status = receipts.get("status")
                        if status == 1:
                            self.logger.info(f'Транзакция прошла успешно: {self.network.explorer}/tx/0x{tx_hash.hex()} | {self.address}')
                            if need_hash:
                                return tx_hash
                            return True
                        elif status is None:
                            await asyncio.sleep(poll_latency)
                        else:
                            return SoftwareException(f'Транзакция не выполнилась: {self.network.explorer}/tx/0x{tx_hash.hex()}')
                    except TransactionNotFound:
                        if total_time > timeout:
                            raise TimeExhausted(f"Транзакция отсутствует в цепочке после {timeout} секунд")
                        total_time += poll_latency
                        await asyncio.sleep(poll_latency)

                    except Exception as error:
                        self.logger.error(f'RPC получил автоматический ответ. Ошибка: {error} | {self.address}')
                        total_time += poll_latency
                        await asyncio.sleep(poll_latency)
            except Exception as error:
                raise BlockchainException(f'{self.get_normalize_error(error)}')

    @classmethod
    async def get_wallet_balance(cls, account_name: str, private_key: str, proxy: str | None) -> Dict[str, Dict[str, int]]:
        pass
        # params = {
        #     'id': 'wallet',
        #     'is_core': 'true',
        # }

        # response = requests.get('https://api.rabby.io/v1/user/total_balance', params=params)

        # client: Client = Client(account_name, private_key, proxy)

        # if NETWORKS:
        #     wallet_balances: Dict[str, Dict[str, float]] = {}
        #     native_tokens_names: Set[str] = set(network.token for network in NETWORKS.values())

        #     for network_name in NETWORKS:
        #         try:
        #             try:
        #                 client.setup_network(network_name)
        #             except Exception as error:
        #                 client.logger_msg(account_name, client.address,
        #                                   f"Error while setting up network.\nError: {error}", "error")
        #                 continue

        #             network_token_contracts: Dict[str, str] = NETWORK_TOKEN_CONTRACTS.get(network_name)
                    
        #             if not network_token_contracts:
        #                 token_name: str = "ETH"
        #                 native_token_balance: int | None = await client.get_token_balance(token_name, check_native=True)

        #                 if not native_token_balance:
        #                     client.logger_msg(account_name, client.address,
        #                                       f"Native token balance not found for network: {network_name}", "error")
        #                     continue

        #                 wallet_balances.setdefault(network_name, {})[token_name] = native_token_balance

        #             else:
        #                 for token_name in network_token_contracts:
        #                     token_contract_address: str | None = network_token_contracts.get(token_name)
        #                     if not token_contract_address:
        #                         client.logger_msg(account_name, client.address,
        #                                         f"Token contract address not found for token: {token_name} in network {network_name}", "error")
        #                         continue
                            
        #                     if token_name in native_tokens_names:
        #                         token_balance: int | None = await client.get_token_balance(token_name, check_native=True)
        #                     else:
        #                         token_balance: int | None = await client.get_token_balance(token_name)

        #                     if not token_balance:
        #                         client.logger_msg(account_name, client.address,
        #                                         f"Token balance not found for token: {token_name}", "error")
        #                         continue

        #                     wallet_balances.setdefault(network_name, {})[token_name] = token_balance

        #         except Exception as error:
        #             client.logger_msg(account_name, client.address,
        #                               f"Error while receiving wallet balances in networks.\nError: {error}", "error")
        #             raise error

        #     return wallet_balances

        # raise SoftwareException("Networks not found! Please, add networks to the networks module.")
