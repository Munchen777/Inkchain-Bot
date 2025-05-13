import asyncio

from typing import Callable, Dict, List, Tuple

from core.bot import InkBot
from core.exceptions import ConfigurationError
from console import Console
from interfaces import BaseModuleInfo
from loader import (
    config,
    semaphore,
)
from logger import log
from models import Account
from settings import MODULES_CLASSES
from utils import (
    get_address,
    random_sleep,
)


async def process_execution(account: Account,
                            selected_module_name: str,
                            process_func: Callable,
                            ) -> Tuple[bool, str]:
    address: str = get_address(account.private_key)
    module_model: BaseModuleInfo | None = MODULES_CLASSES.get(selected_module_name, None)

    if not module_model:
        raise ConfigurationError(f"Not found settings for {selected_module_name} module")

    async with semaphore:
        try:
            if config.delay_before_start.min > 0:
                await random_sleep(
                    address, config.delay_before_start.min, config.delay_before_start.max
                )
            result: Tuple[bool, str] = await process_func(account, module_model())
            success: bool = (
                result[0]
                if isinstance(result, tuple) and len(result) == 2
                else bool(result)
            )
            message: str = (
                result[1]
                if isinstance(result, tuple) and len(result) == 2
                else (
                    f"Account: {address} successfully executed {selected_module_name}"
                    if success else f"Account: {address} failed to execute {selected_module_name}"
                )
            )
            return success, message

        except Exception as error:
            log.error(f"Account: {address} | Error: {error}")
            return False, str(error)


class Runner:
    __slots__ = (
        "console",
        "module_functions",
    )
    EXCLUDED_MODULES = {
        "exit",
    }

    def __init__(self) -> None:
        self.console: Console = Console()

        self.module_functions: Dict[str, Callable] = {}

        for attr_name in dir(InkBot):
            if attr_name.startswith('process_'):
                module_name = attr_name[8:]
                if module_name not in self.EXCLUDED_MODULES:
                    self.module_functions[module_name] = getattr(InkBot, attr_name)

    async def execute(self) -> bool:
        self.console.build()

        match config.module:
            case "exit":
                log.info("❗️ Exiting software ...")
                return True

            case module if module in self.module_functions:
                async def process_account(account):
                    success, message = await process_execution(account, module, self.module_functions[config.module])
                    if success:
                        log.success(message)
                    else:
                        log.error(message)
                    return success, message

                tasks: List[asyncio.Task] = []
                async with asyncio.TaskGroup() as tg:
                    for account in config.accounts:
                        tasks.append(tg.create_task(coro=process_account(account)))

                results: List[asyncio.Future] = [task.result() for task in tasks]

                # for result in results:
                #     if result.cancelled():
                #         result.cancel()

                if config.delay_between_tasks.min > 0:
                    await random_sleep(
                        None, config.delay_between_tasks.min, config.delay_between_tasks.max,
                    )

                return False

            case _:
                log.error(f"Module {config.module} is not implemented!")
                return False
