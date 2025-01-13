import random
import json

from typing import Dict, List, Tuple, Set

from data.config import ACCOUNT_NAMES
from generall_settings import GLOBAL_NETWORK, SHUFFLE_ROUTE
from functions import*
from modules import Logger
from settings import CLASSIC_ROUTES_MODULES_USING, CLASSIC_WITHDRAW_DEPENDENCIES
from utils.client import SoftwareException
from utils.tools import clean_progress_file


AVAILABLE_MODULES_INFO: Dict = {
    # module name: function, priority, tg module name, supported network
    # bridge_native: (bridge_native, 1, "Bridge Native", [2]),
    bridge_gg_worker: (bridge_gg_worker, 1, "Bridge GG", [2]),

}


def get_func_by_name(module_name, help_message: bool = False):
    """Ищет в словаре AVAILABLE_MODULES_INFO по имени модуля и возвращает либо module_name,
    либо tg info, в зависимости от значения аргумента help_message"""
    for k, v in AVAILABLE_MODULES_INFO.items():
        if k.__name__ == module_name:
            if help_message:
                return v[2]
            return v[0]


class RouteGenerator(Logger):
    def __init__(self):
        super().__init__()

        self.modules_names_const: list = [
            module.__name__ for module in list(AVAILABLE_MODULES_INFO.keys())
        ]

    @staticmethod
    def classic_generate_route() -> List[str]:
        """
        Generate list of module_names based on module priority

        """
        route = []
        rpc = GLOBAL_NETWORK
        """ 
        CLASSIC_ROUTES_MODULES_USING = [
            ["bridge_native: 1"],
        ] 
          
        """
        for i in CLASSIC_ROUTES_MODULES_USING:
            module_name: str = random.choice(i)

            if module_name is None:
                continue

            if ":" in module_name:
                module_name, rpc = module_name.split(":")

            module = get_func_by_name(module_name)

            if module:
                route.append(f"{module.__name__} {rpc}")
                continue

            raise SoftwareException(f"There is no module with the name {module_name} in the software!")

        return route
    
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

        accounts_data = {}

        with open(file="./data/service/wallets_progress.json", mode="w") as file:
            for account_name in ACCOUNT_NAMES:
                if isinstance(account_name, (str, int)):
                    classic_route = self.classic_generate_route()

                    if SHUFFLE_ROUTE:
                        classic_route = self.sort_classic_route(route=classic_route)

                    if CLASSIC_WITHDRAW_DEPENDENCIES:
                        classic_route = self.sort_classic_route(route=classic_route, landing_mode=True)

                    account_data = {
                        "current_step": 0,
                        "route": classic_route,
                    }
                    accounts_data[str(account_name)] = account_data

            json.dump(accounts_data, file, indent=4)

        self.logger.info(
            f"Successfully generated {len(accounts_data)} classic routes into /data/services/wallets_progress.json"
        )
