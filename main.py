import asyncio
import os
import sys

from logger import log
from modules_runner import Runner


async def main():
    log.info(f"✅ Software starts ...")

    while True:
        try:
            exit_flag: bool = await Runner().execute()
            if exit_flag:
                break
        except KeyboardInterrupt:
            log.warning("🚨 Manual interruption!")

        input("\nPress Enter to return to menu...")

    log.info(f"✅ Software stops work ...")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
