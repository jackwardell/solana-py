"""Test get confirmed block."""

import solana.transaction as txlib
from solders.keypair import Keypair
from solders.signature import Signature
from solders.system_program import TransferParams, transfer


def test_verify_confirmed_block(stubbed_blockhash):
    """Test verifying signature in a confirmed block."""
    kp0, kp1, kp2, kp3 = (Keypair() for _ in range(4))
    # Create a couple signed transaction
    txn1 = txlib.Transaction(recent_blockhash=stubbed_blockhash).add(
        transfer(TransferParams(from_pubkey=kp0.pubkey(), to_pubkey=kp1.pubkey(), lamports=123))
    )
    txn1.sign(kp0)
    txn2 = txlib.Transaction(recent_blockhash=stubbed_blockhash).add(
        transfer(TransferParams(from_pubkey=kp2.pubkey(), to_pubkey=kp3.pubkey(), lamports=456))
    )
    txn2.sign(kp2)
    # Build confirmed_block with dummy data for blockhases and balances
    confirmed_block = {
        "blockhash": stubbed_blockhash,
        "previousBlockhash": stubbed_blockhash,
        "transactions": [
            {
                "transaction": txn1,
                "meta": {
                    "fee": 0,
                    "preBalances": [100000, 100000, 1, 1, 1],
                    "postBalances": [99877, 100123, 1, 1, 1],
                    "status": {"Ok": None},
                    "err": None,
                },
            },
            {
                "transaction": txn2,
                "meta": {
                    "fee": 0,
                    "preBalances": [100000, 100000, 1, 1, 1],
                    "postBalances": [99544, 100456, 1, 1, 1],
                    "status": {"Ok": None},
                    "err": None,
                },
            },
        ],
        "rewards": [],
    }
    # Verify signatures in confirmed_block
    assert all(tx_with_meta["transaction"].verify_signatures() for tx_with_meta in confirmed_block["transactions"])
    # Test block with bogus signature
    bogus_signature = Signature.default()
    bogus_txn1 = txlib.Transaction.populate(txn1.compile_message(), [bogus_signature])
    bad_confirmed_block = confirmed_block
    bad_confirmed_block["transactions"][0]["transaction"] = bogus_txn1
    assert not all(tx_with_meta["transaction"].verify_signatures() for tx_with_meta in confirmed_block["transactions"])
