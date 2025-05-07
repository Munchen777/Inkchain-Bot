import asyncio
import sys
import subprocess

from questionary import select, Choice

from utils.route_generator import RouteGenerator, classic_route_generate
from utils.modules_runner import Runner
from utils.tools import check_progress_file
from data.config import TITLE


def are_you_sure(module=None, gen_route:bool = False):
    if gen_route or check_progress_file():
        answer = select(
            '\n⚠️⚠️⚠️ THIS ACTION CANCELS OTHER PREVIOUS PROGRESSES FOR CLASSIC ROUTES, continue? ⚠️⚠️⚠️ \n',
            choices=[
                Choice("❌ NO", 'main'),
                Choice("✅ YES", 'module'),
            ],
            qmark='☢️',
            pointer='👉'
        ).ask()
        print()
        if answer == 'main':
            main()
        else:
            if module:
                module()


def main():
    print(TITLE)
    print(
        "\033[32m💬 Updates and code support ➡️  https://t.me/divinus_xyz  🍀 Subscribe 🍀 \033[0m"
    )
    print()
    try:
        while True:
            answer = select(
                "What do you want to do?",
                choices=[
                    Choice("🤖 Start running smart routes", "smart_routes_run"),
                    Choice(
                        "🚀 Start running classic routes for each wallet",
                        "classic_routes_run",
                    ),
                    Choice(
                        "📄 Generate classic-route for each wallet",
                        "classic_routes_gen",
                    ),
                    Choice(
                        "🛜 Check proxies connection",
                        "check_proxy",
                    ),
                    Choice(" ❌ Exit", "exit"),
                ],
                qmark="🛠️",
                pointer="👉",
            ).ask()

            runner = Runner()

            if answer == "smart_routes_run":
                asyncio.run(runner.run(smart_route=True))

            elif answer == "classic_routes_run":
                asyncio.run(runner.run(smart_route=False))

            elif answer == "classic_routes_gen":
                # generator = RouteGenerator()
                asyncio.run(classic_route_generate())

            elif answer == "check_proxy":
                asyncio.run(runner.check_proxies_status())

            elif answer == "exit":
                sys.exit()

    except KeyboardInterrupt:
        print("\nExiting the program by signal <Ctrl+C>")
        sys.exit()


def install_requirements():
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while installing requirements: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # install_requirements()
    main()