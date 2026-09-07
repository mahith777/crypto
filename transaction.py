"""Transaction: a signed transfer of coins from one address to another."""

import time


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

    def sign(self, wallet):
        if wallet.address != self.sender:
            raise ValueError("Cannot sign a transaction for another wallet")
        self.signature = wallet.sign(self.message())

    def is_valid(self) -> bool:
        if self.sender == "NETWORK":
            return True
        if not self.signature:
            return False
        from wallet import Wallet
        return Wallet.verify(self.sender_public_key, self.message(), self.signature)

    def to_dict(self):
        return {
            "sender": self.sender, "recipient": self.recipient,
            "amount": self.amount, "timestamp": self.timestamp,
            "signature": self.signature,
        }

    def __repr__(self):
        return f"{self.sender[:8]}... -> {self.recipient[:8]}... : {self.amount}"
