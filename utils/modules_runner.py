import asyncio
import json
import random
import re
import telebot

from random import shuffle
from typing import Any, Callable, Dict, List, Tuple

from data.config import (ACCOUNT_NAMES, PRIVATE_KEYS, PROXIES, CHAIN_NAMES, MODULE_RUNNERS)
from generall_settings import (WALLETS_TO_WORK, SHUFFLE_WALLETS, SOFTWARE_MODE, USE_PROXY,
                               ACCOUNTS_IN_STREAM, GLOBAL_NETWORK, SAVE_PROGRESS, TELEGRAM_NOTIFICATIONS, BREAK_ROUTE,
                               SLEEP_MODE, SLEEP_TIME_ACCOUNTS, SLEEP_TIME_MODULES, TG_ID, TG_TOKEN)
from modules import Logger
from modules.interfaces import BaseModuleInfo
from utils.tools import clean_progress_file
from utils.route_generator import get_func_by_name, RouteGenerator
from utils.client import SoftwareException, CustomAsyncHTTPProvider, CustomAsyncWeb3
from utils.networks import Ethereum


class Runner(Logger):

    async def smart_sleep(self, account_name: str, account_number: int, accounts_delay: bool):
        if SLEEP_MODE and account_number:
            if accounts_delay:
                duration = random.randint(*tuple(sec * account_number for sec in SLEEP_TIME_ACCOUNTS))
            else:
                duration = random.randint(*SLEEP_TIME_MODULES)

            self.logger_msg(account_name, None, f"Sleeping for {duration:.2f} seconds", "info")
            await asyncio.sleep(duration)

    @staticmethod
    def get_wallets() -> List[Tuple[str, str]]:
        accounts_data = []

        if WALLETS_TO_WORK == 0:
            accounts_data = zip(ACCOUNT_NAMES, PRIVATE_KEYS)

        elif isinstance(WALLETS_TO_WORK, int):
            accounts_data = zip(
                [ACCOUNT_NAMES[WALLETS_TO_WORK - 1]],
                [PRIVATE_KEYS[WALLETS_TO_WORK - 1]],
            )

        elif isinstance(WALLETS_TO_WORK, tuple):
            accounts_data = zip(
                [ACCOUNT_NAMES[i - 1] for i in WALLETS_TO_WORK],
                [PRIVATE_KEYS[i - 1] for i in WALLETS_TO_WORK],
            )

        elif isinstance(WALLETS_TO_WORK, list):
            range_count = range(WALLETS_TO_WORK[0], WALLETS_TO_WORK[1] + 1)
            accounts_data = zip(
                [ACCOUNT_NAMES[i - 1] for i in range_count],
                [PRIVATE_KEYS[i - 1] for i in range_count],
            )

        accounts_data = list(accounts_data)

        if SHUFFLE_WALLETS:
            shuffle(accounts_data)

        return accounts_data

    async def send_tg_message(self, account_name: str, message_to_send, disable_notification: bool):
        try:
            await asyncio.sleep(1)
            str_send = '*' + '\n'.join([re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', message)
                                       for message in message_to_send]) + '*'
            bot = telebot.TeleBot(TG_TOKEN)
            bot.send_message(TG_ID, str_send, parse_mode='MarkdownV2', disable_notification=disable_notification)
            print()
            self.logger_msg(account_name, None, f"The message was sent in Telegram", 'success')

        except Exception as error:
            self.logger_msg(account_name, None, f"Telegram | Error API: {error}", 'error')

    @staticmethod
    def get_wallets_batch(account_list: tuple = None):
        range_count = range(account_list[0], account_list[-1])
        return zip(
            [ACCOUNT_NAMES[i - 1] for i in range_count],
            [PRIVATE_KEYS[i - 1] for i in range_count],
        )

    @staticmethod
    def collect_bad_wallets(account_name: str, module_name: str):
        try:
            with open("./data/service/bad_wallets.json", "r") as file:
                data = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError) as error:
            data = {}

        data.setdefault(str(account_name), []).append(module_name)

        with open("./data/service/bad_wallets.json", "w") as file:
            json.dump(data, file, indent=4)

    def get_proxy_for_account(self, account_name: str) -> str | None:
        if USE_PROXY:
            try:
                account_number = ACCOUNT_NAMES.index(account_name)
                num_proxies = len(PROXIES)
                return PROXIES[account_number % num_proxies]

            except Exception as error:
                self.logger.error(f"Account: {account_name} works without proxy")
                return None

    async def check_proxy_status(self, proxy: str | None):
        """ Check proxy separately for connection to Ethereum RPC """
        request_kwargs: Dict[str, Any] = {
            "proxy": proxy,
            "verify_ssl": False,
            "timeout": 300
        } if proxy else {"verify_ssl": False, "timeout": 300}

        try:
            w3 = CustomAsyncWeb3(
                CustomAsyncHTTPProvider(
                    random.choice(Ethereum.rpc),
                    request_kwargs=request_kwargs
                )
            )
            if await w3.is_connected():
                self.logger.info(f"Proxy: {proxy} successfully connected to Ethereum RPC")
                return True
            
            self.logger.error(f"Proxy: {proxy} can't connect to Ethereum RPC")
            return False

        except Exception as error:
            self.logger.error(f"Proxy: {proxy} | Error: {error}")
            return False

    async def check_proxies_status(self):
        """ Checks all proxies for connection """
        tasks: List[asyncio.Task] = [
            asyncio.create_task(
                self.check_proxy_status(proxy)
            )
            for proxy in PROXIES
        ]
        await asyncio.gather(*tasks)

    @staticmethod
    def load_routes():
        """ Load routes from wallets_progress.json file """
        with open("./data/service/wallets_progress.json", "r") as file:
            return json.load(file)

    def update_step(self, account_name: str, current_step: int, module_name: str):
        wallets = self.load_routes()
        wallets[str(account_name)]["current_step"] = current_step
        route_modules: List[Dict[str, Any]] = wallets[str(account_name)]["route"]

        for module_dict in route_modules:
            if module_dict.get("module_name") == module_name:
                try:
                    module_dict["count_of_operations"] += 1
                    break

                except (KeyError, Exception) as error:
                    self.logger_msg(account_name, None,
                                    f"Error while updating counter of successful transactions: {error}", "error")

        with open("./data/service/wallets_progress.json", "w") as file:
            json.dump(wallets, file, indent=4)

    async def run_account_modules(self, account_name: str, private_key: str, proxy: str | None, smart_route: bool, index: int, route_generator: RouteGenerator | None, parallel_mode: bool = False):
        message_list, result_list, route_paths, break_flag, module_counter = [], [], [], False, 0

        try:
            route_data: Dict[str, Any] = self.load_routes()

            if not route_data:
                raise SoftwareException("Route isn't available")

            route_modules: List[BaseModuleInfo | None] = [
                RouteGenerator.create_route_from_dict(module_data)
                for module_data in route_data.get(str(account_name), {}).get("route", [])
            ]

            current_step = 0
            if SAVE_PROGRESS:
                current_step = route_data.get(str(account_name), {}).get("current_step", 0)

            message_list.append(
                f'⚔️| Account name: "{account_name}"\n \n{len(route_modules)} module(s) in route\n')

            if current_step >= len(route_modules):
                self.logger_msg(
                    account_name, None, f"All modules of route have finished!", type_msg='warning')
                return

            while current_step < len(route_modules):
                module_counter += 1
                current_module: BaseModuleInfo = route_modules[current_step]
                module_name: str = current_module.module_name
                module_func: Callable | None = MODULE_RUNNERS.get(module_name)

                if not module_func:
                    raise SoftwareException(f"Module function not found: {module_name}")

                module_display_name: str = current_module.module_display_name

                if parallel_mode and module_counter == 1:
                    await self.smart_sleep(account_name, index, accounts_delay=True)

                self.logger_msg(account_name, None, f"Launch module: {module_display_name}")

                module_input_data: List[str, str, str, BaseModuleInfo] = [
                    account_name, private_key, proxy, current_module
                ]

                try:
                    result = await module_func(*module_input_data)

                except Exception as error:
                    info = f"Module name: {module_display_name} | Error {error}"
                    self.logger_msg(
                        account_name, None, f"Error while working: {info}", type_msg='error')
                    result = False

                if result:
                    self.update_step(account_name, current_step + 1, current_module.module_name)

                    if not (current_step + 2) > (len(route_modules)):
                        await self.smart_sleep(account_name, account_number=1, accounts_delay=True)

                else:
                    self.collect_bad_wallets(account_name, module_name)
                    result = False

                    if BREAK_ROUTE:
                        message_list.extend([f'❌   {module_display_name}\n', f'💀 The route was broken!\n'])
                        account_progress = (False, current_module.module_name, account_name)
                        result_list.append(account_progress)
                        break

                if route_generator:
                    await route_generator.add_executed_module(account_name, current_module.module_name)

                current_step += 1
                message_list.append(f'{"✅" if result else "❌"}   {module_display_name}\n')
                account_progress = (result, current_module.module_name, account_name)
                result_list.append(account_progress)
                await self.smart_sleep(account_name, index, accounts_delay=True)
    
            success_count = len([1 for i in result_list if i[0]])
            errors_count = len(result_list) - success_count
            message_list.append(f'Total result:    ✅   —   {success_count}    |    ❌   —   {errors_count}')

            if TELEGRAM_NOTIFICATIONS:
                if errors_count > 0:
                    disable_notification = False

                else:
                    disable_notification = True

                await self.send_tg_message(account_name, message_to_send=message_list,
                                           disable_notification=disable_notification)

            if not SOFTWARE_MODE:
                self.logger_msg(None, None, f"Launch further wallet!", 'info')

            else:
                self.logger_msg(account_name, None, f"Wait for other wallets in stream!", 'info')
        
        except Exception as error:
            self.logger_msg(
                account_name, None, f"Error while running: {error}", "error"
            )

    async def run_parallel(self, smart_route: bool, route_generator: RouteGenerator | None):
        selected_wallets = list(self.get_wallets())
        num_accounts = len(selected_wallets)
        accounts_per_stream = ACCOUNTS_IN_STREAM
        num_streams, remainder = divmod(num_accounts, accounts_per_stream)

        if smart_route:
            clean_progress_file()

        for stream_index in range(num_streams + (remainder > 0)):
            start_index = stream_index * accounts_per_stream
            end_index = (stream_index + 1) * accounts_per_stream if stream_index < num_streams else num_accounts

            accounts: List[Tuple[str, str]] = selected_wallets[start_index: end_index]
            proxies: List[str | None] = [
                self.get_proxy_for_account(account_name[0]) for account_name in accounts
            ]

            if smart_route:
                for (account_name, private_key), proxy in zip(accounts, proxies):
                    try:
                        await route_generator.smart_generate_route(account_name, private_key, proxy)

                    except Exception as error:
                        self.logger_msg(account_name, None,
                                        f"Error while generating route for account_name: {account_name} in parallel mode\nError: {error}",
                                        "error")
                        continue

            tasks: List[asyncio.Task] = [
                asyncio.create_task(
                    self.run_account_modules(
                        account_name, private_key, self.get_proxy_for_account(account_name),
                        smart_route, index, route_generator, parallel_mode=True,
                    )
                )
                for index, (account_name, private_key) in enumerate(accounts)
            ]

            result_list = await asyncio.gather(*tasks, return_exceptions=True)

            for result in result_list:
                if isinstance(result, Exception):
                    raise result
            
            # if smart_route:
                # clean_progress_file()
            
            self.logger_msg(None, None, f"Wallets in stream completed their tasks, launching next stream\n", "success")

        self.logger_msg(None, None, f"All wallets completed their tasks in parallel mode", "success")

    async def run_consistently(self, smart_route: bool, route_generator: RouteGenerator | None):
        accounts_data: List[Tuple[str, str]] = self.get_wallets()

        for index, (account_name, private_key) in enumerate(accounts_data):
            proxy: str | None = self.get_proxy_for_account(account_name)
            if smart_route:
                await route_generator.smart_generate_route(account_name, private_key, proxy)

            result = await self.run_account_modules(
                account_name, private_key, proxy,
                smart_route, index, route_generator
            )

    async def run(self, smart_route: bool):
        route_generator: RouteGenerator | None = None

        if smart_route:
            route_generator = RouteGenerator()

        try:
            if SOFTWARE_MODE:
                await self.run_parallel(smart_route, route_generator)
            else:
                await self.run_consistently(smart_route, route_generator)

        except SoftwareException as error:
            self.logger.error(
                f"Error: {error}"
            )
