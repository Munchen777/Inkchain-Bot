from typing import Callable, Dict

from functions import*
from modules.interfaces import*
from utils.networks import Ethereum, Ink
from utils.tools import get_accounts_data


"""
Available modules:
    - bridge_native
    - bridge_owlto_op_to_ink

"""

# Mapping of module names to module classes
MODULES_CLASSES: Dict[str, BaseModuleInfo] = {
    "bridge_native": BridgeNativeModule,
    "bridge_owlto_op_to_ink": BridgeOwltoOPtoInkModule,
}

CHAIN_NAMES: Dict[int, str] = {
    0: Ethereum.name,
    1: Ink.name,
}

# Mapping of module names to module functions
MODULE_RUNNERS: Dict[str, Callable] = {
    "bridge_native": bridge_native,
    "bridge_owlto_op_to_ink": bridge_owlto_op_to_ink
}

ACCOUNT_NAMES, PRIVATE_KEYS, PROXIES = get_accounts_data()

TITLE = """\033[33m
 /$$$$$$           /$$                           /$$                 /$$                 /$$$$$$$              /$$    
|_  $$_/          | $$                          | $$                |__/                | $$__  $$            | $$    
  | $$   /$$$$$$$ | $$   /$$  /$$$$$$   /$$$$$$$| $$$$$$$   /$$$$$$  /$$ /$$$$$$$       | $$  \ $$  /$$$$$$  /$$$$$$  
  | $$  | $$__  $$| $$  /$$/ /$$__  $$ /$$_____/| $$__  $$ |____  $$| $$| $$__  $$      | $$$$$$$  /$$__  $$|_  $$_/  
  | $$  | $$  \ $$| $$$$$$/ | $$  \ $$| $$      | $$  \ $$  /$$$$$$$| $$| $$  \ $$      | $$__  $$| $$  \ $$  | $$    
  | $$  | $$  | $$| $$_  $$ | $$  | $$| $$      | $$  | $$ /$$__  $$| $$| $$  | $$      | $$  \ $$| $$  | $$  | $$ /$$
 /$$$$$$| $$  | $$| $$ \  $$|  $$$$$$/|  $$$$$$$| $$  | $$|  $$$$$$$| $$| $$  | $$      | $$$$$$$/|  $$$$$$/  |  $$$$/
|______/|__/  |__/|__/  \__/ \______/  \_______/|__/  |__/ \_______/|__/|__/  |__/      |_______/  \______/    \___/  
                                                                                                                      
                                                                                                                      
                                                                                                                      

                                                                         
                                                                         
\033[0m                                                                                                        \033[32m@divinus.xyz\033[0m 
"""