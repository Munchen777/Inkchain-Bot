import random

from typing import Any, Dict, Self, Tuple

from core.api import BaseAPIClient
from core.exceptions import InsufficientFundsError
from interfaces import (
    BridgeRelayOPtoInkModule,
    BridgeRelayInktoOPModule,
    BridgeRelayBasetoInkModule,
    BridgeRelayInktoBaseModule,
)
from loader import config
from logger import log
from models import Account, ModuleConfig
from core.wallet import Wallet


class BridgeRelayWorker(Wallet):
    def __init__(self,
                 account: Account,
                 module_model
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

    async def __aenter__(self: Self) -> Self:
        await Wallet.__aenter__(self)
        self.api_client: BaseAPIClient = BaseAPIClient(
            url="https://api.relay.link",
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

    async def _get_headers(self) -> Dict[str, Any]:
        return {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ru-RU,ru;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "origin": "https://relay.link",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://relay.link/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }

    async def _has_sufficient_balance(self,
                                      balance: float,
                                      random_amount: float,
                                      save_amount: float
                                      ) -> bool:
        try:
            if float(balance - random_amount) >= save_amount:
                return True
            return False
        except Exception as error:
            error_msg: str = f"Insufficient Funds to execute {self.module_display_name} | Balance: {balance} | Save amount: {save_amount}"
            raise InsufficientFundsError(error_msg)

    async def _get_payload(self, value: int | float) -> Dict[str, Any]:
            return {
                "user": self.wallet_address,
                "originChainId": self.module_model.source_network_chain_id,
                "destinationChainId": self.module_model.destination_network_chain_id,
                "originCurrency": "0x0000000000000000000000000000000000000000",
                "destinationCurrency": "0x0000000000000000000000000000000000000000",
                "recipient": self.wallet_address,
                "tradeType": "EXACT_INPUT",
                "amount": self.to_wei(value, "ether"),
                "referrer": "relay.link/swap",
                "useExternalLiquidity": False,
            }

    async def run(self) -> Tuple[bool, str]:
        log.info(f"Account: {self.wallet_address} | Processing {self.module_display_name} ...")

        try:
            balance: float = await self.human_balance()

            module_config: ModuleConfig = await config._get_module_settings(self.module_name)

            min_percent_range, max_percent_range = (
                module_config.percent_range.min,
                module_config.percent_range.max,
            )

            if min_percent_range and max_percent_range:
                log.info(f"Account: {self.wallet_address} | Percent range {min_percent_range} - {max_percent_range}")

            min_save_amount, max_save_amount = (
                module_config.save_amount.min,
                module_config.save_amount.max,
            )

            if min_save_amount and max_save_amount:
                log.info(f"Account: {self.wallet_address} | Save amount range {min_save_amount} - {max_save_amount}")

            min_amount, max_amount = (
                float(balance * (min_percent_range / 100)),
                float(balance * (max_percent_range / 100)),
            )

            random_amount: float = random.uniform(min_amount, max_amount)
            random_save_amount: float = random.uniform(min_save_amount, max_save_amount)

            if await self._has_sufficient_balance(balance, random_amount, random_save_amount):
                value: float = float(balance - (balance - random_amount))
                if value == 0:
                    value: float = float(random_amount * 0.95)

                log.info(f"Account: {self.wallet_address} make {self.module_display_name} using {value} | Save in {self.module_model.source_network_name}: {random_save_amount}")

                headers: Dict[str, Any] = await self._get_headers()
                payload: Dict[str, Any] = await self._get_payload(value)

                tx_data: Dict[str, Any] = await self.api_client.send_request(
                    request_type="POST",
                    method="/quote",
                    json_data=payload,
                    headers=headers,
                )

                tx_params: Dict[str, Any] = await self.build_transaction_params(
                    to=self.to_checksum_address(tx_data["data"]["steps"][0]['items'][0]['data']['to']),
                    value=self.to_wei(value, "ether"),
                    data=tx_data["data"]["steps"][0]['items'][0]['data']['data'],
                )

                if balance == random_amount:
                    gas_limit: int = tx_params.get("gas", 0)
                    max_fee_per_gas: int = tx_params.get("maxFeePerGas", 0)
                    max_priority_fee_per_gas: int = tx_params.get("maxPriorityFeePerGas", 0)

                    total_gas_cost: int = int(gas_limit * (max_fee_per_gas + max_priority_fee_per_gas) * 1.02)
                    adjusted_value: float = float(balance - await self.convert_amount_to_ether(total_gas_cost))

                    payload: Dict[str, Any] = await self._get_payload(adjusted_value)
                    tx_data: Dict[str, Any] = await self.api_client.send_request(
                        request_type="POST",
                        method="/quote",
                        json_data=payload,
                        headers=headers,
                    )

                    tx_params: Dict[str, Any] = await self.build_transaction_params(
                        to=self.to_checksum_address(tx_data["data"]["steps"][0]['items'][0]['data']['to']),
                        value=self.to_wei(adjusted_value, "ether"),
                        data=tx_data["data"]["steps"][0]['items'][0]['data']['data'],
                    )

                status, tx_hash = await self._process_transaction(tx_params)
                return (
                    True, f"Account: {self.wallet_address} | Successfully executed {self.module_display_name}: {self.module_model.source_network.explorer}{tx_hash}"
                    ) if status else (
                        False, f"Account: {self.wallet_address} | Failed to execute {self.module_display_name}: {tx_hash}"
                        )

            else:
                error_msg: str = f"Insufficient balance for processing {self.module_display_name}"
                log.error(f"Account: {self.wallet_address} | {error_msg}")
                raise InsufficientFundsError

        except Exception as error:
            error_msg: str = f"Error in {self.module_display_name}: {error}"
            log.error(f"Account: {self.wallet_address} | {error_msg}")
            return False, error_msg


class BridgeRelayOPtoInkWorker(BridgeRelayWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeRelayOPtoInkModule,
                 ) -> None:
        super().__init__(account, module_model)


class BridgeRelayInkToOPWorker(BridgeRelayWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeRelayInktoOPModule,
                 ) -> None:
        super().__init__(account, module_model)


class BridgeRelayBaseToInkWorker(BridgeRelayWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeRelayBasetoInkModule,
                 ) -> None:
        super().__init__(account, module_model)


class BridgeRelayInkToBaseWorker(BridgeRelayWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeRelayInktoBaseModule,
                 ) -> None:
        super().__init__(account, module_model)
