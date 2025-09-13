import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import hashlib
from datetime import datetime


class AuthSystem:
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.users = self.load_users()

    def load_users(self):
        """Загрузка пользователей из файла"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, "r", encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_users(self):
        """Сохранение пользователей в файл"""
        with open(self.users_file, "w", encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password, email=None):
        """Регистрация нового пользователя"""
        if username in self.users:
            return False, "Пользователь уже существует"

        if len(password) < 4:
            return False, "Пароль должен содержать минимум 4 символа"

        self.users[username] = {
            'password_hash': self.hash_password(password),
            'email': email,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_login': None
        }
        self.save_users()
        return True, "Регистрация успешна"

    def login(self, username, password):
        """Авторизация пользователя"""
        if username not in self.users:
            return False, "Пользователь не найден"

        if self.users[username]['password_hash'] != self.hash_password(password):
            return False, "Неверный пароль"

        self.users[username]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_users()
        self.current_user = username
        return True, "Вход выполнен успешно"

    def logout(self):
        """Выход из системы"""
        self.current_user = None

    def get_current_user(self):
        """Получение текущего пользователя"""
        return self.current_user

    def change_password(self, username, old_password, new_password):
        """Смена пароля"""
        if not self.login(username, old_password)[0]:
            return False, "Неверный старый пароль"

        self.users[username]['password_hash'] = self.hash_password(new_password)
        self.save_users()
        return True, "Пароль изменен успешно"


class AuthWindow:
    def __init__(self, auth_system, on_success_callback):
        self.auth_system = auth_system
        self.on_success_callback = on_success_callback

        self.auth_window = tk.Toplevel()
        self.auth_window.title("Авторизация")
        self.auth_window.geometry("400x500")
        self.auth_window.resizable(False, False)

        # Обработка закрытия окна
        self.auth_window.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.setup_ui()

    def on_window_close(self):
        """Обработчик закрытия окна авторизации"""
        self.auth_window.destroy()

    def setup_ui(self):
        """Настройка интерфейса авторизации"""
        # Создаем Notebook для вкладок
        notebook = ttk.Notebook(self.auth_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Вкладка входа
        login_frame = ttk.Frame(notebook, padding=20)
        notebook.add(login_frame, text="Вход")

        # Вкладка регистрации
        register_frame = ttk.Frame(notebook, padding=20)
        notebook.add(register_frame, text="Регистрация")

        # Настройка вкладки входа
        self.setup_login_tab(login_frame)

        # Настройка вкладки регистрации
        self.setup_register_tab(register_frame)

    def setup_login_tab(self, frame):
        """Настройка вкладки входа"""
        ttk.Label(frame, text="Логин:", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.login_username = ttk.Entry(frame, font=("Arial", 11))
        self.login_username.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(frame, text="Пароль:", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.login_password = ttk.Entry(frame, show="*", font=("Arial", 11))
        self.login_password.pack(fill=tk.X, pady=(0, 20))

        login_btn = ttk.Button(frame, text="Войти", command=self.handle_login)
        login_btn.pack(fill=tk.X, pady=10)

        # Биндинг Enter для входа
        self.login_password.bind("<Return>", lambda e: self.handle_login())
        self.login_username.bind("<Return>", lambda e: self.login_password.focus())

    def setup_register_tab(self, frame):
        """Настройка вкладки регистрации"""
        ttk.Label(frame, text="Логин:", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.register_username = ttk.Entry(frame, font=("Arial", 11))
        self.register_username.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(frame, text="Пароль:", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.register_password = ttk.Entry(frame, show="*", font=("Arial", 11))
        self.register_password.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(frame, text="Email (необязательно):", font=("Arial", 11)).pack(anchor=tk.W, pady=(0, 5))
        self.register_email = ttk.Entry(frame, font=("Arial", 11))
        self.register_email.pack(fill=tk.X, pady=(0, 20))

        register_btn = ttk.Button(frame, text="Зарегистрироваться", command=self.handle_register)
        register_btn.pack(fill=tk.X, pady=10)

        # Биндинг Enter для регистрации
        self.register_password.bind("<Return>", lambda e: self.handle_register())
        self.register_email.bind("<Return>", lambda e: self.handle_register())

    def handle_login(self):
        """Обработчик входа"""
        username = self.login_username.get().strip()
        password = self.login_password.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        success, message = self.auth_system.login(username, password)
        if success:
            messagebox.showinfo("Успех", message)
            self.auth_window.destroy()
            self.on_success_callback()
        else:
            messagebox.showerror("Ошибка", message)

    def handle_register(self):
        """Обработчик регистрации"""
        username = self.register_username.get().strip()
        password = self.register_password.get()
        email = self.register_email.get().strip() or None

        if not username or not password:
            messagebox.showerror("Ошибка", "Заполните обязательные поля")
            return

        success, message = self.auth_system.register(username, password, email)
        if success:
            messagebox.showinfo("Успех", message)
            # Автоматически заполняем форму входа
            self.login_username.delete(0, tk.END)
            self.login_username.insert(0, username)
            self.login_password.focus()
        else:
            messagebox.showerror("Ошибка", message)
