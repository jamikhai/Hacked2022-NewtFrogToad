import argparse
import string
import random
import json
import time
import base58
from solana.keypair import Keypair
from solana.rpc.api import Client
from metaplex.metadata import get_metadata
from cryptography.fernet import Fernet
from api.metaplex_api import MetaplexAPI

def await_full_confirmation(client, txn, max_timeout=60):
    if txn is None:
        return
    elapsed = 0
    while elapsed < max_timeout:
        sleep_time = 1
        time.sleep(sleep_time)
        elapsed += sleep_time
        resp = client.get_confirmed_transaction(txn)
        while 'result' not in resp:
            resp = client.get_confirmed_transaction(txn)
        if resp["result"]:
            print(f"Took {elapsed} seconds to confirm transaction {txn}")
            break

def test(url_json,api_endpoint="https://api.devnet.solana.com/"):
    keypair = Keypair()
    cfg = {
        "PRIVATE_KEY": "",
        "PUBLIC_KEY": "EMBaZYKcC3uoDTMg5WLVc2mmTttTuZ89ZomN825QXoJW",
        "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
    }
    api = MetaplexAPI(cfg)
    client = Client(api_endpoint)
    resp = {}
    while 'result' not in resp:
        resp = client.request_airdrop(cfg["PUBLIC_KEY"], int(1e9))
    print("Request Airdrop:", resp)
    txn = resp['result']
    await_full_confirmation(client, txn)
    letters = string.ascii_uppercase
    name = ''.join([random.choice(letters) for i in range(32)])
    symbol = ''.join([random.choice(letters) for i in range(10)])
    print("Name:", name)
    print("Symbol:", symbol)
    # added seller_basis_fee_points
    deploy_response = json.loads(api.deploy(api_endpoint, name, symbol, 0))
    print("Deploy:", deploy_response)
    assert deploy_response["status"] == 200
    contract = deploy_response.get("contract")
    print(get_metadata(client, contract))
    wallet = json.loads(api.wallet())
    address1 = cfg["PUBLIC_KEY"]
    encrypted_pk1 = api.cipher.encrypt(bytes(wallet.get('private_key')))
    topup_response = json.loads(api.topup(api_endpoint, address1))
    print(f"Topup {address1}:", topup_response)
    assert topup_response["status"] == 200
    mint_to_response = json.loads(api.mint(api_endpoint, contract, address1, url_json))
    print("Mint:", mint_to_response)
    # await_confirmation(client, mint_to_response['tx'])
    assert mint_to_response["status"] == 200
    print(get_metadata(client, contract))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url_json", default=None)
    args = ap.parse_args()
    test(args.url_json)

