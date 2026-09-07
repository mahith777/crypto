"""Demo: Alice mines coins, sends some to Bob, and the chain is validated."""

from wallet import Wallet
from blockchain import Blockchain
from transaction import Transaction

blockchain = Blockchain()
alice, bob = Wallet(), Wallet()

print(f"Alice: {alice.address}")
print(f"Bob:   {bob.address}")

# Alice mines a block and earns new coins
blockchain.mine_pending_transactions(alice.address)
print(f"\nAlice's balance after mining: {blockchain.get_balance(alice.address)}")

# Alice sends 2.5 coins to Bob
tx = Transaction(alice.address, alice.public_key_hex, bob.address, 2.5)
tx.sign(alice)
blockchain.add_transaction(tx)
blockchain.mine_pending_transactions(alice.address)

print(f"\nAfter the transfer:")
print(f"Alice: {blockchain.get_balance(alice.address)}")
print(f"Bob:   {blockchain.get_balance(bob.address)}")
print(f"\nChain valid? {blockchain.is_valid()}")
