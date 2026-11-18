# from flask import Flask, render_template

# app = Flask(__name__)


# @app.route("/")
# def home():

#     original_message = "Hello Skodex"

#     stored_message = original_message

#     key_status = "Azure Key Vault Key NOT Used"

#     return render_template(
#         "index.html",
#         original_message=original_message,
#         stored_message=stored_message,
#         key_status=key_status
#     )


# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, render_template

from azure.identity import DefaultAzureCredential

from azure.keyvault.keys import KeyClient

from azure.keyvault.keys.crypto import (
    CryptographyClient,
    EncryptionAlgorithm
)

import os
import base64


app = Flask(__name__)


VAULT_NAME = os.environ.get("KEY_VAULT_NAME", "")

VAULT_URL = f"https://{VAULT_NAME}.vault.azure.net"


credential = DefaultAzureCredential()


@app.route("/")
def home():

    original_message = "Hello Skodex"

    encrypted_message = "Not Available"

    decrypted_message = "Not Available"

    key_status = "Not Connected"

    try:

        key_client = KeyClient(
            vault_url=VAULT_URL,
            credential=credential
        )

        key = key_client.get_key(
            "skodex-encryption-key"
        )

        crypto_client = CryptographyClient(
            key,
            credential=credential
        )

        encrypted = crypto_client.encrypt(
            EncryptionAlgorithm.rsa_oaep_256,
            original_message.encode("utf-8")
        )

        encrypted_message = base64.b64encode(
            encrypted.ciphertext
        ).decode("utf-8")

        decrypted = crypto_client.decrypt(
            EncryptionAlgorithm.rsa_oaep_256,
            encrypted.ciphertext
        )

        decrypted_message = decrypted.plaintext.decode(
            "utf-8"
        )

        key_status = "Azure Key Vault Key Connected"

    except Exception:

        key_status = "Azure Key Vault Key Connection Failed"

    return render_template(
        "index.html",
        original_message=original_message,
        encrypted_message=encrypted_message,
        decrypted_message=decrypted_message,
        key_status=key_status
    )


if __name__ == "__main__":
    app.run(debug=True)