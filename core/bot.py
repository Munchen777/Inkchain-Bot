from typing import Tuple

from models import Account
from .modules import (
    BridgeOwltoOPtoInkWorker,
    BridgeOwltoInkToOPWorker,
    BridgeOwltoBaseToInkWorker,
    BridgeOwltoInkToBaseWorker,

    BridgeRelayOPtoInkWorker,
    BridgeRelayInkToOPWorker,
    BridgeRelayBaseToInkWorker,
    BridgeRelayInkToBaseWorker,

    BridgeGGEthereumToInkWorker,

    ClaimDailyGMWorker,
    ZNSDomenWorker,

    MintParagraphNFTWorker,
)


class InkBot:
    @staticmethod
    async def process_bridge_owlto_op_to_ink(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeOwltoOPtoInkWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_owlto_ink_to_op(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeOwltoInkToOPWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_owlto_base_to_ink(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeOwltoBaseToInkWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_owlto_ink_to_base(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeOwltoInkToBaseWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_relay_op_to_ink(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeRelayOPtoInkWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_relay_ink_to_op(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeRelayInkToOPWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_relay_ink_to_base(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeRelayInkToBaseWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_relay_base_to_ink(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeRelayBaseToInkWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_bridge_gg_ethereum_to_ink(account: Account, module_settings) -> Tuple[bool, str]:
        async with BridgeGGEthereumToInkWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_claim_daily_gm(account: Account, module_settings) -> Tuple[bool, str]:
        async with ClaimDailyGMWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_buy_znc_domen_ink_network(account: Account, module_settings) -> Tuple[bool, str]:
        async with ZNSDomenWorker(account, module_settings) as module:
            return await module.run()

    @staticmethod
    async def process_mint_paragraf_nft(account: Account, module_settings) -> Tuple[bool, str]:
        async with MintParagraphNFTWorker(account, module_settings) as module:
            return await module.run()
