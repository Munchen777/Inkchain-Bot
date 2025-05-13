import asyncio
import random

from eth_account import Account

from logger import log


async def random_sleep(account_name: str | None = "None", min_delay: int = 30, max_delay: int = 60) -> None:
    delay: int = random.randint(min_delay, max_delay)
    minutes, seconds = divmod(delay, 60)
    template = (
        f"Account {account_name} | Sleep "
        f"{int(minutes)}m {seconds:.1f}s" if minutes > 0 else 
        f"Account {account_name} | Sleep {seconds:.1f}s"
    )
    log.info(template)
    await asyncio.sleep(delay)


def get_address(private_key: str) -> str:
    return Account.from_key(private_key).address
