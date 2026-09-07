"""Run with: python3 -m unittest test_blockchain.py -v"""

import unittest
from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction


class TestBlockchain(unittest.TestCase):
    def setUp(self):
        self.bc = Blockchain()
        self.alice = Wallet()
        self.bob = Wallet()

    def test_mining_rewards_miner(self):
        self.bc.mine_pending_transactions(self.alice.address)
        self.assertEqual(self.bc.get_balance(self.alice.address), self.bc.mining_reward)

    def test_transfer_updates_balances(self):
        self.bc.mine_pending_transactions(self.alice.address)
        tx = Transaction(self.alice.address, self.alice.public_key_hex, self.bob.address, 2)
        tx.sign(self.alice)
        self.bc.add_transaction(tx)
        self.bc.mine_pending_transactions(self.alice.address)
        self.assertEqual(self.bc.get_balance(self.bob.address), 2)

    def test_overspend_rejected(self):
        tx = Transaction(self.alice.address, self.alice.public_key_hex, self.bob.address, 100)
        tx.sign(self.alice)
        with self.assertRaises(ValueError):
            self.bc.add_transaction(tx)

    def test_forged_signature_rejected(self):
        tx = Transaction(self.alice.address, self.alice.public_key_hex, self.bob.address, 1)
        tx.signature = "00" * 64
        with self.assertRaises(ValueError):
            self.bc.add_transaction(tx)

    def test_tampering_detected(self):
        self.bc.mine_pending_transactions(self.alice.address)
        self.bc.chain[-1].transactions[0].amount = 999
        self.assertFalse(self.bc.is_valid())


if __name__ == "__main__":
    unittest.main()
