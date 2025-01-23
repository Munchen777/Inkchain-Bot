import random
import json
import sys

from collections import deque
from pathlib import Path
from pydantic import ValidationError
from typing import Any, Dict, Deque, List, Set

from data.config import ACCOUNT_NAMES, MODULES_CLASSES
from generall_settings import SHUFFLE_ROUTE, USE_L2_TO_DEPOSIT
from functions import*
from modules import Logger
from modules.interfaces import BaseModuleInfo
from utils.networks import Network
from settings import CLASSIC_ROUTES_MODULES_USING, CLASSIC_WITHDRAW_DEPENDENCIES, PRIORITY_NETWORK_NAMES
from utils.networks import NETWORKS
from utils.client import SoftwareException
from utils.tools import clean_progress_file


def get_func_by_name(module_name, help_message: bool = False) -> BaseModuleInfo | None:
    """Ищет в словаре AVAILABLE_MODULES_INFO по имени модуля и возвращает либо module_name,
    либо tg info, в зависимости от значения аргумента help_message"""
    module_class = MODULES_CLASSES.get(module_name)

    try:
        if help_message:
            return module_class().module_display_name
        return module_class()

    except Exception as error:
        return None


class RouteGenerator(Logger):
    def __init__(self, file_path: str = "./data/service/history.json"):
        super().__init__()
        self.file_path: Path = Path(file_path)
        self.history: Dict[str, Set[str]] = {}
        self.load_history()

    def load_history(self):
        """ Download history of accounts that have been run """
        if self.file_path.exists():
            try:
                with open(self.file_path, "r") as file:
                    data: Dict[str, Set[str]] = json.load(file)
            
            except Exception as error:
                self.history: Dict[str, Set[str]] = {}
                return

            self.history: Dict[str, Set[str]] = {
                account_name: set(modules)
                for account_name, modules in data.items()
            }
        else:
            self.history: Dict[str, Set[str]] = {}

    async def add_executed_module(self, account_name: str, module_name: str) -> None:
        self.history.setdefault(account_name, set()).add(module_name)
        await self.save_history()

    async def save_history(self) -> None:
        data: Dict[str, List[str]] = {
            account_name: list(modules)
            for account_name, modules in self.history.items()
        }
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    async def check_first_run_modules(self, account_name: str) -> bool:
        return account_name not in self.history

    @staticmethod
    def classic_generate_route() -> List[BaseModuleInfo]:
        """
        Generate and sort list of BaseNoduleInfo by module_priority
        The lower priority is the first in the route list

        """
        route: List[BaseModuleInfo] = []

        for i in CLASSIC_ROUTES_MODULES_USING:
            module_name: str = random.choice(i)

            if module_name is None or module_name not in MODULES_CLASSES:
                continue

            module_obj: BaseModuleInfo | None = get_func_by_name(module_name)

            if module_obj:
                route.append(module_obj)
                continue

            raise SoftwareException(f"There is no module with the name {module_name} in the software!")

        # route.sort(key=lambda x: x.module_priority, reverse=True)

        return route

    @classmethod
    def create_route_from_dict(cls, route_dict: Dict[str, Any]) -> BaseModuleInfo:
        module_name: str = route_dict.get("module_name")

        module_class: BaseModuleInfo | None = MODULES_CLASSES.get(module_name)

        if not module_class:
            raise ValueError(f"Unknown module name: {module_name}")

        try:
            validated_module: BaseModuleInfo = module_class.model_validate(route_dict)
            return validated_module

        except ValidationError as error:
            raise ValidationError(f"Error while validating module {module_name}.\nError: {error}")

    def sort_classic_route(self, route: list[str], landing_mode: bool) -> List[str]:
        """
        Create classic route

        Atributes:
            route - list of module names

        """
        if not landing_mode:
            modules_dependents: Dict[str, int] = {
                # TODO: в случае, если понадобится пополнение с биржи, то расскоментировать и написать модули

                # "okx_withdraw": 0,
                # "binance_withdraw": 0,
                # "bybit_withdraw": 0,
                # "bingx_withdraw": 0,
                # "bitget_withdraw": 0,
                # "bridge_native": 1,
            }

            classic_route = []

            for module_name in route:
                if module_name in modules_dependents:
                    classic_route.append((module_name), modules_dependents[module_name])
                else:
                    classic_route.append((module_name, 2))

            random.shuffle(classic_route)

            route_with_priority: List[str] = [
                module_name[0]
                for module_name in sorted(classic_route, key=lambda x: x[1])
            ]

        else:
            route_with_priority = route

        if CLASSIC_WITHDRAW_DEPENDENCIES:
            deposit_modules: Set = set([
                "deposit_module",
            ])
            new_route_with_dep = []

            for module_info in route_with_priority:
                module_name, rpc = module_info.split()
                new_route_with_dep.append(module_info)

                if module_name in deposit_modules:
                    withdraw_module_name = module_name.replace("deposit", "withdraw")
                    withdraw_module = get_func_by_name(withdraw_module_name)
                    new_route_with_dep.append(f"{withdraw_module.__name__} {rpc}")

        else:
            new_route_with_dep = route_with_priority

        return new_route_with_dep
    
    async def get_available_modules(self,
                                    all_available_modules: Dict[str, BaseModuleInfo],
                                    executed_modules: Set[str],
                                    all_available_wallet_balances: Dict[str, Dict[str, float]],
                                    required_modules_to_execute: Set[str],
                                    client: Client,
                                    is_first_run: bool = False,
                                    ) -> List[BaseModuleInfo] | None:
        available_modules: Deque[BaseModuleInfo] | None = deque([])

        if is_first_run and required_modules_to_execute:
            networks_being_deposited: Set[str] = set()

            # Идем по модулям, которые должны быть обязательно выполнены
            for module_name in required_modules_to_execute:
                required_module_to_execute: BaseModuleInfo | None = all_available_modules.get(module_name)
                if not required_module_to_execute:
                    self.logger_msg(client.name, client.address,
                                    f"There is no network for required module {module_name}")
                    continue

                network_balances: Dict[str, float] = all_available_wallet_balances.get(
                    required_module_to_execute.source_network, {}
                )
                # Проверяем на наличие баланса в сети назначения (destination_network)
                # и наличие названия сети в множестве PRIORITY_NETWORK_NAMES
                if required_module_to_execute.destination_network and \
                    required_module_to_execute.destination_network in PRIORITY_NETWORK_NAMES:
                        destination_network: Network | None = NETWORKS.get(required_module_to_execute.destination_network)
                        if not destination_network:
                            self.logger_msg(client.name, client.address,
                                    f"There is no destination network {required_module_to_execute.destination_network}")
                            continue

                        token_balances_in_destination_network: Dict[str, float] | None = all_available_wallet_balances.get(
                            destination_network.name, {}
                        )
                        # Проверяем на наличие баланса в сети назначения (destination_network)
                        if token_balances_in_destination_network:
                            for token_name, token_balance in token_balances_in_destination_network.items():
                                if (float(token_balance) <= required_module_to_execute.min_available_balance and \
                                    token_name == destination_network.token and \
                                        destination_network.name not in networks_being_deposited):

                                    # Используем ли бриджи, у которых required_on_first_run = False
                                    deposit_modules: List[BridgeModuleInfo] | None = []

                                    if USE_L2_TO_DEPOSIT:
                                        deposit_modules: List[BridgeModuleInfo] | None = [
                                            module_class
                                            for module_class in all_available_modules.values()
                                            if module_class.module_type == "bridge" and \
                                                module_class.destination_network == required_module_to_execute.destination_network and \
                                                    module_class.required_on_first_run is False
                                        ]
                                    else:
                                        deposit_modules: List[BridgeModuleInfo] | None = [
                                            module_class
                                            for module_class in all_available_modules.values()
                                            if module_class.module_type == "bridge" and \
                                                module_class.destination_network == required_module_to_execute.destination_network and \
                                                    module_class.required_on_first_run is True
                                        ]

                                    # Проверяем баланс в сети отправки
                                    for deposit_module in deposit_modules:
                                        source_network: Network | None = NETWORKS.get(deposit_module.source_network)

                                        source_network_token_balance: float | None = all_available_wallet_balances.get(
                                            source_network.name, {}).get(source_network.token, 0
                                        )

                                        if float(source_network_token_balance) > required_module_to_execute.min_available_balance:
                                            available_modules.appendleft(deposit_module)

                                            # if required_module_to_execute.module_type != "bridge":
                                            available_modules.append(required_module_to_execute)

                                            networks_being_deposited.add(destination_network.name)
                                            required_module_to_execute.dependencies.required_modules.add(deposit_module.module_name) #

                                elif required_module_to_execute.module_type != "bridge":
                                    available_modules.append(required_module_to_execute)

                        else:
                            self.logger_msg(None, None,
                                            f"Can't find balance in destination network for module {required_module_to_execute.module_name}\nGo to next required module")
                            continue
    
        for module_name, module_class in all_available_modules.items():
            # если такой модуль уже был добавлен или был выполнен, то пропускаем его
            if module_name in executed_modules:
                continue

            if is_first_run and not module_class.required_on_first_run:
                continue

            # if not is_first_run and module_class.required_on_first_run:
            #     continue

            if not module_class.dependencies.required_modules.issubset(executed_modules):
                continue

            network_balances: Dict[str, int] = all_available_wallet_balances.get(
                    module_class.source_network, {}
            )
            # Проверяем на наличие баланса в сети
            for token_name, token_balance in network_balances.items():
                bridge_modules: List[BridgeModuleInfo] | None = [
                    module_class
                    for module_class in all_available_modules.values()
                    if module_class.module_type == "bridge" and \
                        module_class.source_network == module_class.source_network
                ]
                if float(token_balance) > module_class.min_available_balance:
                    available_modules.append(module_class)

        return available_modules

    async def smart_generate_route(self, account_name: str, private_key: str, proxy: str | None) -> None:
        route_modules_dict: Dict[str, BaseModuleInfo] = {}

        try:
            try:
                all_available_modules: Dict[str, BaseModuleInfo] | None = {
                    module_name: module_class()
                    for module_name, module_class in MODULES_CLASSES.items()
                }

            except ValidationError as error:
                self.logger_msg(account_name, None,
                                f"Error while creating all available modules.\nError: {error}", "error")
                raise error

            if not all_available_modules:
                self.logger_msg(account_name, None,
                                f"There is no any module for account {account_name}", "warning")
                raise SoftwareException

            client: Client = Client(account_name, private_key, proxy)
            all_available_wallet_balances: Dict[str, Dict[str, int]] = await client.get_wallet_balance()

            if not all_available_wallet_balances:
                self.logger_msg(account_name, None,
                                f"There is no any wallet balance for acccount {account_name}", "error")
                return

            # 1. Проверяем, запускаем ли мы софт впервые
            is_first_run: bool = await self.check_first_run_modules(account_name)

            suitable_modules: List[BaseModuleInfo] = []
            executed_modules: Dict[str, Set[str]] = self.history.get(account_name, set())

            try:
                required_modules_to_execute: List[str] = RequiredModulesToExecute().required_modules

            except Exception as error:
                self.logger_msg(account_name, None,
                                f"Error while getting required modules to execute.\nError: {error}", "error")
                # return

            if required_modules_to_execute:
                required_modules_to_execute: Set[str] = set(required_modules_to_execute)
                required_modules_to_execute: Set[str] = required_modules_to_execute - executed_modules

            available_modules: List[BaseModuleInfo] | None = await self.get_available_modules(
                all_available_modules,
                executed_modules,
                all_available_wallet_balances,
                required_modules_to_execute,
                client,
                is_first_run,
            )
            if not available_modules:
                self.logger_msg(client.name, client.address,
                                f"No available modules for account {account_name}", "warning")
                return

            suitable_modules.extend(available_modules)

            executed_modules.update(
                [module_class.module_name for module_class in available_modules]
            )

            if not suitable_modules:
                self.logger_msg(account_name, None,
                                f"There is no any suitable modules for account {account_name}", "warning")
                return

            try:
                route_modules_dict: Dict[str, Any] = {
                    str(account_name): {
                        "current_step": 0,
                        "route": [module_obj.model_dump() for module_obj in suitable_modules],
                    }
                }
            except Exception as error:
                self.logger_msg(account_name, None,
                                f"Error while serializing route modules.\nError: {error}", "error")
                return

            try:
                with open(file="./data/service/wallets_progress.json", mode="w") as file:
                    json.dump(route_modules_dict, file, indent=4)

                self.logger_msg(account_name, None,
                    f"Successfully generated {len(route_modules_dict)} routes into /data/services/wallets_progress.json", "success")
                return

            except FileNotFoundError as error:
                self.logger_msg(account_name, None,
                                f"File ./data/service/wallets_progress.json not found.\nError: {error}", "error")
                return

        except SoftwareException as error:
            self.logger_msg(account_name, None,
                            f"Error while smart generate route. Check settings or config modules.\nError: {error}", "error")
            sys.exit(1)

        except Exception as error:
            self.logger_msg(account_name, None,
                            f"Error in smart_generate_route function.\nError: {error}", "error")
            raise error

    def classic_routes_json_save(self):
        clean_progress_file()

        accounts_data: Dict[str, Any] = {}

        with open(file="./data/service/wallets_progress.json", mode="w") as file:
            for account_name in ACCOUNT_NAMES:
                if isinstance(account_name, (str, int)):
                    classic_route: List[BaseModuleInfo] = self.classic_generate_route()

                    # if SHUFFLE_ROUTE:
                    #     classic_route = self.sort_classic_route(route=classic_route)

                    # if CLASSIC_WITHDRAW_DEPENDENCIES:
                    #     classic_route = self.sort_classic_route(route=classic_route, landing_mode=True)

                    account_data = {
                        "current_step": 0,
                        "route": [module_obj.model_dump() for module_obj in classic_route],
                    }
                    accounts_data[str(account_name)] = account_data

            json.dump(accounts_data, file, indent=4)

        self.logger.info(
            f"Successfully generated {len(accounts_data)} classic routes into /data/services/wallets_progress.json"
        )