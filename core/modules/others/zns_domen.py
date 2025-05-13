import faker
import random
import re
import ua_generator

from typing import Any, Dict, Self, Tuple
from web3.contract import AsyncContract

from core.api import BaseAPIClient
from core.exceptions import InsufficientFundsError
from core.wallet import Wallet
from models import Account, ModuleConfig
from loader import config
from logger import log


class ZNSDomenWorker(Wallet):
    def __init__(self,
                 account: Account,
                 module_model,
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

    async def get_availability_domen(self) -> bool:
        try:
            response_dict: Dict[str, Any] = await self.api_client.send_request(
                request_type="GET",
                method=f"/api/v2/addresses/{self.wallet_address}/transactions",
                headers=await self._get_headers(),
            )
            if response_dict.get("status_code") == 200:
                    transactions = response_dict.get("data", {})

                    for tx in transactions['items']:
                        if (tx.get('status') == 'ok' and 
                            tx.get('method') == 'registerDomains'):
                            return True

                    return False

            else:
                log.error(f"Account: {self.wallet_address} | Request failed with status code {response_dict.get("status_code")}")
                return False

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
                availability_contract = await self.get_availability_domen()
                if availability_contract:
                    msg: str = f"ZNC domen on the Ink network has previously been acquired"
                    log.info(
                        f"Account: {self.wallet_address} | {msg}"
                    )
                    return True, msg

                contract: AsyncContract = await self.get_contract(self.contract_data)
                
                faker_name = False

                while True:
                    if faker_name:
                        while True:
                            domain_name = faker.domain_name()
                            name = re.split(r'\.', domain_name)[0]
                            if len(name) > 5:
                                break
                    else:
                        domain_name = self.client.name_znc_domen

                    domain_length: int = len(name)
                    price = contract.functions.priceToRegister(domain_length).call()

                    try:
                        contract_function = contract.functions.registerDomains(
                            [self.wallet_address],
                            [name],
                            1,
                            self.to_checksum_address("0x0000000000000000000000000000000000000000"),
                            0
                        )
                        tx_params = await self.build_transaction_params(
                            value=price,
                            contract_function=contract_function,
                        )
                        status, tx_hash = await self._process_transaction(tx_params)
                        return (
                            True, f"Account: {self.wallet_address} | Successfully executed {self.module_display_name}: {self.module_model.source_network.explorer}{tx_hash}"
                            ) if status else (
                                False, f"Account: {self.wallet_address} | Failed to execute {self.module_display_name}: {tx_hash}"
                                )

                    except Exception as error:
                        if '0x3a81d6fc' in str(error):
                            error_msg: str = f"Domain {domain_name} already registered, skipping..."
                            log.warning(f"Account: {self.wallet_address} | {error_msg}")
                            faker_name = True
                            continue
                        else:
                            error_msg: str = f"Error with buying ZNS Domen"
                            log.error(  
                                f'Account: {self.wallet_address} | Error with buying ZNS Domen'
                            )
                            return False, error

            else:
                error_msg: str = f"Insufficient balance for processing {self.module_display_name}"
                log.error(f"Account: {self.wallet_address} | {error_msg}")
                return InsufficientFundsError

        except Exception as error:
            error_msg: str = f"Error in {self.module_display_name}: {error}"
            log.error(f"Account: {self.wallet_address} | {error_msg}")
            return False, error_msg
