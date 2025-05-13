import random
import ua_generator

from datetime import datetime, timedelta
from typing import Any, Dict, Self, Tuple
from web3.contract import AsyncContract

from core.api import BaseAPIClient
from core.wallet import Wallet
from core.exceptions import InsufficientFundsError
from models import Account, ModuleConfig
from loader import config
from logger import log
from settings import (
    DailyGMContract,
    ClaimDailyGMModule,
)


class ClaimDailyGMWorker(Wallet):
    def __init__(self,
                 account: Account,
                 module_model: ClaimDailyGMModule,
                 ) -> None:
        Wallet.__init__(self,
                        private_key=account.private_key,
                        proxy=account.proxy,
                        rpc_url=random.choice(module_model.source_network.rpc),
        )
        self.api_client: BaseAPIClient | None = None

        self.account: Account = account
        self.module_model = module_model
        self.module_name: str = self.module_model.module_name
        self.module_display_name: str = self.module_model.module_display_name
        self.contract_data: DailyGMContract = DailyGMContract()

    async def __aenter__(self: Self) -> Self:
        await Wallet.__aenter__(self)
        self.api_client: BaseAPIClient = BaseAPIClient(
            url="https://explorer.inkonchain.com",
            proxy=self.account.proxy,
        )
        await self.api_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback) -> None:
        try:
            if hasattr(self, "api_client") and  self.api_client:
                await self.api_client.__aexit__(exc_type, exc_value, exc_traceback)
        finally:
            await Wallet.__aexit__(self, exc_type, exc_value, exc_traceback)

    async def _get_headers(self) -> Dict[str, str]:
        return {
            'accept': '*/*',
            'referer': f'{self.api_client.base_url}/address/{self.wallet_address}',
            'user-agent': self.api_client._generate_headers().get("user-agent", ua_generator.generate(
                device=("desktop", ),
                platform=("windows", "macos", "linux", ),
                browser=("chrome", ),
                ).text
            ),
        }

    async def get_last_claim(self) -> Tuple[bool, int]:
        try:
            response_dict: Dict[str, Any] = await self.api_client.send_request(
                request_type="GET",
                method=f"/api/v2/addresses/{self.wallet_address}/transactions",
                headers=await self._get_headers(),
            )
            if response_dict.get("status_code") == 200:
                transactions = response_dict.get("data")

                last_tx_timestamp = None
                for tx in transactions.get('items', []):
                    if isinstance(tx, dict):
                        to_field = tx.get('to', {})
                        if isinstance(to_field, dict):
                            if all([
                                to_field.get('name') == 'DailyGM', 
                                tx.get('status') == 'ok', 
                                'contract_call' in tx.get('transaction_types', [])
                            ]):
                                last_tx_timestamp = tx.get('timestamp')

                    if last_tx_timestamp:
                        tx_time: datetime = datetime.strptime(last_tx_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                        current_time: datetime = datetime.now()
                        time_diff = current_time - tx_time
                        remaining_time = timedelta(hours=24) - time_diff
                        if time_diff < timedelta(hours=24):
                            return True, remaining_time
                        else: return False, 0

                    return False, 0

                else:
                    log.error(f"Account: {self.wallet_address} |  Request failed with status code: {response_dict.get("status_code", "N/A")}")
                    return False, 0

        except Exception as error:
            log.error(f"Account: {self.wallet_address} | Failed to send request: {error}")
            return False, 0

    async def _has_sufficient_balance(self, balance: float, save_amount: float) -> bool:
        try:
            if balance > save_amount:
                return True
            return False
        except Exception:
            error_msg: str = f"Insufficient Funds to execute {self.module_display_name} | Balance: {balance} | Save amount: {save_amount}"
            raise InsufficientFundsError(error_msg)

    async def run(self) -> Tuple[bool, str]:
        log.info(f"Account: {self.wallet_address} | Processing {self.module_display_name} ...")

        try:
            balance: float = await self.human_balance()
            module_config: ModuleConfig = await config._get_module_settings(self.module_name)

            min_save_amount, max_save_amount = (
                module_config.save_amount.min,
                module_config.save_amount.max,
            )
            random_save_amount: float = random.uniform(min_save_amount, max_save_amount)

            if await self._has_sufficient_balance(balance, random_save_amount):

                availability_contract, remaining_time = await self.get_last_claim()
                if availability_contract:
                    msg: str = f"You won't be able to fulfill your GM claim until {remaining_time}"
                    log.info(
                        f"Account: {self.wallet_address} | {msg}"
                    )
                    return True, msg

                contract: AsyncContract = await self.get_contract(self.contract_data)
                contract_function = contract.functions.gm()

                tx_params = await self.build_transaction_params(
                    contract_function=contract_function,
                )
                status, tx_hash = await self._process_transaction(tx_params)
                return (True, tx_hash) if status else (False, f"Transaction failed: {tx_hash}")

            else:
                error_msg: str = f"Insufficient balance for processing {self.module_display_name}"
                log.error(f"Account: {self.wallet_address} | {error_msg}")
                raise InsufficientFundsError

        except Exception as error:
            error_msg: str = f"Error in {self.module_display_name}: {error}"
            log.error(f"Account: {self.wallet_address} | {error_msg}")
            return False, error_msg
