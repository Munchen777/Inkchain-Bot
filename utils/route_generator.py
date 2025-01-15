import random
import json

from typing import Any, Dict, List, Set

from data.config import ACCOUNT_NAMES, MODULES_CLASSES
from generall_settings import GLOBAL_NETWORK, SHUFFLE_ROUTE
from functions import*
from modules import Logger
from modules.interfaces import BaseModuleInfo
from settings import CLASSIC_ROUTES_MODULES_USING, CLASSIC_WITHDRAW_DEPENDENCIES
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

        route.sort(key=lambda x: x.module_priority)

        return route
    
    @classmethod
    def create_route_from_dict(cls, route_dict: Dict[str, Any]) -> BaseModuleInfo:
        module_name, module_display_name = (
            route_dict.get("module_name"),
            route_dict.get("module_display_name")
        )
        module_class: BaseModuleInfo | None = MODULES_CLASSES.get(module_name) or \
                                                MODULES_CLASSES.get(module_display_name)

        # validated_module = module_class.model_validate(route_dict)

        if not module_class:
            raise ValueError(f"Unknown module name: {module_name} or {module_display_name}")

        return module_class(**route_dict)

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
