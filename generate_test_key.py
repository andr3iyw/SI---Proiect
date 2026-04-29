import os

os.makedirs("keys", exist_ok=True)

key_256 = os.urandom(32)

with open("keys/aes_main.key", "wb") as f:
    f.write(key_256)
    
print("Cheia de test AES-256 a fost generata in: keys/aes_main.key")