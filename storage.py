import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from crypto import CryptoManager


# ========== ДОБАВЛЕНО: определение исключения ==========
class SecureStorageError(Exception):
    """Исключение для ошибок хранилища"""
    pass


class SecureStorage:
    def __init__(self, master_password: str, filename: str = "vault.dat"):
        # Используем папку "Документы/PassKeeper"
        docs_path = Path.home() / "Documents" / "PassKeeper"
        
        # Создаем папку если её нет
        docs_path.mkdir(parents=True, exist_ok=True)
        
        # Полный путь к файлу
        self.filepath = docs_path / filename  # ← ИСПРАВЛЕНО: было self.filename, теперь self.filepath
        
        print(f"Данные будут здесь: {self.filepath}")
        
        self.master_password = master_password
        self.data = []
        self.crypto = CryptoManager()
        self._load()
    
    def _load(self) -> None:
        try:
            #читаем зашифрованный файл
            with open(self.filepath, 'rb') as f:  # ← ИСПРАВЛЕНО: было self.filename
                encrypted_data = f.read()
            if encrypted_data:
                #расшифровываем данные
                try:
                    json_str = self.crypto.decrypt(encrypted_data, self.master_password)
                    self.data = json.loads(json_str)
                except Exception as e:
                    #в случае неудачной расшифровки(неверный пароль)
                    raise SecureStorageError(
                        "Неверный мастер-пароль или файл поврежден"
                    ) from e
            else:
                #новое хранилище
                self.data = []
                
        except FileNotFoundError:
            #создаем новое хранилище
            self.data = []
            self._save()  #создаем файл
            print("Создано новое защищенное хранилище")
    
    def _save(self) -> None:
        try:
            #преобразуем данные в JSON строку
            json_str = json.dumps(self.data, ensure_ascii=False, indent=2)
            
            #шифруем данные
            encrypted_data = self.crypto.encrypt(json_str, self.master_password)
            
            #сохраняем в файл
            with open(self.filepath, 'wb') as f:  # ← ИСПРАВЛЕНО: было self.filename
                f.write(encrypted_data)
                
        except Exception as e:
            raise SecureStorageError(f"Ошибка сохранения данных: {e}") from e


#МЕТОДЫ РАБОТЫ С ДАННЫМИ
    def add_entry(self, service: str, login: str, password: str, notes: str = "") -> None:
        self.data.append({
            "service": service,
            "login": login,
            "password": password,
            "notes": notes
        })
        self._save()
    
    def get_all_entries(self) -> List[Dict]:
        return self.data.copy()  #возвращаем копию для безопасности
    
    def get_entry_count(self) -> int:
        return len(self.data)   #возвращает колво записей
    
    def find_entries(self, search_term: str) -> List[Dict]: #поисковик
        search_term = search_term.lower()
        return [
            entry for entry in self.data
            if search_term in entry['service'].lower() 
            or search_term in entry['login'].lower()
        ]
    
    def get_entry_by_index(self, index: int) -> Optional[Dict]: #возвращает запись по индексу
        if 0 <= index < len(self.data):
            return self.data[index].copy()
        return None
    
    def update_entry(self, index: int, **kwargs) -> bool: #обновляет существующую запись
        if 0 <= index < len(self.data):
            for key, value in kwargs.items():
                if key in self.data[index]:
                    self.data[index][key] = value
            self._save()
            return True
        return False
    
    def delete_entry(self, index: int) -> bool: #удаляет запись
        if 0 <= index < len(self.data):
            self.data.pop(index)
            self._save()
            return True
        return False
    
    def change_master_password(self, new_password: str) -> None: #изменяет мастер-пароль
        #сохраняем текущие данные
        current_data = self.data
        #меняем пароль
        self.master_password = new_password
        #пересохраняем данные с новым паролем
        self._save()
    
    def export_to_json(self, filename: str) -> None: #передаём в другой файлик для резервного копирования
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def import_from_json(self, filename: str) -> None: #импорт из файла
        with open(filename, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self._save()
