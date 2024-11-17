import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def encrypt(plain_text: str) -> str:
    """
    Encrypt a plain text and return a JSON string containing the encrypted plain text and associated data.

    Args:
        plain text (str): The plain text to encrypt.

    Returns:
        str: A JSON string containing the encrypted plain text, nonce, header, tag, and key (all base64-encoded).
    """
    # Convert the plain text to bytes
    text_bytes = plain_text.encode("utf-8")

    # Create a random key and initialize the AES cipher in GCM mode
    key = get_random_bytes(16)  # Generate a random 16-byte key
    cipher = AES.new(key, AES.MODE_GCM)  # Create AES cipher in GCM mode

    # Optional header (could be useful for authenticated encryption)
    header = b"header"

    # Update the cipher with the header
    cipher.update(header)

    # Encrypt the plain text and get the ciphertext and tag
    ciphertext, tag = cipher.encrypt_and_digest(text_bytes)

    # Encode the nonce, header, ciphertext, and tag using base64
    json_keys = ["nonce", "header", "ciphertext", "tag", "key"]
    json_values = [
        b64encode(x).decode("utf-8") for x in (cipher.nonce, header, ciphertext, tag)
    ]
    # Encode the key and add it to the JSON values
    json_values.append(b64encode(key).decode("utf-8"))

    # Create a JSON object with the encoded values
    result = json.dumps(dict(zip(json_keys, json_values)))

    return result


def decrypt(json_data: str) -> str:
    """
    Decrypt a password from an encrypted JSON data string.

    Args:
        json_data (str): The base64-encoded JSON string containing the encrypted data and associated components.

    Returns:
        str: The decrypted password as a string.

    Raises:
        ValueError: If the decryption process fails due to incorrect data, key, or tampering.
    """
    # Load the JSON data
    data = json.loads(json_data)

    # Decode the base64-encoded strings to bytes
    nonce = b64decode(data["nonce"])
    header = b64decode(data["header"])
    ciphertext = b64decode(data["ciphertext"])
    tag = b64decode(data["tag"])
    key = b64decode(data["key"])

    # Initialize the AES cipher in GCM mode using the key and nonce
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    # Update the cipher with the header (AAD)
    cipher.update(header)

    # Decrypt the data and validate the authentication tag
    try:
        decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        # Convert decrypted data from bytes to a string
        decrypted_password = decrypted_data.decode("utf-8")
        return decrypted_password
    except ValueError as e:
        # Handle decryption failure
        raise ValueError(
            "Decryption failed: the data or key may be incorrect, or the data may have been tampered with."
        ) from e
