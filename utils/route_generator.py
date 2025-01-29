import random
import os
import json
import sys

from collections import deque, defaultdict
from pathlib import Path
from pydantic import ValidationError
from typing import Any, Dict, Deque, list, Set, Tuple, DefaultDict

from data.config import ACCOUNT_NAMES, MODULES_CLASSES, PRIVATE_KEYS, PROXIES
from generall_settings import SHUFFLE_ROUTE, USE_L2_TO_DEPOSIT
from functions import*
from modules import Logger
from modules.interfaces import BaseModuleInfo
from utils.networks import Network
from settings import *
from utils.networks import NETWORKS
from utils.client import SoftwareException
from utils.tools import clean_progress_file, topological_sort


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


class ModuleHistory:
    def __init__(self, file_path: str = "./data/service/history.json"):
        self.file_path: Path = Path(file_path)
        self.history: Dict[str, Set[str]] = {}
        self.load_history()

    def load_history(self):
        if self.file_path.exists():
            with open(self.file_path, "r") as file:
                try:
                    data = json.load(file)
                    self.history = {
                        account_name: set(modules)
                        for account_name, modules in data.items()
                    }
                except json.JSONDecodeError:
                    self.history = {}
        else:
            self.history = {}
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w") as file:
                json.dump({}, file)

    async def add_executed_module(self, account_name: str, module_name: str, module_success: bool) -> None:
        if module_success:
            self.history.setdefault(account_name, set()).add(module_name)
            await self.save_history()

    async def save_history(self) -> None:
        data = {
            account_name: list(modules)
            for account_name, modules in self.history.items()
        }
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    async def check_first_run_modules(self, account_name: str) -> bool:
        return account_name not in self.history


class RouteGenerator(Logger):
    def __init__(self, file_path="../data/service/history.json"):
        super().__init__()
        self.module_history: ModuleHistory = ModuleHistory()
        self.file_path: Path = Path(file_path)
        self.history: Dict[str, Set[str]] = {}
        self.load_history()

    def load_history(self):
        if self.file_path.exists():
            with open(self.file_path, "r") as file:
                try:
                    data = json.load(file)
                    self.history = {
                        account_name: set(modules)
                        for account_name, modules in data.items()
                    }
                except json.JSONDecodeError:
                    self.history = {}
        else:
            self.history = {}
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, "w") as file:
                json.dump({}, file)


    async def add_executed_module(self, account_name: str, module_name: str, module_success: bool) -> None:
        if module_success:
            self.history.setdefault(account_name, set()).add(module_name)
            await self.save_history()

    async def save_history(self) -> None:
        data = {
            account_name: list(modules)
            for account_name, modules in self.history.items()
        }
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, "w") as file:
            json.dump(data, file, indent=4)

    async def check_first_run_modules(self, account_name: str) -> bool:
        return account_name not in self.history

    async def build_dependency_graph(self,
                                     modules: list[BaseModuleInfo],
                                     all_available_wallet_balances: Dict[str, Dict[str, float]]
                                     ) -> DefaultDict[str, list]:
        graph: DefaultDict[str, list[str]] = defaultdict(list)

        try:
            # Иду по всем модулям
            for module_name in modules:
                module: BaseModuleInfo = MODULES_CLASSES.get(module_name)()
                source_tokens: list[str] | None = module.source_token if isinstance(module.source_token, list) else [module.source_token]
                source_network: str | None = module.source_network
                
                if not all(all_available_wallet_balances.get(source_network, {}).get(token, 0) >= module.min_amount_residue
                    for token in source_tokens if token
                ):
                    continue

                for dep_modul_name in modules:
                    # Если равны, то пропускаем
                    if module_name == dep_modul_name:
                        continue

                    dep_module: BaseModuleInfo = MODULES_CLASSES.get(dep_modul_name)()
                    dep_tokens: list[str] | None = module.dest_token if isinstance(dep_module.dest_token, list) else [dep_module.dest_token]
                    dep_module_dest_network: str | None = dep_module.destination_network
                    
                    # Проверяю равняется ли сеть отправления сети получения и есть ли на выходе какой-нибудь токен,
                    # который нужен на входе другого модуля
                    if source_network == dep_module_dest_network and any(token in dep_tokens for token in source_tokens):
                        if all(all_available_wallet_balances.get(dep_module_dest_network, {}).get(token, 0) > dep_module.min_amount_residue
                               for token in dep_tokens if token
                        ):
                            # Если в сети назначения и отправления есть токены
                            if all(all_available_wallet_balances.get(source_network, {}).get(token, 0) > 0 for token in source_tokens) and \
                                all(all_available_wallet_balances.get(dep_module_dest_network, {}).get(token, 0) > 0 for token in dep_tokens):
                                # Отнимаю балансы в source (сети отправления)
                                for token in source_tokens:
                                    if token:
                                        all_available_wallet_balances[source_network][token] += module.min_amount_out
                                # Отнимаю балансы в destination (сети назначения)
                                for token in dep_tokens:
                                    if token:
                                        all_available_wallet_balances[dep_module_dest_network][token] -= dep_module.min_amount_out

                                graph[dep_modul_name].append(module_name)
        
        except Exception as error:
            self.logger_msg(None, None,
                            f"Error while building modules with dependencies.\nError: {error}", "error")
            return None

        return graph

    async def classic_generate_route(self) -> list[BaseModuleInfo]:
        from .modules_runner import Runner

        modules_data: Dict[str, Any] = {}

        try:
            # Получаем словарь с названиями и инстансами моделей
            all_available_modules: Dict[str, BaseModuleInfo] | None = {
                module_name: module_class()
                for module_name, module_class in MODULES_CLASSES.items()
            }

        except ValidationError as error:
            self.logger_msg(account_name, None,
                            f"Error while creating all available modules.\nError: {error}", "error")
            raise error

        if CLASSIC_ROUTES_MODULES_USING:
            modules_to_execute: list[str] = CLASSIC_ROUTES_MODULES_USING
            # Пробуем строить зависимости между модулями
            dependency_graph: Dict[str, list[str]] = await self.build_dependency_graph(CLASSIC_ROUTES_MODULES_USING)
            if dependency_graph:
                # Выполняем топологическую сортировку
                ordered_modules: list[str] | None = topological_sort(dependency_graph)
                if ordered_modules:
                    modules_to_execute = ordered_modules
        
        else:
            modules_to_execute = list(all_available_modules.keys())
            # modules_to_execute: list[str] = list(all_available_modules.keys())
            # dependency_graph: Dict[str, list[str]] = await self.build_dependency_graph(modules_to_execute)
            # if dependency_graph:
            #     ordered_modules: list[str] | None = topological_sort(dependency_graph)
            #     if ordered_modules:
            #         modules_to_execute = ordered_modules

        try:
            runner: Runner = Runner()
            accounts_data: list[Tuple[str, str]] = runner.get_wallets()

            for index, (account_name, private_key) in enumerate(accounts_data):
                proxy: str | None = runner.get_proxy_for_account(account_name)
                name_znc_domen: str | None = runner.get_name_znc_domen_for_account(account_name)
                client: Client = Client(account_name, private_key, proxy, name_znc_domen=name_znc_domen)

                all_available_wallet_balances: Dict[str, Dict[str, float]] = await client.get_wallet_balance(balance_in_eth=True)
                
                if not all_available_wallet_balances:
                    self.logger_msg(client.name, client.address,
                                    f"We can't get token balances on {client.name} account.", "warning")
                    return
       
                classic_route: Deque[list] | None = deque([])
                
                graph = await self.build_dependency_graph(modules_to_execute, all_available_wallet_balances)
                # Если не получилось сформировать зависимости
                if not graph:
                    # соберем классический маршрут
                    route = CLASSIC_ROUTES_MODULES_USING
                
                # TODO: остановился на этапе формирования пути
                # нужно выполнить топологическую сортировку
                # но она невозможна, если в графе есть циклы
                # я пробую удалить циклы, но все равно какая-то связанность присутствует
                ordered_route = topological_sort(graph)
                
                

                # Проходимся по модулям
                for module_name in modules_to_execute:
                    # Берем текущий модуль
                    module: BaseModuleInfo | None = all_available_modules.get(module_name)

                    if not module:
                        self.logger_msg(client.name, client.address,
                                        f"We can't find the module in available modules\nGo to the next module", "error")
                        continue
                    # Берем сети отправления и получения текущего модуля
                    source_network: Network | None = NETWORKS.get(module.source_network)
                    dest_network: Network | None = NETWORKS.get(module.destination_network)
                    # Если сеть отправления отсутствует, пропускаем
                    if not source_network:
                        self.logger_msg(client.name, client.address,
                                        f"Error while getting source network for accounting balance", "error")
                        continue

                    # Если отсутствует сеть назвачения, то она может быть равна сети отправления
                    if not dest_network:
                        dest_network = source_network
                    # Получаем названия токенов в сети отправления
                    current_tokens: list[str] = module.source_token if isinstance(module.source_token, list) else [module.source_token]

                    if any([curr_token is None for curr_token in current_tokens]):
                        self.logger_msg(client.name, client.address,
                                        f"Check source token in {module.module_name}. Perhaps, it contains None value.", "error")
                        raise SoftwareException

                    for curr_token in current_tokens:
                        source_curr_balance: float | None = all_available_wallet_balances.get(
                            source_network.name, {}).get(curr_token, 0)
                        
                        dest_curr_token: float | None = all_available_wallet_balances.get(
                            dest_network.name, {}).get(curr_token, 0)
                        
                        # Если не хватает баланса токена в сети отправления
                        if float(source_curr_balance) <= module.min_available_balance:
                            # self.logger_msg(client.name, client.address,
                            #                 f"We need to top up {source_network.name} network to execute {module.module_name}")

                            # Строим граф для построения зависимостей модуля по отношению к другим
                            graph: DefaultDict[str, list] = defaultdict(list)

                    # # Если у модуля есть source_token, тогда ищем зависимости
                        if module.source_token:
                            # Берем необходимые токены в сети отправления модуля
                            required_tokens: list[str] = module.source_token if isinstance(module, list) else [module.source_token]

                            # Ищем, как мы можем получить их из других модулей на выходе
                            for token in required_tokens:
                                for dependency_module_name, dependency_module in all_available_modules.items():
                                    if dependency_module.dest_token:

                                        provided_tokens: list[str] = dependency_module.dest_token \
                                            if isinstance(dependency_module, list) else [dependency_module.dest_token]

                                        if token in provided_tokens and module.source_network == dependency_module.destination_network:
                                            graph[dependency_module.module_name].append(module.module_name)

                            # Получаем модули, которые нужно выполнить перед текущим
                            required_modules_to_execute: list[str] | None = topological_sort(graph)

                            # Если нашли такие модули
                            if required_modules_to_execute:
                                if required_modules_to_execute:
                                    for _module_name in required_modules_to_execute:
                                        dependency_module_class: BaseModuleInfo | None = all_available_modules.get(_module_name)
                                        if not dependency_module_class:
                                            continue

                                        source_network_dependency: Network | None = NETWORKS.get(dependency_module_class.source_network)
                                        dest_network_dependency: Network | None = NETWORKS.get(dependency_module_class.destination_network)
                                    
                                        if not source_network_dependency:
                                            self.logger_msg(client.name, client.address,
                                                            f"Error while getting source network for accounting balance", "error")
                                            continue

                                        # Если отсутствует сеть назвачения, то она может быть равна сети отправления
                                        if not dest_network_dependency:
                                            dest_network_dependency = source_network_dependency

                                        # Получаем названия токенов зависимых модулей
                                        required_tokens: list[str] = dependency_module_class.source_token \
                                            if isinstance(dependency_module_class.source_token, list) else [dependency_module_class.source_token]

                                        # Проверяем балансы токенов в сетях зависимый модулей
                                        for req_token_name in required_tokens:
                                            # Получаем баланс токена в сети отправления
                                            source_token_balance: float | None = all_available_wallet_balances.get(
                                                dependency_module_class.source_network
                                            ).get(req_token_name, 0)
                                            # Получаем баланс токена в сети назвачения
                                            destination_token_balance: float | None = all_available_wallet_balances.get(
                                                dependency_module_class.source_network or dependency_module_class.destination_network
                                            ).get(dependency_module_class.dest_token, 0)
                                        
                                            # Если баланс токена > мин.доступное количество, то считаем балансы и добавляем в начало
                                            if float(source_token_balance) > dependency_module_class.min_available_balance:
                                                # if source_network is not dest_network:
                                                all_available_wallet_balances[source_network.name][req_token_name] = (
                                                    source_token_balance - dependency_module_class.min_amount_out
                                                )
                                                all_available_wallet_balances[dest_network.name][dependency_module_class.dest_token] = (
                                                    destination_token_balance + dependency_module_class.min_amount_out
                                                )
                                                classic_route.appendleft(dependency_module_class)
                        
                        else:
                            self.logger_msg(client.name, client.address,
                                            f"There is no any other dependency module for {module_name}", "warning")
                                
                    classic_route.append(module)
                
                account_data = {
                    "current_step": 0,
                    "route": [module_obj.model_dump() for module_obj in classic_route]
                }
                modules_data[account_name] = account_data

            # Записываем в файл
            try:
                with open(file="./data/service/wallets_progress.json", mode="a") as file:
                    json.dump(modules_data, file, indent=4)

            except Exception as error:
                self.logger_msg(None, None,
                                f"Error while saving classic generated route in file", "error")

            self.logger.info(
                f"Successfully generated {len(accounts_data)} classic routes into /data/services/wallets_progress.json"
            )

        except Exception as error:
            self.logger_msg(None, None,
                            f"Error in classic_generate_route method!\nError: {error}", "error")
            return

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

    # def sort_classic_route(self, route: list[str], landing_mode: bool) -> list[str]:
    #     """
    #     Create classic route

    #     Atributes:
    #         route - list of module names

    #     """
    #     if not landing_mode:
    #         modules_dependents: Dict[str, int] = {
    #             # TODO: в случае, если понадобится пополнение с биржи, то расскоментировать и написать модули

    #             # "okx_withdraw": 0,
    #             # "binance_withdraw": 0,
    #             # "bybit_withdraw": 0,
    #             # "bingx_withdraw": 0,
    #             # "bitget_withdraw": 0,
    #             # "bridge_native": 1,
    #         }

    #         classic_route = []

    #         for module_name in route:
    #             if module_name in modules_dependents:
    #                 classic_route.append((module_name), modules_dependents[module_name])
    #             else:
    #                 classic_route.append((module_name, 2))

    #         random.shuffle(classic_route)

    #         route_with_priority: list[str] = [
    #             module_name[0]
    #             for module_name in sorted(classic_route, key=lambda x: x[1])
    #         ]

    #     else:
    #         route_with_priority = route

    #     if CLASSIC_WITHDRAW_DEPENDENCIES:
    #         deposit_modules: Set = set([
    #             "deposit_module",
    #         ])
    #         new_route_with_dep = []

    #         for module_info in route_with_priority:
    #             module_name, rpc = module_info.split()
    #             new_route_with_dep.append(module_info)

    #             if module_name in deposit_modules:
    #                 withdraw_module_name = module_name.replace("deposit", "withdraw")
    #                 withdraw_module = get_func_by_name(withdraw_module_name)
    #                 new_route_with_dep.append(f"{withdraw_module.__name__} {rpc}")

    #     else:
    #         new_route_with_dep = route_with_priority

    #     return new_route_with_dep
    
    async def get_available_modules(
            self,
            all_available_modules: dict[str, BaseModuleInfo],
            executed_modules: set[str],
            all_available_wallet_balances: dict[str, dict[str, float]],
            required_modules_to_execute: set[str],
            client: Client,
            is_first_run: bool = False,
        ) -> list[BaseModuleInfo] | None: 

        available_modules: Deque[BaseModuleInfo] | None = deque([])

        if not is_first_run:
            required_modules_to_execute: set[str] = all_available_modules.keys()

        try:
            for module_name in required_modules_to_execute:
                required_module_to_execute: BaseModuleInfo | None = all_available_modules.get(module_name)

                if not required_module_to_execute:
                    self.logger_msg(client.name, client.address,
                                    f"There is no network for required module {module_name}")
                    continue

                if required_module_to_execute.module_type == "bridge":
                    if required_module_to_execute.destination_network and \
                        required_module_to_execute.destination_network in PRIORITY_NETWORK_NAMES:

                            source_network: Network | None = NETWORKS.get(required_module_to_execute.source_network)
                            destination_network: Network | None = NETWORKS.get(required_module_to_execute.destination_network)

                            if not destination_network:
                                self.logger_msg(client.name, client.address,
                                        f"There is no destination network {required_module_to_execute.destination_network}")
                                continue

                            token_balances_in_destination_network: float = all_available_wallet_balances.get(
                                destination_network.name, {}).get(destination_network.token, 0
                            )

                            if token_balances_in_destination_network == 0 or \
                                float(token_balances_in_destination_network) <= required_module_to_execute.min_available_balance:
                                    
                                    deposit_modules: list[BridgeModuleInfo] | None = []

                                    if USE_L2_TO_DEPOSIT:
                                        deposit_modules: list[BridgeModuleInfo] | None = [
                                            module_class
                                            for module_class in all_available_modules.values()
                                            if module_class.module_type == "bridge" and \
                                                module_class.destination_network == required_module_to_execute.destination_network and \
                                                    module_class.required_on_first_run is False
                                        ]
                                    elif not USE_L2_TO_DEPOSIT:
                                        deposit_modules: list[BridgeModuleInfo] | None = [
                                            module_class
                                            for module_class in all_available_modules.values()
                                            if module_class.module_type == "bridge" and \
                                                module_class.destination_network == required_module_to_execute.destination_network and \
                                                    module_class.required_on_first_run is True
                                        ]

                                    # Все модули бриджей, которые могут пополнить баланс в сети назначения
                                    all_deposit_modules: list[BridgeModuleInfo] | None = [
                                        module_class
                                        for module_class in all_available_modules.values()
                                        if module_class.module_type == "bridge" and \
                                            module_class.destination_network == required_module_to_execute.destination_network
                                    ]

                                    # Получаем баланс в сети назначения до пополнения
                                    destination_token_balance_before_deposit: float = all_available_wallet_balances.get(
                                        destination_network.name, {}).get(destination_network.token, 0)
                                    
                                    # Получаем баланс в сети отправки до пополнения
                                    source_balance_before_deposit: float = all_available_wallet_balances.get(
                                        source_network.name, {}).get(source_network.token, 0)
                                    
                                    # Для сравнения баланса в сети назначения после пополнения
                                    token_balance_after_deposit: float = destination_token_balance_before_deposit

                                    # Проверяем баланс в сети отправления
                                    for deposit_module in deposit_modules:
                                        source_network: Network | None = NETWORKS.get(deposit_module.source_network)

                                        source_network_token_balance: float | None = all_available_wallet_balances.get(
                                            source_network.name, {}).get(source_network.token, 0
                                        )
                                        expected_balance_after_deposit_source: float = float(
                                            source_network_token_balance - deposit_module.min_amount_out
                                        )
                                        # Если баланс в сети отправки больше минимального баланса, то добавляем модуль в список
                                        if float(source_network_token_balance) > required_module_to_execute.min_available_balance:
                                            available_modules.appendleft(deposit_module)

                                            # if required_module_to_execute.module_type != "bridge":
                                            # Обновляем баланс в сети назначения
                                            available_modules.append(required_module_to_execute)
                                            all_available_wallet_balances[destination_network.name][source_network.token] = (
                                                destination_token_balance_before_deposit + float(deposit_module.min_amount_out)
                                            )
                                            
                                            # all_available_wallet_balances.setdefault(
                                            #     destination_network.name, {}
                                            #     ).setdefault(source_network.token, 0 + float(deposit_module.min_amount_out))
                                            
                                            # Обновляем баланс в сети отправки
                                            all_available_wallet_balances[source_network.name][source_network.token] = (
                                                source_balance_before_deposit - float(deposit_module.min_amount_out)
                                            )
                                            
                                            # all_available_wallet_balances.setdefault(
                                            #     source_network.name, {}
                                            # ).setdefault(source_network.token, 0 - float(deposit_module.min_amount_out))

                                            token_balance_after_deposit += float(deposit_module.min_amount_out)

                                            # networks_being_deposited.add(destination_network.name)
                                            # required_module_to_execute.dependencies.required_modules.add(deposit_module.module_name) #
                                    
                                    # Если не нашли мост, который бы пополнил, то тогда проверяем все мосты
                                    if all_deposit_modules and destination_token_balance_before_deposit == token_balance_after_deposit and \
                                        is_first_run:
                                        for deposit_module in all_deposit_modules:
                                            source_network: Network | None = NETWORKS.get(deposit_module.source_network)

                                            source_network_token_balance: float | None = all_available_wallet_balances.get(
                                                source_network.name, {}).get(source_network.token, 0
                                            )
                                            # Если баланс в сети отправки больше минимального баланса, то добавляем модуль в список
                                            if float(source_network_token_balance) > required_module_to_execute.min_available_balance and \
                                                deposit_module.module_name not in executed_modules:
                                                available_modules.appendleft(deposit_module)

                                                # if required_module_to_execute.module_type != "bridge":
                                                # Обновляем баланс в сети назначения
                                                available_modules.append(required_module_to_execute)
                                                all_available_wallet_balances[destination_network.name][source_network.token] = (
                                                    destination_token_balance_before_deposit + float(deposit_module.min_amount_out)
                                                )
                                                # available_modules.append(required_module_to_execute)
                                                # all_available_wallet_balances.setdefault(
                                                #     destination_network.name, {}
                                                #     ).setdefault(source_network.token, 0 + float(deposit_module.min_amount_out))
                                                # Обновляем баланс в сети отправки
                                                all_available_wallet_balances[source_network.name][source_network.token] = (
                                                    source_balance_before_deposit - float(deposit_module.min_amount_out)
                                                )
                                                # all_available_wallet_balances.setdefault(
                                                #     source_network.name, {}
                                                # ).setdefault(source_network.token, 0 - float(deposit_module.min_amount_out))

                            elif required_module_to_execute.module_type == "swap":
                                available_modules.append(required_module_to_execute)
                            
                            else:
                                continue

                            # else:
                            #     self.logger_msg(client.name, client.address,
                            #                     f"Can't find balance in destination network for module {required_module_to_execute.module_name}\nGo to next required module")
                            #     continue
                else:
                    available_modules.append(required_module_to_execute)
            # Если нет модулей бриджей и это у нас первый запуск, то выводим ошибку
            if not any(module_class for module_class in available_modules
                        if module_class.module_type == "bridge") and \
                             is_first_run:
                self.logger_msg(client.name, client.address,
                                f"There is no bridge modules in the route!", "warning")
                return
                raise SoftwareException(f"There is no bridge modules in the route! Check the balance on the wallet {client.address}")

        except SoftwareException as error:
            sys.exit(1)

        except Exception as error:
            self.logger_msg(client.name, client.address,
                            f"Error while getting available modules.\nError: {error}", "error")
            return
        
        return available_modules

    async def smart_generate_route( # генерация умного маршрута
            self,
            account_name: str,  # имя аккаунта
            private_key: str,  # приватный ключ
            proxy: str | None,   # прокси
            name_znc_domen: str | None = None  # доменное имя
        ) -> None:

        route_modules_dict: Dict[str, BaseModuleInfo] = {}   # Определяем модули для маршрута, пока пустой словарь

        try:
            try:
                all_available_modules: Dict[str, BaseModuleInfo] | None = {
                    module_name: module_class()
                    for module_name, module_class in MODULES_CLASSES.items()
                }   # Тут мы получили абсолютно все доступные модули которые имеются

            except ValidationError as error:
                self.logger_msg(account_name, None,
                                f"Error while creating all available modules.\nError: {error}", "error")
                raise error

            if not all_available_modules:
                self.logger_msg(account_name, None,
                                f"There is no any module for account {account_name}", "warning")
                raise SoftwareException

            client: Client = Client(account_name, private_key, proxy, name_znc_domen=name_znc_domen)   # Создаём клиента
            all_available_wallet_balances: Dict[str, Dict[str, int]] = await client.get_wallet_balance()    # Возвращаем балансы всех токенов 

            if not all_available_wallet_balances:   # Если нет балансов выкидываем исключение
                self.logger_msg(account_name, None,
                                f"There is no any wallet balance for acccount {account_name}", "error")
                return

            # 1. Проверяем, запускаем ли мы софт впервые
            is_first_run: bool = await self.check_first_run_modules(account_name)

            suitable_modules: list[BaseModuleInfo] = []
            executed_modules: Dict[str, Set[str]] = self.history.get(account_name, set())   # Список уже выполненных модулей

            try:  # Получаем список обязательных модулей для выполнения:
                required_modules_to_execute: list[str] = RequiredModulesToExecute().required_modules

            except Exception as error:
                self.logger_msg(account_name, None,
                                f"Error while getting required modules to execute.\nError: {error}", "error")

            if required_modules_to_execute:
                required_modules_to_execute: Set[str] = set(required_modules_to_execute)   # Создаём множество для вычитания
                required_modules_to_execute: Set[str] = required_modules_to_execute - executed_modules  # Отнимаем выполненые от обязательных и получаем обязательные невыполненные

            # Самая важная часть кода
            available_modules: list[BaseModuleInfo] | None = await self.get_available_modules(
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
                # TODO: тут пока что обновление не работает
                filepath = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    "data",
                    "service",
                    "wallets_progress.json"
                )
                with open(file=filepath, mode="w") as file:
                    if os.path.getsize(filepath) == 0:
                        json.dump(route_modules_dict, file, indent=4)
                    else:
                        data: Dict[str, Any] = json.load(file)
                        data.setdefault(account_name, {}).setdefault("route", []).extend(
                            [module_obj for module_obj in route_modules_dict[account_name]["route"]]
                        )
                        json.dump(data, file, indent=4)

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


async def classic_route_generate():
    clean_progress_file()
    generator: RouteGenerator = RouteGenerator()
    await generator.classic_generate_route()
