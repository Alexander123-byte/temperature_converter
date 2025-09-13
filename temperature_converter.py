import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from auth import AuthSystem, AuthWindow


class TemperatureConverter:

    @staticmethod
    def c_to_f(celsius):
        """Цельсий → Фаренгейт"""
        if celsius < -273.15:
            raise ValueError("Температура ниже абсолютного нуля!")
        return (celsius * 9 / 5) + 32

    @staticmethod
    def f_to_c(fahrenheit):
        """Фаренгейт → Цельсий"""
        if fahrenheit < -459.67:
            raise ValueError("Температура ниже абсолютного нуля!")
        return (fahrenheit - 32) * 5 / 9

    @staticmethod
    def c_to_k(celsius):
        """Цельсий → Кельвин"""
        if celsius < -273.15:
            raise ValueError("Температура ниже абсолютного нуля!")
        return celsius + 273.15

    @staticmethod
    def k_to_c(kelvin):
        """Кельвин → Цельсий"""
        if kelvin < 0:
            raise ValueError("Температура ниже абсолютного нуля!")
        return kelvin - 273.15

    @staticmethod
    def f_to_k(fahrenheit):
        """Фаренгейт → Кельвин"""
        return TemperatureConverter.c_to_k(TemperatureConverter.f_to_c(fahrenheit))

    @staticmethod
    def k_to_f(kelvin):
        """Кельвин → Фаренгейт"""
        return TemperatureConverter.c_to_f(TemperatureConverter.k_to_c(kelvin))

    def __init__(self, root):
        self.root = root
        self.root.title("Умный конвертер температур")
        self.root.geometry("500x500")

        # Инициализация системы авторизации
        self.auth_system = AuthSystem()

        # Показываем окно авторизации
        self.show_auth_window()

        # История конвертаций
        self.history = []
        self.load_history()

        # Переменные
        self.mode = tk.StringVar(value='c_to_f')
        self.input_var = tk.StringVar()
        self.valid_input = tk.BooleanVar(value=True)  # Добавлено

        # Регистрируем функцию валидации
        self.validate_cmd = root.register(self.validate_input)

        # Создание интерфейса
        self.create_widgets()

    def show_auth_window(self):
        """Показать окно авторизации"""
        # Скрываем главное окно пока не авторизуемся
        self.root.withdraw()

        # Создаем окно авторизации
        auth_window = AuthWindow(
            self.auth_system,
            on_success_callback=self.on_auth_success
        )

        # Ждем закрытия окна авторизации
        self.root.wait_window(auth_window.auth_window)

        # Проверяем, был ли успешный вход
        if not self.auth_system.get_current_user():
            # Если пользователь не авторизовался, закрываем приложение
            self.root.destroy()

    def on_auth_success(self):
        """Вызывается после успешной авторизации"""
        try:
            # Показываем главное окно
            self.root.deiconify()

            # Загружаем историю для текущего пользователя
            self.history = []
            self.load_history()

            # Переменные
            self.input_var = tk.StringVar()
            self.valid_input = tk.BooleanVar(value=True)
            self.from_unit = tk.StringVar(value="Цельсий")
            self.to_unit = tk.StringVar(value="Фаренгейт")

            # Регистрируем функцию валидации
            self.validate_cmd = self.root.register(self.validate_input)

            # Создание интерфейса
            self.create_widgets()

            # Добавляем меню пользователя
            self.create_user_menu()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании интерфейса: {str(e)}")

    def create_user_menu(self):
        """Создание меню пользователя"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        user_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=f"👤 {self.auth_system.get_current_user()}", menu=user_menu)
        user_menu.add_command(label="Сменить пароль", command=self.change_password)
        user_menu.add_separator()
        user_menu.add_command(label="Выйти", command=self.logout)

    def change_password(self):
        """Смена пароля"""
        pass

    def logout(self):
        """Выход из системы"""
        self.auth_system.logout()
        # Очищаем интерфейс
        for widget in self.root.winfo_children():
            widget.destroy()
        # Показываем окно авторизации снова
        self.show_auth_window()

    def create_widgets(self):
        # Основное окно - конвертер
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = tk.Label(
            main_frame,
            text="Конвертер температур",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Фрейм для выбора конвертации
        conversion_frame = ttk.LabelFrame(main_frame, text="Выберите конвертацию")
        conversion_frame.pack(fill=tk.X, pady=10)

        # Выпадающие списки
        input_frame = ttk.Frame(conversion_frame)
        input_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_frame, text="Из:").pack(side=tk.LEFT, padx=(0, 10))

        self.from_unit = ttk.Combobox(
            input_frame,
            values=["Цельсий", "Фаренгейт", "Кельвин"],
            state="readonly",
            width=15
        )
        self.from_unit.set("Цельсий")
        self.from_unit.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Label(input_frame, text="в:").pack(side=tk.LEFT, padx=(0, 10))

        self.to_unit = ttk.Combobox(
            input_frame,
            values=["Фаренгейт", "Кельвин", "Цельсий"],
            state="readonly",
            width=15
        )
        self.to_unit.set("Фаренгейт")
        self.to_unit.pack(side=tk.LEFT)

        # ДОБАВЛЯЕМ ПРИВЯЗКУ СОБЫТИЙ ПОСЛЕ СОЗДАНИЯ КОМБОБОКСОВ
        self.from_unit.bind("<<ComboboxSelected>>", lambda e: self.on_unit_change())
        self.to_unit.bind("<<ComboboxSelected>>", lambda e: self.on_unit_change())

        # Поле ввода
        input_label_frame = ttk.LabelFrame(main_frame)
        input_label_frame.pack(fill=tk.X, pady=10)

        ttk.Label(input_label_frame, text="Введите температуру:", font=("Arial", 10)).pack(anchor=tk.W)

        self.entry = ttk.Entry(
            main_frame,
            textvariable=self.input_var,
            validate="key",
            validatecommand=(self.validate_cmd, "%P"),
            font=("Arial", 12)
        )
        self.entry.pack(fill=tk.X, pady=(0, 10))
        self.entry.focus_set()

        # Биндинги для поля ввода
        self.entry.bind("<Return>", lambda e: self.convert())

        # Подсказка под полем ввода
        self.validation_label = ttk.Label(
            main_frame,
            text="",
            foreground="red",
            font=("Arial", 9)
        )
        self.validation_label.pack(anchor=tk.W)

        # Следим за изменениями валидности
        self.valid_input.trace_add("write", self.update_validation_status)

        # Кнопка конвертации
        convert_btn = ttk.Button(
            main_frame,
            text="Конвертировать",
            command=self.convert,
            style="Accent.TButton"
        )
        convert_btn.pack(pady=15)

        # Результат
        result_frame = tk.Frame(main_frame)
        result_frame.pack(fill=tk.X, pady=10)

        ttk.Label(result_frame, text="Результат:", font=("Arial", 11, "bold")).pack(anchor=tk.W)

        self.result_label = ttk.Label(
            result_frame,
            text="—",
            font=("Arial", 14, "bold"),
            foreground="#2c3e50"
        )
        self.result_label.pack(anchor=tk.W, pady=(5, 0))

        # Кнопка открытия истории
        history_btn = tk.Button(
            main_frame,
            text="📋 Показать историю",
            command=self.open_history_window,
            font=("Arial", 11, "bold"),
            bg="#2E7D32",  # Темно-зеленый фон
            fg="white",  # Белый текст
            padx=30,  # Горизонтальные отступы
            pady=12,  # Вертикальные отступы
            relief="raised",
            bd=2,
            cursor="hand2"
        )
        history_btn.pack(pady=20)

        # Эффект при наведении
        history_btn.bind("<Enter>", lambda e: history_btn.config(bg="#388E3C"))
        history_btn.bind("<Leave>", lambda e: history_btn.config(bg="#2E7D32"))

        # Настраиваем стили
        self.setup_styles()

    def setup_styles(self):
        """Настройка стилей для красивого интерфейса"""
        style = ttk.Style()

        # Стиль для акцентной кнопки
        style.configure("Accent.TButton", font=("Arial", 11, "bold"))

        # Стиль для кнопки истории - ВЫДЕЛЕННЫЙ
        style.configure("History.TButton",
                        font=("Arial", 10, "bold"),
                        background="#4CAF50",  # Зеленый фон
                        foreground="white",  # Белый текст
                        padding=(10, 5))

        # Стиль для выпадающих списков
        style.configure("TCombobox", padding=5)

    def update_validation_status(self, *args):
        """Обновляет подсказку и визуальное отображение валидности"""
        current_text = self.input_var.get()

        if not self.valid_input.get() and current_text not in ("", "-"):
            self.validation_label.config(text="Введите число (например: 23.5 или -10)")
            # Красный фон для ошибки, черный текст для читаемости
            self.entry.config(background="#ffcccc", foreground="black")
        else:
            self.validation_label.config(text="")
            # Стандартные цвета
            self.entry.config(background="white", foreground="black")

    def validate_input(self, new_text):
        """Проверяет корректность ввода в реальном времени"""
        if new_text == "" or new_text == "-":
            self.valid_input.set(True)
            return True

        # Разрешаем отрицательные числа
        if new_text.startswith("-"):
            number_part = new_text[1:]
            if number_part == "" or number_part == ".":
                self.valid_input.set(True)
                return True
            try:
                float(number_part)
                self.valid_input.set(True)
                return True
            except ValueError:
                self.valid_input.set(False)
                return False

        try:
            float(new_text)
            self.valid_input.set(True)
            return True
        except ValueError:
            self.valid_input.set(False)
            return False

    def show_validation_error(self):
        """Визуальное оповещение об ошибке (мигание)"""
        original_bg = self.entry.cget("background")
        original_fg = self.entry.cget("foreground")

        # Мигание красным фоном, но сохраняем черный текст
        self.entry.config(background="#ffcccc", foreground="black")
        self.entry.after(300, lambda: self.entry.config(
            background=original_bg,
            foreground=original_fg
        ))

    def validate_paste(self, text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def open_history_window(self):
        # Создаем новое окно
        history_window = tk.Toplevel(self.root)
        history_window.title("История конвертации")
        history_window.geometry("500x300+200+200")

        history_tree = ttk.Treeview(
            history_window,
            columns=("time", "input", "result"),
            show="headings",
            height=10
        )

        # Настройка колонок
        history_tree.heading("time", text="Время")
        history_tree.heading("input", text="Ввод")
        history_tree.heading("result", text="Результат")

        history_tree.column("time", width=120)
        history_tree.column("input", width=150)
        history_tree.column("result", width=150)

        # Скроллбар
        scrollbar = ttk.Scrollbar(history_window, orient=tk.VERTICAL, command=history_tree.yview)
        history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        history_tree.pack(fill=tk.BOTH, expand=True)

        # Заполнение данными
        for item in self.history:
            history_tree.insert("", tk.END, values=item)

        # Кнопки управления историей
        btn_frame = ttk.Frame(history_window)
        btn_frame.pack(pady=10)

        ttk.Button(
            btn_frame, text="Очистить историю",
            command=lambda: [self.clear_history(), history_window.destroy()]
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame, text="Экспорт в CSV",
            command=self.export_history  # Исправлено: убрано лишнее
        ).pack(side=tk.LEFT, padx=10)

        ttk.Button(
            btn_frame, text="Закрыть",
            command=history_window.destroy
        ).pack(side=tk.RIGHT, padx=10)

        # Запрещение создания нескольких окон
        history_window.focus_set()
        history_window.grab_set()

    def convert(self, event=None):
        if not self.valid_input.get():
            messagebox.showerror("Ошибка", "Некорректный ввод. Введите число.")
            return

        try:
            temp = float(self.input_var.get())
            from_unit = self.from_unit.get()
            to_unit = self.to_unit.get()

            # Проверяем, что выбраны разные единицы
            if from_unit == to_unit:
                messagebox.showerror("Ошибка", "Выберите разные единицы измерения")
                return

            # Определяем тип конвертации (используем первые буквы)
            from_letter = from_unit[0].lower()  # "ц" -> "c", "ф" -> "f", "к" -> "k"
            to_letter = to_unit[0].lower()

            # Русские буквы в английские для методов
            russian_to_english = {"ц": "c", "ф": "f", "к": "k"}
            from_letter = russian_to_english.get(from_letter, from_letter)
            to_letter = russian_to_english.get(to_letter, to_letter)

            conversion_type = f"{from_letter}_to_{to_letter}"

            if conversion_type == "c_to_f":
                result = TemperatureConverter.c_to_f(temp)
                self.result_label.config(text=f"{temp:.2f}°C = {result:.2f}°F")
                self.add_to_history(f"{temp:.2f}°C", f"{result:.2f}°F")

            elif conversion_type == "c_to_k":
                result = TemperatureConverter.c_to_k(temp)
                self.result_label.config(text=f"{temp:.2f}°C = {result:.2f}K")
                self.add_to_history(f"{temp:.2f}°C", f"{result:.2f}K")

            elif conversion_type == "f_to_c":
                result = TemperatureConverter.f_to_c(temp)
                self.result_label.config(text=f"{temp:.2f}°F = {result:.2f}°C")
                self.add_to_history(f"{temp:.2f}°F", f"{result:.2f}°C")

            elif conversion_type == "f_to_k":
                result = TemperatureConverter.f_to_k(temp)
                self.result_label.config(text=f"{temp:.2f}°F = {result:.2f}K")
                self.add_to_history(f"{temp:.2f}°F", f"{result:.2f}K")

            elif conversion_type == "k_to_c":
                result = TemperatureConverter.k_to_c(temp)
                self.result_label.config(text=f"{temp:.2f}K = {result:.2f}°C")
                self.add_to_history(f"{temp:.2f}K", f"{result:.2f}°C")

            elif conversion_type == "k_to_f":
                result = TemperatureConverter.k_to_f(temp)
                self.result_label.config(text=f"{temp:.2f}K = {result:.2f}°F")
                self.add_to_history(f"{temp:.2f}K", f"{result:.2f}°F")

            else:
                messagebox.showerror("Ошибка", f"Неизвестный тип конвертации: {conversion_type}")

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def on_unit_change(self, event=None):
        """Обработчик изменения выбора единиц измерения"""
        from_unit = self.from_unit.get()
        to_unit = self.to_unit.get()

        if from_unit and to_unit and from_unit == to_unit:
            self.result_label.config(text="—", foreground="red")
        else:
            self.result_label.config(text="—", foreground="#2c3e50")

    def add_to_history(self, input_temp, result_temp):
        from_unit = self.from_unit.get()[:1].upper()
        to_unit = self.to_unit.get()[:1].upper()

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.insert(0, (timestamp, input_temp, result_temp))

        if len(self.history) > 15:
            self.history = self.history[:15]

        self.save_history()

    def export_history(self):
        import csv
        from tkinter import filedialog

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            with open(file_path, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Time", "Input", "Result"])
                writer.writerows(self.history)

    def clear_history(self):
        self.history = []
        self.save_history()

    def save_history(self):
        """Сохранение истории для текущего пользователя"""
        username = self.auth_system.get_current_user()
        history_file = f"history_{username}.json"

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def load_history(self):
        """Загрузка истории для текущего пользователя"""
        username = self.auth_system.get_current_user()
        history_file = f"history_{username}.json"

        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except:
                self.history = []


if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureConverter(root)
    root.mainloop()
