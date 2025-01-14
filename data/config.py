from typing import Callable, Dict

from functions import bridge_native_worker, bridge_owlto_worker, bridge_gg_worker
from modules.interfaces import BridgeNativeModule, BaseModuleInfo, BridgeOwltoModule, BridgeGGModule
from utils.networks import Ethereum, Ink
from utils.tools import get_accounts_data


"""
Available modules:
    - bridge_native
    - bridge_gg

"""

# Mapping of module names to module classes
MODULES_CLASSES: Dict[str, BaseModuleInfo] = {
    "bridge_native": BridgeNativeModule,
    "bridge_gg": BridgeGGModule,
    "bridge_owlto": BridgeOwltoModule,
}

CHAIN_NAMES: Dict[int, str] = {
    0: Ethereum.name,
    1: Ink.name,
}

# Mapping of module names to module functions
MODULE_RUNNERS: Dict[str, Callable] = {
    "bridge_native": bridge_native_worker,
    "bridge_gg": bridge_gg_worker,
    "bridge_owlto": bridge_owlto_worker,
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