import tkinter as tk
from tkinter import ttk, messagebox
from storage import SecureStorage, SecureStorageError

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Защищенный менеджер паролей")
        self.root.geometry("850x550")
        self.root.minsize(800, 500)
        
        #цветовая схема
        self.colors = {
            'bg': '#f0f0f0',
            'header': '#2c3e50',      # темно-синий
            'success': '#27ae60',      # зеленый
            'warning': '#f39c12',       # оранжевый
            'danger': '#c0392b',        # красный
            'info': '#2980b9',          # синий
            'white': '#ffffff',
            'text': '#333333'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        #сначала запрашиваем мастер-пароль
        self.master_password = self._ask_master_password()
        if not self.master_password:
            self.root.destroy()
            return
        
        #подключаемся к хранилищу
        self._init_storage()
        #создаем интерфейс
        self._setup_ui()
        #загружаем записи
        self._refresh_list()
    
    def _ask_master_password(self): #иалоговое окно для основного пароля
        dialog = tk.Toplevel(self.root)
        dialog.title("Вход в систему")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        #центрируем окно
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        #заголовок
        tk.Label(
            dialog,
            text="Мастер-пароль",
            font=('Arial', 14, 'bold')
        ).pack(pady=15)
        
        tk.Label(
            dialog,
            text="Введите пароль для доступа к хранилищу:",
            font=('Arial', 10)
        ).pack(pady=5)
        
        #поле ввода пароля
        password_var = tk.StringVar()
        password_entry = tk.Entry(
            dialog,
            textvariable=password_var,
            show="•",
            width=30,
            font=('Arial', 11)
        )
        password_entry.pack(pady=10)
        password_entry.focus()
        
        result = []
        
        def on_ok():
            if password_var.get():
                result.append(password_var.get())
                dialog.destroy()
            else:
                messagebox.showwarning("Внимание", "Введите пароль!")
        
        def on_cancel():
            dialog.destroy()
        
        #привязываем Enter
        password_entry.bind('<Return>', lambda e: on_ok())
        
        #кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)
        
        tk.Button(
            btn_frame,
            text="Войти",
            command=on_ok,
            bg=self.colors['success'],
            fg='white',
            width=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Выход",
            command=on_cancel,
            bg=self.colors['danger'],
            fg='white',
            width=10,
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        #ждем закрытия
        self.root.wait_window(dialog)
        
        return result[0] if result else None
    
    def _init_storage(self):
        try:
            self.storage = SecureStorage(self.master_password, "vault.dat")
        except SecureStorageError as e:
            messagebox.showerror(
                "Ошибка доступа",
                f"Не удалось открыть хранилище:\n{e}\n\n"
                "Проверьте мастер-пароль!"
            )
            self.root.destroy()
            return

#ИНТЕРФЕЙС
   
    def _setup_ui(self):
        
        #верхняя панель
        header = tk.Frame(self.root, bg=self.colors['header'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        title_label = tk.Label(
            header,
            text="Защищенное хранилище паролей",
            bg=self.colors['header'],
            fg='white',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=15)
        
        #основная часть
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        #кнопки слева
        left = tk.Frame(main, bg=self.colors['white'], width=180)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)
        
        #заголовок панели
        tk.Label(
            left,
            text="Управление",
            bg=self.colors['white'],
            font=('Arial', 12, 'bold'),
            fg=self.colors['header']
        ).pack(pady=15)
        
        #кнопки действий
        buttons = [
            ("Добавить запись", self._add_entry, self.colors['success']),
            ("Редактировать", self._edit_entry, self.colors['warning']),
            ("Удалить", self._delete_entry, self.colors['danger']),
            ("Обновить", self._refresh_list, self.colors['info']),
            ("Статистика", self._show_stats, self.colors['header'])
        ]
        
        for text, cmd, color in buttons:
            btn = tk.Button(
                left,
                text=text,
                command=cmd,
                bg=color,
                fg='white',
                font=('Arial', 10),
                relief=tk.FLAT,
                cursor='hand2',
                height=2
            )
            btn.pack(fill=tk.X, padx=10, pady=3)
        
        #информация о хранилище
        info_frame = tk.Frame(left, bg=self.colors['white'])
        info_frame.pack(fill=tk.X, padx=10, pady=(20, 10))
        
        tk.Label(
            info_frame,
            text="Хранилище",
            bg=self.colors['white'],
            font=('Arial', 10, 'bold')
        ).pack(anchor=tk.W)
        
        self.info_label = tk.Label(
            info_frame,
            text="Записей: 0",
            bg=self.colors['white'],
            font=('Arial', 9),
            justify=tk.LEFT
        )
        self.info_label.pack(anchor=tk.W, pady=2)
        
        #правая панель
        right = tk.Frame(main, bg=self.colors['white'])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        #поисковик
        search_frame = tk.Frame(right, bg=self.colors['white'])
        search_frame.pack(fill=tk.X, padx=15, pady=15)
        
        tk.Label(
            search_frame,
            text="Поиск:",
            bg=self.colors['white'],
            font=('Arial', 10)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._refresh_list())
        
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=30
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(
            search_frame,
            text="Очистить",
            command=self._clear_search,
            font=('Arial', 8)
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        #таблица
        table_frame = tk.Frame(right, bg=self.colors['white'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        #скроллбар
        scrollbar_y = tk.Scrollbar(table_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        #таблица
        columns = ('Сервис', 'Логин', 'Пароль', 'Заметки')
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            selectmode='browse'
        )
        
        # настройка колонок
        column_widths = [150, 200, 120, 200]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        #связываем скроллбары
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        #двойной клик для копирования
        self.tree.bind('<Double-Button-1>', lambda e: self._copy_password())
        
        #нижняя панель
        status = tk.Frame(self.root, bg=self.colors['header'], height=30)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        
        self.status_label = tk.Label(
            status,
            text="Готов к работе",
            bg=self.colors['header'],
            fg='white',
            font=('Arial', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def _refresh_list(self): #обновление всей таблицы
        #очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        #получаем данные
        search = self.search_var.get().strip()
        if search:
            entries = self.storage.find_entries(search)
        else:
            entries = self.storage.get_all_entries()
        
        #заполняем таблицу
        for entry in entries:
            self.tree.insert('', 'end', values=(
                entry['service'],
                entry['login'],
                '•' * 8,  #скрываем пароль
                entry.get('notes', '')
            ))
        
        #обновляем информацию
        total = self.storage.get_entry_count()
        self.info_label.config(text=f"Записей: {total}")
        self.status_label.config(
            text=f"Показано записей: {len(entries)} из {total}"
        )
    
    def _clear_search(self):
        """Очищает поиск"""
        self.search_var.set("")
        self.search_entry.focus()
    
    def _get_selected_entry(self):
        """Возвращает выбранную запись"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Внимание",
                "Выберите запись из списка!"
            )
            return None
        
        #получаем данные из таблицы
        item = self.tree.item(selection[0])
        service = item['values'][0]
        
        #ищем в хранилище
        for i, entry in enumerate(self.storage.get_all_entries()):
            if entry['service'] == service:
                return i, entry
        
        return None
    
    def _add_entry(self):
        """Диалог добавления записи"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Новая запись")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрируем
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Поля ввода
        fields = [
            ("Сервис:", 'service'),
            ("Логин:", 'login'),
            ("Пароль:", 'password'),
            ("Заметки:", 'notes')
        ]
        
        entries = {}
        
        for i, (label, field) in enumerate(fields):
            tk.Label(
                dialog,
                text=label,
                font=('Arial', 10)
            ).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            
            entry = tk.Entry(
                dialog,
                width=30,
                show='*' if field == 'password' else ''
            )
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry
        
        def save():
            if not entries['service'].get() or not entries['login'].get() or not entries['password'].get():
                messagebox.showerror("Ошибка", "Сервис, логин и пароль обязательны!")
                return
            
            self.storage.add_entry(
                entries['service'].get(),
                entries['login'].get(),
                entries['password'].get(),
                entries['notes'].get()
            )
            self._refresh_list()
            dialog.destroy()
            self.status_label.config(
                text=f"Добавлена запись: {entries['service'].get()}"
            )
        
        #ещё кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        
        tk.Button(
            btn_frame,
            text="Сохранить",
            command=save,
            bg=self.colors['success'],
            fg='white',
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy,
            bg=self.colors['danger'],
            fg='white',
            width=10
        ).pack(side=tk.LEFT)
    
    def _edit_entry(self):
        """Диалог редактирования"""
        selected = self._get_selected_entry()
        if not selected:
            return
        
        index, entry = selected
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        #центрируем
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        #поля с текущими значениями
        fields = [
            ("Сервис:", 'service', entry['service']),
            ("Логин:", 'login', entry['login']),
            ("Пароль:", 'password', entry['password']),
            ("Заметки:", 'notes', entry.get('notes', ''))
        ]
        
        entries = {}
        
        for i, (label, field, value) in enumerate(fields):
            tk.Label(
                dialog,
                text=label,
                font=('Arial', 10)
            ).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            
            entry_widget = tk.Entry(dialog, width=30)
            entry_widget.insert(0, value)
            entry_widget.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry_widget
        
        def save():
            self.storage.update_entry(
                index,
                service=entries['service'].get(),
                login=entries['login'].get(),
                password=entries['password'].get(),
                notes=entries['notes'].get()
            )
            self._refresh_list()
            dialog.destroy()
            self.status_label.config(
                text=f"Обновлена запись: {entries['service'].get()}"
            )
        
        #кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=15)
        
        tk.Button(
            btn_frame,
            text="Сохранить",
            command=save,
            bg=self.colors['success'],
            fg='white',
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Отмена",
            command=dialog.destroy,
            bg=self.colors['danger'],
            fg='white',
            width=10
        ).pack(side=tk.LEFT)
    
    def _delete_entry(self): #удаление записи
        selected = self._get_selected_entry()
        if not selected:
            return
        
        index, entry = selected
        
        if messagebox.askyesno(
            "Подтверждение",
            f"Удалить запись для '{entry['service']}'?\n\n"
            "Это действие нельзя отменить!"
        ):
            self.storage.delete_entry(index)
            self._refresh_list()
            self.status_label.config(
                text=f"Удалена запись: {entry['service']}"
            )
    
    def _copy_password(self):#копирование пароля в буфер обмена
        selected = self._get_selected_entry()
        if not selected:
            return
        
        index, entry = selected
        
        #копируем в буфер обмена
        self.root.clipboard_clear()
        self.root.clipboard_append(entry['password'])
        
        self.status_label.config(
            text=f"Пароль для {entry['service']} скопирован"
        )
    
    def _show_stats(self):#показывает статистику
        total = self.storage.get_entry_count()
        #считаем уникальные сервисы
        services = set(entry['service'] for entry in self.storage.get_all_entries())
        
        stats_text = (
            f"Статистика хранилища\n\n"
            f"Всего записей: {total}\n"
            f"Уникальных сервисов: {len(services)}\n"
            f"Файл: vault.dat\n"
            f"Статус: Зашифровано"
        )
        
        messagebox.showinfo("Статистика", stats_text)
