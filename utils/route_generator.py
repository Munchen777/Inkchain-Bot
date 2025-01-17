import random
import json
import sys

from pydantic import ValidationError
from typing import Any, Dict, List, Set

from data.config import ACCOUNT_NAMES, MODULES_CLASSES
from generall_settings import SHUFFLE_ROUTE
from functions import*
from modules import Logger
from modules.interfaces import BaseModuleInfo
from utils.networks import Network
from settings import CLASSIC_ROUTES_MODULES_USING, CLASSIC_WITHDRAW_DEPENDENCIES
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
    def __init__(self):
        super().__init__()

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

        route.sort(key=lambda x: x.module_priority, reverse=True)

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

            all_available_networks: Dict[str, Network] = NETWORKS
            all_available_wallet_balances: Dict[str, Dict[str, int]] = await Client.get_wallet_balance(
                account_name=account_name, private_key=private_key, proxy=proxy
            )

            if not all_available_wallet_balances:
                self.logger_msg(account_name, None,
                                f"There is no any wallet balance for acccount {account_name}", "error")
                return

            for network_name, network_balances in all_available_wallet_balances.items():
                current_network: Network | None = all_available_networks.get(network_name)

                if not current_network:
                    continue

                for token_name, token_balance in network_balances.items():
                    suitable_modules: List[BaseModuleInfo] = [
                        module_instance
                        for _, module_instance in all_available_modules.items()
                        if module_instance.source_network == current_network.name and \
                            module_instance.min_available_balance <= float(token_balance)
                    ]
                    if not suitable_modules:
                        self.logger_msg(account_name, None,
                                        f"There is no any suitable modules for account {account_name} on network {network_name}", "warning")
                        continue

                    suitable_modules.sort(key=lambda x: (x.module_priority, x.count_of_operations), reverse=True)

                    account_data: Dict[str, Any] = {
                        "current_step": 0,
                        "route": [module_obj.model_dump() for module_obj in suitable_modules],
                    }

                    route_modules_dict[str(account_name)] = account_data

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
            return

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