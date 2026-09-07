"""Block and Blockchain: proof-of-work mining, balances, and validation."""

import hashlib
import json
import time

from transaction import Transaction


class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        content = {
            "index": self.index,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


class Blockchain:
    difficulty = 4
    mining_reward = 6.25

    def __init__(self):
        self.chain = [Block(0, [], "0")]
        self.pending = []

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, tx: Transaction):
        if not tx.is_valid():
            raise ValueError("Invalid signature")
        if tx.sender != "NETWORK" and self.get_balance(tx.sender) < tx.amount:
            raise ValueError("Insufficient balance")
        self.pending.append(tx)

    def _mine(self, block: Block) -> str:
        target = "0" * self.difficulty
        while not block.hash.startswith(target):
            block.nonce += 1
            block.hash = block.compute_hash()
        return block.hash

    def mine_pending_transactions(self, miner_address: str) -> Block:
        self.pending.append(Transaction("NETWORK", None, miner_address, self.mining_reward))
        block = Block(self.last_block.index + 1, self.pending, self.last_block.hash)
        self._mine(block)
        self.chain.append(block)
        self.pending = []
        return block

    def get_balance(self, address: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def is_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current, prev = self.chain[i], self.chain[i - 1]
            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != prev.hash:
                return False
            if not all(tx.is_valid() for tx in current.transactions):
                return False
        return True
