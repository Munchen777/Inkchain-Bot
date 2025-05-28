import asyncio
import asyncio_throttle

from better_proxy import Proxy
from decimal import Decimal
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_typing import ChecksumAddress, HexStr
from pydantic import HttpUrl
from typing import Any, Dict, Self
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.contract import AsyncContract
from web3.eth import AsyncEth
from web3.types import Nonce, TxParams

from core.exceptions import WalletError, BlockchainError, InsufficientFundsError
from logger import log
from models import BaseContract, ERC20Contract


class Wallet(AsyncWeb3, Account):
    ZERO_ADDRESS: str = "0x0000000000000000000000000000000000000000"

    def __init__(self,
                 private_key: str,
                 proxy: Proxy | None = None,
                 rpc_url: HttpUrl | str = None,
                 ) -> None:

        provider: AsyncHTTPProvider = AsyncHTTPProvider(
            endpoint_uri=str(rpc_url),
            request_kwargs={
                "proxy": proxy.as_url if proxy else None,
                "ssl": False,
            },
        )
        super().__init__(provider=provider, modules={"eth": AsyncEth})

        self.private_key: str = self._initialize_private_key(private_key)
        self._contracts_cache: Dict[str, AsyncContract] = {}
        self._throttler: asyncio_throttle.Throttler = asyncio_throttle.Throttler(rate_limit=10, period=1)

    async def __aenter__(self: Self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        if hasattr(self.provider, '_session') and self.provider._session is not None:
            try:
                await self.provider._session.close()
            except Exception as error:
                log.error(f"Failed to close session: {error}", exc_info=True)

    async def _close_session(self):
        if hasattr(self.provider, '_session') and self.provider._session:
            await self.provider._session.close()

    @staticmethod
    def _initialize_private_key(private_key: str) -> Account:
        try:
            stripped_key = private_key.strip().lower()
            if not stripped_key.startswith("0x"):
                formatted_key = f"0x{stripped_key}"
            else:
                formatted_key = stripped_key
            return Account.from_key(formatted_key)

        except (ValueError, AttributeError) as error:
            log.error(f"Failed to initialize private key: {error}", exc_info=True)
            raise WalletError(f"Invalid private key format: {error}") from error

    @property
    def wallet_address(self) -> ChecksumAddress:
        return self.private_key.address

    @property
    async def use_eip1559(self) -> bool:
        try:
            latest_block = await self.eth.get_block('latest')
            return 'baseFeePerGas' in latest_block
        except Exception as e:
            log.error(f"Error checking EIP-1559 support: {e}")
            return False
    
    @staticmethod
    def _get_checksum_address(address: str) -> ChecksumAddress:
        return AsyncWeb3.to_checksum_address(address)   

    async def get_contract(self, contract: BaseContract | str | object) -> AsyncContract:
        if isinstance(contract, str):
            address: ChecksumAddress = self._get_checksum_address(contract)

            if address not in self._contracts_cache:
                temp_contract: ERC20Contract = ERC20Contract(address="")
                abi = await temp_contract.get_abi()
                contract_instance: AsyncContract = self.eth.contract(
                    address=address,
                    abi=abi,
                )
                self._contracts_cache[address] = contract_instance

            return self._contracts_cache[address]
        
        if isinstance(contract, BaseContract):
            address: ChecksumAddress = self._get_checksum_address(contract.address)
            if address not in self._contracts_cache:
                abi = await contract.get_abi()
                self._contracts_cache[address] = self.eth.contract(
                    address=address,
                    abi=abi,
                )
            return self._contracts_cache[address]

        if hasattr(contract, "address") and hasattr(contract, "abi"):
            address: ChecksumAddress = self._get_checksum_address(contract.address)

            if address not in self._contracts_cache:
                self._contracts_cache[address] = self.eth.contract(
                    address=address,
                    abi=contract.abi,
                )
            return self._contracts_cache[address]

        raise TypeError("Invalid contract type: expected BaseContract, str, or contract-like object")

    async def token_balance(self, token_address: str) -> int:
        contract: AsyncContract = await self.get_contract(token_address)
        return await contract.functions.balanceOf(
            self._get_checksum_address(self.private_key.address)
        ).call()

    async def _is_native_token(self, token_address: str) -> bool:
        return token_address == self.ZERO_ADDRESS

    async def _get_cached_contract(self, token_address: str) -> AsyncContract:
        checksum_address: ChecksumAddress = self._get_checksum_address(token_address)
        if checksum_address not in self._contracts_cache:
            self._contracts_cache[checksum_address] = await self.get_contract(checksum_address)

        return self._contracts_cache[checksum_address]

    async def convert_amount_to_decimals(self, amount: Decimal, token_address: str) -> int:
        checksum_address: ChecksumAddress = self._get_checksum_address(token_address)
    
        if await self._is_native_token(checksum_address):
            return self.to_wei(Decimal(str(amount)), 'ether')
        
        contract: AsyncContract = await self._get_cached_contract(checksum_address)
        decimals = await contract.functions.decimals().call()
        return int(Decimal(str(amount)) * Decimal(10 ** decimals))
    
    async def convert_amount_from_decimals(self, amount: int, token_address: str) -> float:
        checksum_address = self._get_checksum_address(token_address)
    
        if await self._is_native_token(checksum_address):
            return float(self.from_wei(amount, 'ether'))
        
        contract = await self._get_cached_contract(checksum_address)
        decimals = await contract.functions.decimals().call()
        return float(Decimal(amount) / Decimal(10 ** decimals))

    async def get_nonce(self) -> Nonce:
        for attempt in range(3):
            try:
                count = await self.eth.get_transaction_count(self.wallet_address, 'pending')
                return Nonce(count)
            except Exception as e:
                log.warning(f"Failed to get nonce (attempt {attempt + 1}): {e}", exc_info=True)
                if attempt < 2:
                    await asyncio.sleep(1)
                else:
                    raise RuntimeError("Failed to get nonce after 3 attempts") from e

    async def check_balance(self) -> None:
        balance = await self.eth.get_balance(self.private_key.address)
        if balance <= 0:
            raise InsufficientFundsError("ETH balance is empty")

    async def human_balance(self) -> float:
        balance = await self.eth.get_balance(self.private_key.address)
        return float(self.from_wei(balance, "ether"))
    
    async def convert_amount_to_ether(self, amount: float | int) -> float:
        try:
            if not isinstance(amount, (float, int)):
                raise ValueError(f"Amount is not integer or float type!")
            return float(self.from_wei(int(amount), "ether"))

        except ValueError as error:
            raise error

    async def has_sufficient_funds_for_tx(self, transaction: TxParams) -> bool:
        try:
            balance = await self.eth.get_balance(self.private_key.address)
            required = int(transaction.get('value', 0))
            
            if balance < required:
                required_eth = self.from_wei(required, 'ether')
                balance_eth = self.from_wei(balance, 'ether')
                raise InsufficientFundsError(
                    f"Insufficient ETH balance. Required: {required_eth:.6f} ETH, Available: {balance_eth:.6f} ETH"
                )
                
            return True
            
        except ValueError as error:
            raise ValueError(f"Invalid transaction parameters: {str(error)}") from error
        except Exception as error:
            raise BlockchainError(f"Failed to check transaction availability: {str(error)}") from error

    async def get_signature(self, text: str, private_key: str | None = None) -> HexStr:
        try:
            signing_key = (
                self.from_key(private_key) 
                if private_key 
                else self.private_key
            )

            encoded = encode_defunct(text=text)
            signature = signing_key.sign_message(encoded).signature
            
            return HexStr(signature.hex())

        except Exception as error:
            raise ValueError(f"Signing failed: {str(error)}") from error

    async def _estimate_gas_params(
        self,
        tx_params: dict,
        gas_buffer: float = 1.2,
        gas_price_buffer: float = 1.15,
        balance: float | None = None,
    ) -> dict:
        try:
            if not balance:
                balance: float = await self.human_balance()

            gas_estimate = await self.eth.estimate_gas(tx_params)
            tx_params["gas"] = int(gas_estimate * gas_buffer)

            if await self.use_eip1559:
                latest_block = await self.eth.get_block('latest')
                base_fee = latest_block['baseFeePerGas']
                priority_fee = await self.eth.max_priority_fee

                max_fee: int = int(base_fee * 2  + priority_fee)

                if balance and int(self.to_wei(balance, "ether")) == tx_params.get("value", 0):
                    gas_cost = tx_params["gas"] * max_fee

                    if gas_cost >= balance:
                        raise InsufficientFundsError(
                            f"Gas cost {self.from_wei(gas_cost, "ether")} ETH exceeds balance {balance} ETH"
                        )

                    tx_params.update({
                        # "maxPriorityFeePerGas": int((base_fee * 2 + priority_fee) * gas_price_buffer),
                        # "maxFeePerGas": int((base_fee * 2 + priority_fee) * gas_price_buffer)
                        "maxPriorityFeePerGas": priority_fee,
                        "maxFeePerGas": max_fee
                    })
                    # tx_params["value"] = int(tx_params.get("value", balance) - tx_params.get("maxFeePerGas"))
                    tx_params["value"] = balance - gas_cost

                else:
                    tx_params.update({
                        "maxPriorityFeePerGas": int(priority_fee * gas_price_buffer),
                        "maxFeePerGas": int((base_fee * 2 + priority_fee) * gas_price_buffer)
                    })
            else:
                tx_params["gasPrice"] = int(await self.eth.gas_price * gas_price_buffer)

            return tx_params
        except Exception as error:
            log.error(f"Gas estimation failed: {error}", exc_info=True)
            raise BlockchainError(f"Failed to estimate gas: {error}") from error

    async def build_transaction_params(
        self,
        contract_function: Any = None,
        to: str | None = None,
        value: int = 0,
        gas_buffer: float = 1.2,
        gas_price_buffer: float = 1.15,
        **kwargs
    ) -> Dict[str, Any]:
        base_params: Dict[str, Any] = {
            "from": self.wallet_address,
            "nonce": await self.get_nonce(),
            "value": value,
            **kwargs,
        }

        try:
            chain_id = await self.eth.chain_id
            base_params["chainId"] = chain_id
        except Exception as e:
            log.warning(f"Failed to get chain_id: {e}", exc_info=True)

        if not contract_function:
            if to is None:
                raise ValueError("'to' address required for ETH transfers")

            base_params.update({"to": to})
            return await self._estimate_gas_params(base_params, gas_buffer, gas_price_buffer)

        tx_params = await contract_function.build_transaction(base_params)
        return await self._estimate_gas_params(tx_params, gas_buffer, gas_price_buffer)

    async def _check_and_approve_token(
        self, 
        token_address: str, 
        spender_address: str, 
        amount: int
    ) -> tuple[bool, str]:
        try:
            token_contract: AsyncContract = await self.get_contract(token_address)
            
            current_allowance = await token_contract.functions.allowance(
                self.wallet_address, 
                spender_address
            ).call()

            if current_allowance >= amount:
                return True, "Allowance already sufficient"

            approve_params = await self.build_transaction_params(
                contract_function=token_contract.functions.approve(spender_address, amount)
            )

            success, result = await self._process_transaction(approve_params)
            if not success:
                raise WalletError(f"Approval failed: {result}")

            return True, "Approval successful"

        except Exception as error:
            return False, f"Error during approval: {str(error)}"
        
    async def send_and_verify_transaction(self, transaction: Any) -> tuple[bool, str]:
        async with self._throttler:
            max_attempts = 3
            current_attempt = 0
            last_error = None
            
            while current_attempt < max_attempts:
                try:
                    signed = self.private_key.sign_transaction(transaction)
                    tx_hash = await self.eth.send_raw_transaction(signed.raw_transaction)
                    receipt = await self.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
                    return receipt["status"] == 1, tx_hash.hex()
                    
                except Exception as error:
                    error_str = str(error)
                    last_error = error
                    current_attempt += 1
                    
                    if "NONCE_TOO_SMALL" in error_str or "nonce too low" in error_str.lower():
                        log.warning(f"Nonce too small. Current: {transaction.get('nonce')}. Getting new nonce.")
                        try:
                            new_nonce = await self.get_nonce()
                            transaction['nonce'] = new_nonce
                        except Exception as nonce_error:
                            log.error(f"Error during getting new nonce: {str(nonce_error)}")
                            
                    else:
                        log.error(f"Error during sending transaction: {error_str}")
                        return False, error_str
                        
                    await asyncio.sleep(2)
            
            return False, f"Failed to execute transaction after {max_attempts} attempts. Last error: {str(last_error)}"
    
    async def _process_transaction(self, transaction: Any) -> tuple[bool, str]:
        try:
            status, result = await self.send_and_verify_transaction(transaction)
            return status, result
        except Exception as error:
            return False, str(error)

    async def get_available_balances(self) -> Dict[str, float]:
        try:
            pass
        except Exception as error:
            pass
