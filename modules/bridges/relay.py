from . import*

class BridgeRelayWorker:
    def __init__(self, client: Client):
        self.client = client

    async def bridge_from_op_to_ink(self):
        value, balance = await self.client.get_value_and_normalized_value()

        logger.info(
            f'{self.client.name} Sending {balance} ETH via the official bridge from the Optimism network to Ink'
        )

        address_contract: ChecksumAddress = AsyncWeb3.to_checksum_address(
            '0xa5f565650890fba1824ee0f21ebbbf660a179934'
        )

        try:
            tx_params = await self.client.prepare_transaction(value=value)
            tx_params['to'] = address_contract 
            await self.client.send_transaction(tx_params, need_hash=True)
        except Exception as error:
            logger.error(
                f'{self.client.name} Failed to send {balance} ETH from the Optimism network to Ink'
            )