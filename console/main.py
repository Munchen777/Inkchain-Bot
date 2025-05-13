import inquirer
import os
import sys

from colorama import Fore
from inquirer.themes import GreenPassion
from rich.console import Console as RichConsole
from rich import box
from rich.table import Table
from rich.panel import Panel
from typing import Dict, List, Tuple

from loader import config


class Console:
    MODULES: Tuple[str] = (

        "Exit",

        "Owlto Bridge OP to Ink",
        "Owlto Bridge Ink to OP",
        "Owlto Bridge Base to Ink",
        "Owlto Bridge Ink to Base",

        "Relay Bridge OP to Ink",
        "Relay Bridge Ink to OP",
        "Relay Bridge Base to Ink",
        "Relay Bridge Ink to Base",

        "BridgeGG Ethereum to Ink",
        "Claim Daily GM",
        "Claim ZNS Domen",
        "Mint Paragraph NFT",
    )

    MODULES_DATA: Dict[str, str] = {

        "Exit": "exit",

        "Owlto Bridge OP to Ink": "bridge_owlto_op_to_ink",
        "Owlto Bridge Ink to OP": "bridge_owlto_ink_to_op",
        "Owlto Bridge Base to Ink": "bridge_owlto_base_to_ink",
        "Owlto Bridge Ink to Base": "bridge_owlto_ink_to_base",

        "Relay Bridge OP to Ink": "bridge_relay_op_to_ink",
        "Relay Bridge Ink to OP": "bridge_relay_ink_to_op",
        "Relay Bridge Base to Ink": "bridge_relay_base_to_ink",
        "Relay Bridge Ink to Base": "bridge_relay_ink_to_base",

        "BridgeGG Ethereum to Ink": "bridge_gg_ethereum_to_ink",

        "Claim Daily GM": "claim_daily_gm",
        "Claim ZNS Domen": "buy_znc_domen_ink_network",
        "Mint Paragraph NFT": "mint_paragraf_nft",
    }

    def __init__(self) -> None:
        self.rich_console: RichConsole = RichConsole()

    @staticmethod
    def prompt(data: List):
        answers = inquirer.prompt(data, theme=GreenPassion())
        return answers

    def get_module(self, modules: Tuple[str] | List[str]) -> str:
        questions = [
            inquirer.List(
                "module",
                message=Fore.LIGHTBLACK_EX + "Select the module",
                choices=modules,
            ),
        ]
        answers = self.prompt(questions)
        return answers.get("module")

    def display_info(self):
        table = Table(title="System Configuration", box=box.ROUNDED)
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("Accounts", str(len(config.accounts)))
        table.add_row("Threads", str(config.threads))
        table.add_row(
            "Delay before start",
            f"{config.delay_before_start.min} - {config.delay_before_start.max} sec."
        )

        panel: Panel = Panel(
            table,
            expand=False,
            border_style="green",
            title="[bold yellow]System Information[/bold yellow]",
            subtitle="[italic]Use arrow keys to navigate[/italic]",
        )
        self.rich_console.print(panel)

    def build(self) -> None:
        self.display_info()
        module: str = self.get_module(self.MODULES)
        config.module = self.MODULES_DATA[module]
