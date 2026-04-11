import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CryptoManager:
    def __init__(self):
        self.salt = b'password_manager_salt_2024'
        
    def _derive_key(self, master_password: str) -> bytes:
        #преобразуем пароль в байты
        password_bytes = master_password.encode('utf-8')
        #используем PBKDF2 для усиления пароля
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        #генерация ключа
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, data: str, master_password: str) -> bytes:
        key = self._derive_key(master_password)
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data.encode('utf-8'))
        return encrypted_data
    
    def decrypt(self, encrypted_data: bytes, master_password: str) -> str:
        key = self._derive_key(master_password)
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
