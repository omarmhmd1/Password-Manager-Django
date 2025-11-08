from cryptography.fernet import Fernet

# Generate a new key
key = Fernet.generate_key()

# Print the key to use it later
print(key)
