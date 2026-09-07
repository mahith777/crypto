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

```bash
python3 demo.py
```

```bash
python3 -m unittest test_blockchain.py -v
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
