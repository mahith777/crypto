"""Wallet: a private/public key pair used to sign and verify transactions."""

import hashlib
import binascii
import ecdsa


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
