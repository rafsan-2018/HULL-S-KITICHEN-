import json
from cypto_utils import encrypt, decrypt

# Encrypt a password
json_data = encrypt()

# Pretty-print the encrypted data using json.dumps with the indent parameter
formatted_json_data = json.dumps(json.loads(json_data), indent=4)
print("\n\n============== Results ===============")
print("\n\nEncrypted data (formatted):")
print("--------------------------------------\n")
print(formatted_json_data)

# Decrypt the password
try:
    decrypted = decrypt(json_data)
    print("\n\n\nDecrypted data: ")
    print("--------------------------------------\n")
    print(decrypted)
    print("\n--------------------------------------\n")
    print("\n\n")
except ValueError as e:
    print(str(e))
    print("\n\n")

    # https://youtu.be/XVqdulkhn_o?si=RIxJJCDMVeLZfdWp
