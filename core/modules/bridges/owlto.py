import random

from abc import ABC, abstractmethod
from typing import Tuple
from eth_typing import ChecksumAddress
from web3.contract import AsyncContract

from core.exceptions import InsufficientFundsError
from interfaces import (
    BridgeOwltoOPtoInkModule,
    BridgeOwltoInktoOPModule,
    BridgeOwltoBasetoInkModule,
    BridgeOwltoInktoBaseModule,
)
from loader import config
from logger import log
from models import Account, ModuleConfig
from core.wallet import Wallet
from settings import (
    OwltoContract,
)


class BridgeOwltoWorker(ABC):
    def __init__(self,
                 account: Account,
                 module_model,
                 ) -> None:
        Wallet.__init__(self,
                        private_key=account.private_key,
                        proxy=account.proxy,
                        rpc_url=random.choice(module_model.source_network.rpc),
        )

        self.account: Account = account
        self.module_model = module_model
        self.module_name: str = self.module_model.module_name
        self.module_display_name: str = self.module_model.module_display_name
        self.contract_data: OwltoContract = OwltoContract()
        self.destination: int | None = None

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

    @property
    def destination(self) -> int:
        return self.destination

    @destination.setter
    @abstractmethod
    def destionation(self, value) -> None:
        if not isinstance(value, int):
            raise TypeError("Destination parameter should be an integer type")
        self.destination: int = value

    @abstractmethod
    async def _get_data(self,
                        value: float,
                        ) -> Tuple[ChecksumAddress | int | str]:
        return (
            self.wallet_address,
            self.to_checksum_address("0x0000000000000000000000000000000000000000"),
            self.to_checksum_address("0x1f49a3fa2b5B5b61df8dE486aBb6F3b9df066d86"),
            self.to_wei(value, "ether"),
            self.destination,
            98675412,
        )

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

            if await self._has_sufficient_balance(balance, random_amount, min_save_amount):
                value: float = float(balance - random_amount)
                if value == 0:
                    value: float = float(random_amount * 0.95)

                log.info(f"Account: {self.wallet_address} make {self.module_display_name} using {value} | Save in {self.module_model.source_network_name}: {random_save_amount}")

                contract: AsyncContract = await self.get_contract(self.contract_data)
                contract_function = contract.functions.deposit(*await self._get_data(
                    value=value, destination=self.destination,
                ))
                tx_params = await self.build_transaction_params(
                    contract_function=contract_function,
                    value=self.to_wei(value, "ether"),
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
            error_msg: str = f"Error in {self.module_display_name} module: {error}"
            log.error(f"Account: {self.wallet_address} | {error_msg}")
            return False, error_msg


class BridgeOwltoOPtoInkWorker(BridgeOwltoWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeOwltoOPtoInkModule,
                 ) -> None:
        super().__init__(account, module_model)

    @property
    def destination(self) -> int:
        return self.destination

    @destination.setter
    @abstractmethod
    def destionation(self):
        self.destination = 88


class BridgeOwltoInkToOPWorker(BridgeOwltoWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeOwltoInktoOPModule,
                 ) -> None:
        super().__init__(account, module_model)

    @property
    def destination(self) -> int:
        return self.destination

    @destination.setter
    @abstractmethod
    def destionation(self):
        self.destination = 3


class BridgeOwltoBaseToInkWorker(BridgeOwltoWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeOwltoBasetoInkModule,
                 ) -> None:
        super().__init__(account, module_model)

    @property
    def destination(self) -> int:
        return self.destination

    @destination.setter
    @abstractmethod
    def destionation(self):
        self.destination = 88


class BridgeOwltoInkToBaseWorker(BridgeOwltoWorker):
    def __init__(self,
                 account: Account,
                 module_model: BridgeOwltoInktoBaseModule,
                 ) -> None:
        super().__init__(account, module_model)
    
    @property
    def destination(self) -> int:
        return self.destination

    @destination.setter
    @abstractmethod
    def destionation(self):
        self.destination = 3
