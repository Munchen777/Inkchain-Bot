import random

from typing import Tuple
from web3.contract import AsyncContract

from core.exceptions import InsufficientFundsError
from core.wallet import Wallet
from interfaces import RhinoNFTModule
from loader import config
from logger import log
from models import Account, ModuleConfig
from settings import RhinoFiNFTContract


class RhinoFiNFTWorker(Wallet):
    def __init__(self,
                 account: Account,
                 module_model: RhinoNFTModule,
                 ) -> None:
        Wallet.__init__(self,
                        private_key=account.private_key,
                        proxy=account.proxy,
                        rpc_url=random.choice(module_model.source_network.rpc),
        )

        self.account: Account = account
        self.module_model: RhinoNFTModule = module_model
        self.module_name: str = self.module_model.module_name
        self.module_display_name: str = self.module_model.module_display_name
        self.contract_data: RhinoFiNFTContract = RhinoFiNFTContract()

    async def _has_sufficient_balance(self,
                                    balance: float,
                                    value_in_wei: int,
                                    save_amount: float
                                    ) -> bool:
        try:
            if float(balance - float(value_in_wei)) >= save_amount:
                return True
            return False
        except Exception as error:
            error_msg: str = f"Insufficient Funds to execute {self.module_display_name} | Balance: {balance} | Save amount: {save_amount}"
            raise InsufficientFundsError(error_msg)

    async def run(self) -> Tuple[bool, str]:
        log.info(f"Account: {self.wallet_address} | Processing {self.module_display_name} ...")

        try:
            balance: float = await self.human_balance()
            contract: AsyncContract = await self.get_contract(self.contract_data)
            token_balance = await contract.functions.balanceOf(self.wallet_address, 1).call()

            if token_balance >= 1:
                msg: str = f"The address already has Rhino NFT on the Ink network"
                log.info(f"Account: {self.wallet_address} | {msg}")
                return True, msg

            module_config: ModuleConfig = await config._get_module_settings(self.module_name)
            min_save_amount, max_save_amount = (
                module_config.save_amount.min,
                module_config.save_amount.max,
            )
            value_in_wei: int = self.from_wei(150_000_000_000_000, "ether")
            random_save_amount: float = random.uniform(min_save_amount, max_save_amount)

            if await self._has_sufficient_balance(balance, value_in_wei, random_save_amount):
                contract_function = contract.functions.mint(1)
                tx_params = await self.build_transaction_params(
                    contract_function=contract_function,
                    value=150_000_000_000_000,
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
