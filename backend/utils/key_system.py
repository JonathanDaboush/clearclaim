from cryptography.hazmat.primitives.asymmetric import rsa as _rsa, padding as _padding  # type: ignore[import-untyped]
from cryptography.hazmat.primitives import hashes as _hashes, serialization as _serialization  # type: ignore[import-untyped]
from cryptography.hazmat.backends import default_backend as _default_backend  # type: ignore[import-untyped]
from typing import Any, Tuple, cast

rsa = cast(Any, _rsa)
padding = cast(Any, _padding)
hashes = cast(Any, _hashes)
serialization = cast(Any, _serialization)
default_backend = cast(Any, _default_backend)


class KeySystem:
    @staticmethod
    def generate_key_pair() -> Tuple[Any, Any]:
        """Generate a 2048-bit RSA key pair. Returns (private_key, public_key) objects."""
        private_key: Any = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        return private_key, private_key.public_key()

    @staticmethod
    def sign_data(data: bytes, private_key: Any) -> bytes:
        """Sign data with the given RSA private key. Returns the signature bytes."""
        return private_key.sign(
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

    @staticmethod
    def verify_signature(data: bytes, signature: bytes, public_key: Any) -> bool:
        """Return True if the signature is valid for the given data and public key."""
        try:
            public_key.verify(
                signature,
                data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False
