import random

from typing import Tuple
from web3.contract import AsyncContract

from core.exceptions import InsufficientFundsError
from core.wallet import Wallet
from interfaces import MintNFTParagrafModule
from loader import config
from logger import log
from models import Account, ModuleConfig
from settings import ParagraphContract


class MintParagraphNFTWorker(Wallet):
    def __init__(self,
                 account: Account,
                 module_model: MintNFTParagrafModule,
                 ) -> None:
        Wallet.__init__(self,
                        private_key=account.private_key,
                        proxy=account.proxy,
                        rpc_url=random.choice(module_model.source_network.rpc),
        )

        self.account: Account = account
        self.module_model: MintNFTParagrafModule = module_model
        self.module_name: str = self.module_model.module_name
        self.module_display_name: str = self.module_model.module_display_name
        self.contract_data: ParagraphContract = ParagraphContract()

    async def _has_sufficient_balance(self,
                                    balance: float,
                                    save_amount: float,
                                    ) -> bool:
        try:
            if balance > save_amount:
                return True
            return False
        except Exception as error:
            error_msg: str = f"Insufficient Funds to execute {self.module_display_name} | Balance: {balance} | Save amount: {save_amount}"
            raise InsufficientFundsError(error_msg)

    async def run(self) -> Tuple[bool, str]:
        log.info(f"Account: {self.wallet_address} | Processing {self.module_display_name} ...")

        try:
            balance: float = await self.human_balance()
            module_config: ModuleConfig = await config._get_module_settings(self.module_name)

            contract: AsyncContract = await self.get_contract(self.contract_data)
            token_balance = contract.functions.balanceOf(self.wallet_address).call()

            if token_balance > 0:
                msg: str = f"The address already has nft Paragraf on the Ink network"
                log.info(f"Account: {self.wallet_address} | {msg}")
                return True, msg

            min_save_amount, max_save_amount = (
                module_config.save_amount.min,
                module_config.save_amount.max,
            )
            random_save_amount: float = random.uniform(min_save_amount, max_save_amount)

            if await self._has_sufficient_balance(balance, random_save_amount):
                contract_function = contract.functions.mintWithReferrer(
                    self.wallet_address,
                    self.to_checksum_address("0x0000000000000000000000000000000000000000"),
                )
                tx_params = await self.build_transaction_params(
                    contract_function=contract_function,
                    value=777000000000000,
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
