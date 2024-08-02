# Copyright © Aptos Foundation
# SPDX-License-Identifier: Apache-2.0

"""
This example depends on the MoonCoin.move module having already been published to the destination blockchain.

One method to do so is to use the CLI:
    * Acquire the Aptos CLI, see https://aptos.dev/cli-tools/aptos-cli/use-cli/install-aptos-cli
    * `python -m examples.your-coin ~/aptos-core/aptos-move/move-examples/moon_coin`.
    * Open another terminal and `aptos move compile --package-dir ~/aptos-core/aptos-move/move-examples/moon_coin --save-metadata --named-addresses MoonCoin=<Alice address from above step>`.
    * Return to the first terminal and press enter.
"""

import asyncio
import os
import sys

from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.aptos_cli_wrapper import AptosCLIWrapper
from aptos_sdk.async_client import FaucetClient, RestClient
from aptos_sdk.bcs import Serializer
from aptos_sdk.package_publisher import PackagePublisher
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)
from aptos_sdk.type_tag import StructTag, TypeTag

from .common import FAUCET_URL, NODE_URL

MY_LOCAL_ACCOUNT_MINT_TOKENS = 1000000
MY_WEB_ACCOUNT_GET_TOKENS = 1000000

class CoinClient(RestClient):
    async def register_coin(self, coin_address: AccountAddress, sender: Account) -> str:
        """Register the receiver account to receive transfers for the new coin."""

        payload = EntryFunction.natural(
            "0x1::managed_coin",
            "register",
            [TypeTag(StructTag.from_str(f"{coin_address}::stable_coin1::StableCoin1"))],
            [],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            sender, TransactionPayload(payload)
        )
        return await self.submit_bcs_transaction(signed_transaction)

    async def mint_coin(
        self, minter: Account, receiver_address: AccountAddress, amount: int
    ) -> str:
        """Mints the newly created coin to a specified receiver address."""

        payload = EntryFunction.natural(
            "0x1::managed_coin",
            "mint",
            [TypeTag(StructTag.from_str(f"{minter.address()}::stable_coin1::StableCoin1"))],
            [
                TransactionArgument(receiver_address, Serializer.struct),
                TransactionArgument(amount, Serializer.u64),
            ],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            minter, TransactionPayload(payload)
        )
        return await self.submit_bcs_transaction(signed_transaction)

    async def get_balance(
        self,
        coin_address: AccountAddress,
        account_address: AccountAddress,
    ) -> str:
        """Returns the coin balance of the given account"""

        balance = await self.account_resource(
            account_address,
            f"0x1::coin::CoinStore<{coin_address}::stable_coin1::StableCoin1>",
        )
        return balance["data"]["coin"]["value"]


async def main(moon_coin_path: str):

    my_local_account_private_key = os.getenv('MY_LOCAL_ACCOUNT_PRIVATE_KEY')
    my_web_account_address = os.getenv('MY_WEB_ACCOUNT_ADDRESS')

    if my_local_account_private_key is None or my_web_account_address is None:
        print("Please set the MY_LOCAL_ACCOUNT_PRIVATE_KEY and MY_WEB_ACCOUNT_ADDRESS environment variables.")
        return

    my_local_account = Account.load_key(my_local_account_private_key)
    my_web_account_adderss = AccountAddress.from_str(my_web_account_address)

    print("\n=== Addresses ===")
    print(f"My local account: {my_local_account.address()}")
    print(f"My web account: {my_web_account_adderss}")

    rest_client = CoinClient(NODE_URL)
    faucet_client = FaucetClient(FAUCET_URL, rest_client)

    my_local_account_fund = faucet_client.fund_account(my_local_account.address(), 20_000_000)
    my_web_account_fund = faucet_client.fund_account(my_web_account_adderss, 20_000_000_000)
    await asyncio.gather(*[my_local_account_fund, my_web_account_fund])

    if AptosCLIWrapper.does_cli_exist():
        AptosCLIWrapper.compile_package(moon_coin_path, {"StableCoin1": my_local_account.address()})
    else:
        input("\nUpdate the module with My local account's address, compile, and press enter.")
    print("\nCompiled StableCoin1 module.")

    # :!:>publish
    module_path = os.path.join(
        moon_coin_path, "build", "Examples", "bytecode_modules", "stable_coin1.mv"
    )
    with open(module_path, "rb") as f:
        module = f.read()

    metadata_path = os.path.join(
        moon_coin_path, "build", "Examples", "package-metadata.bcs"
    )
    with open(metadata_path, "rb") as f:
        metadata = f.read()

    print("\nPublishing StableCoin1 package.")
    package_publisher = PackagePublisher(rest_client)
    txn_hash = await package_publisher.publish_package(my_local_account, metadata, [module])
    await rest_client.wait_for_transaction(txn_hash)
    # <:!:publish
    print("Published StableCoin1 package.")

    txn_hash = await rest_client.register_coin(my_local_account.address(), my_local_account)
    await rest_client.wait_for_transaction(txn_hash)

    print("my_local_account mints some of the new coin.")
    txn_hash = await rest_client.mint_coin(my_local_account, my_local_account.address(), MY_LOCAL_ACCOUNT_MINT_TOKENS)
    await rest_client.wait_for_transaction(txn_hash)


    try:
        maybe_balance = await rest_client.get_balance(my_local_account.address(), my_local_account.address())
    except Exception:
        maybe_balance = None
    print(f"my_local_account's updated StableCoin1 balance: {maybe_balance}")


    print("my_local_account transfers some of the new coin to my web account.")

    txn_hash = await rest_client.transfer_coins(
            my_local_account, my_web_account_adderss, f"{my_local_account.address()}::stable_coin1::StableCoin1", MY_WEB_ACCOUNT_GET_TOKENS
        )
    await rest_client.wait_for_transaction(txn_hash)


    balance = await rest_client.get_balance(my_local_account.address(), my_local_account.address())
    print(f"my_local_account's updated StableCoin1 balance: {balance}")
    balance = await rest_client.get_balance(my_local_account.address(), my_web_account_adderss)
    print(f"My web account's updated StableCoin1 balance: {balance}")


if __name__ == "__main__":
    assert (
        len(sys.argv) == 2
    ), "Expecting an argument that points to the moon_coin directory."

    asyncio.run(main(sys.argv[1]))
