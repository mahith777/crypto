# Simple Blockchain Crypto

A tiny, readable cryptocurrency written in Python. It shows exactly how
coins are **created** (mining) and **transferred** (signed transactions)
on a blockchain, in under 150 lines of code.

## Files

| File | Purpose |
|---|---|
| `wallet.py` | Generates a public/private key pair; signs & verifies messages |
| `transaction.py` | A signed transfer of coins between two addresses |
| `blockchain.py` | Block + Blockchain: proof-of-work mining, balances, validation |
| `demo.py` | Runs a full example: Alice mines coins, sends some to Bob |
| `test_blockchain.py` | Unit tests |

## Setup

```bash
pip install -r requirements.txt
```

## Run
```
"""
crypto_blockchain.py
---------------------
A complete, single-file cryptocurrency demo: wallets, signed
transactions, mining (creating new coins), and blockchain validation.

Run with:
    python3 crypto_blockchain.py
"""

import hashlib
import binascii
import json
import time
import ecdsa


# ============================================================
# WALLET — generates a key pair, signs and verifies messages
# ============================================================
class Wallet:
    def __init__(self):
        self._private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
        self._public_key = self._private_key.get_verifying_key()

    @property
    def address(self):
        return hashlib.sha256(self._public_key.to_string()).hexdigest()[:40]

    @property
    def public_key_hex(self):
        return binascii.hexlify(self._public_key.to_string()).decode()

    def sign(self, message: str) -> str:
        return binascii.hexlify(self._private_key.sign(message.encode())).decode()

    @staticmethod
    def verify(public_key_hex: str, message: str, signature_hex: str) -> bool:
        try:
            key = ecdsa.VerifyingKey.from_string(binascii.unhexlify(public_key_hex), curve=ecdsa.SECP256k1)
            return key.verify(binascii.unhexlify(signature_hex), message.encode())
        except Exception:
            return False


# ============================================================
# TRANSACTION — a signed transfer of coins
# ============================================================
class Transaction:
    def __init__(self, sender, sender_public_key, recipient, amount):
        self.sender = sender
        self.sender_public_key = sender_public_key
        self.recipient = recipient
        self.amount = amount
        self.timestamp = time.time()
        self.signature = None

    def message(self) -> str:
        return f"{self.sender}{self.recipient}{self.amount}{self.timestamp}"

    def sign(self, wallet: Wallet):
        if wallet.address != self.sender:
            raise ValueError("Cannot sign a transaction for another wallet")
        self.signature = wallet.sign(self.message())

    def is_valid(self) -> bool:
        if self.sender == "NETWORK":
            return True
        if not self.signature:
            return False
        return Wallet.verify(self.sender_public_key, self.message(), self.signature)

    def to_dict(self):
        return {
            "sender": self.sender, "recipient": self.recipient,
            "amount": self.amount, "timestamp": self.timestamp,
            "signature": self.signature,
        }

    def __repr__(self):
        return f"{self.sender[:8]}... -> {self.recipient[:8]}... : {self.amount}"


# ============================================================
# BLOCK — a batch of transactions linked to the previous block
# ============================================================
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


# ============================================================
# BLOCKCHAIN — mining (creates coins), balances, validation
# ============================================================
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


# ============================================================
# DEMO — Alice mines coins, sends some to Bob
# ============================================================
if __name__ == "__main__":
    blockchain = Blockchain()
    alice, bob = Wallet(), Wallet()

    print(f"Alice: {alice.address}")
    print(f"Bob:   {bob.address}")

    # Alice mines a block and earns new coins (this is how coins are CREATED)
    blockchain.mine_pending_transactions(alice.address)
    print(f"\nAlice's balance after mining: {blockchain.get_balance(alice.address)}")

    # Alice sends 2.5 coins to Bob (this is how coins are TRANSFERRED)
    tx = Transaction(alice.address, alice.public_key_hex, bob.address, 2.5)
    tx.sign(alice)
    blockchain.add_transaction(tx)
    blockchain.mine_pending_transactions(alice.address)

    print(f"\nAfter the transfer:")
    print(f"Alice: {blockchain.get_balance(alice.address)}")
    print(f"Bob:   {blockchain.get_balance(bob.address)}")
    print(f"\nChain valid? {blockchain.is_valid()}")

    # Bonus: prove tampering gets caught
    blockchain.chain[-1].transactions[0].amount = 999
    print(f"Chain valid after tampering? {blockchain.is_valid()}")

```


## How it works

- **Creating coins:** mining searches for a `nonce` that makes a block's
  SHA-256 hash start with several zeros. Whoever finds it gets a reward
  paid from a special `"NETWORK"` sender.
- **Transferring coins:** sending money means signing a message with your
  private key. Anyone can check that signature with your public key,
  and the chain verifies your balance before accepting it.
- **Security:** every block stores the previous block's hash, so editing
  old data breaks the chain — caught by `is_valid()`.

## License

MIT — see [LICENSE](LICENSE).

## output 
<img width="756" height="303" alt="image" src="https://github.com/user-attachments/assets/08040811-d4e8-4667-8077-afcf1041ab07" />

## result 

Alice mined new coins and successfully sent 2.5 of them to Bob, with the blockchain confirming the transfer as valid. When a past transaction was secretly altered afterward, the blockchain immediately detected it and marked itself invalid.
