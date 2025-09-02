import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os


class TemperatureConverter:

    @staticmethod
    def c_to_f(celsius):
        if celsius < -273.15:
            raise ValueError("Температура ниже абсолютного нуля!")
        return (celsius * 9 / 5) + 32

    @staticmethod
    def f_to_c(fahrenheit):
        if fahrenheit < -459.67:
            raise ValueError("Температура ниже абсолютного нуля!")
        return (fahrenheit - 32) * 5 / 9

    @staticmethod
    def c_to_k(celsius):
        if celsius < -273.15:
            raise ValueError("Температура ниже абсолютного нуля!")
        return celsius + 273.15

    @staticmethod
    def k_to_c(kelvin):
        if kelvin < 0:
            raise ValueError("Температура ниже абсолютного нуля!")
        return kelvin - 273.15

    def __init__(self, root):
        self.root = root
        self.root.title("Умный конвертер температур")
        self.root.geometry("450x450")

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

    def create_widgets(self):
        # Основное окно - конвертер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Переключатель режимов
        mode_frame = ttk.LabelFrame(main_frame, text="Режим конвертации")
        mode_frame.pack(fill=tk.X, pady=5)

        modes = [
            ("Цельсий → Фаренгейт", "c_to_f"),
            ("Фаренгейт → Цельсий", "f_to_c"),
            ("Цельсий → Кельвины", "c_to_k"),
            ("Кельвины → Цельсий", "k_to_c")
        ]

        for text, mode in modes:
            ttk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.mode,
                value=mode
            ).pack(anchor=tk.W, pady=2)

        # Поле ввода
        ttk.Label(main_frame, text="Введите температуру:").pack(anchor=tk.W)

        # Создаем стиль для валидации - ИСПРАВЛЕНО
        style = ttk.Style()
        style.configure("Invalid.TEntry", foreground="red", background="#ffeeee")

        # Поле ввода с валидацией
        self.entry = ttk.Entry(
            main_frame,
            textvariable=self.input_var,
            validate="key",
            validatecommand=(self.validate_cmd, "%P")
        )
        self.entry.pack(fill=tk.X, pady=5)

        # Биндинги для поля ввода
        self.entry.bind("<Return>", lambda e: self.convert())
        self.entry.bind("<<Paste>>", lambda e: self.on_paste())

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
        ttk.Button(
            main_frame, text="Конвертировать",
            command=self.convert
        ).pack(pady=10)

        # Результат
        self.result_label = ttk.Label(
            main_frame, text="",
            font=("Arial", 12, "bold")
        )
        self.result_label.pack()

        # Кнопка открытия истории
        ttk.Button(
            main_frame, text="Показать историю (CTRL+H)",
            command=self.open_history_window
        ).pack(pady=20)

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
            mode = self.mode.get()

            if mode == "c_to_f":
                result = TemperatureConverter.c_to_f(temp)
                self.result_label.config(text=f"{temp}°C = {result:.2f}°F")
                self.add_to_history(f"{temp}°C", f"{result:.2f}°F")

            elif mode == "f_to_c":
                result = TemperatureConverter.f_to_c(temp)
                self.result_label.config(text=f"{temp}°F = {result:.2f}°C")
                self.add_to_history(f"{temp}°F", f"{result:.2f}°C")

            elif mode == "c_to_k":
                result = TemperatureConverter.c_to_k(temp)
                self.result_label.config(text=f"{temp}°C = {result:.2f}K")
                self.add_to_history(f"{temp}°C", f"{result:.2f}K")

            elif mode == "k_to_c":
                result = TemperatureConverter.k_to_c(temp)
                self.result_label.config(text=f"{temp}K = {result:.2f}°C")
                self.add_to_history(f"{temp}K", f"{result:.2f}°C")

        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def add_to_history(self, input_temp, result_temp):
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
        with open("converter_history.json", "w") as f:
            json.dump(self.history, f)

    def load_history(self):
        if os.path.exists("converter_history.json"):
            try:
                with open("converter_history.json", "r") as f:
                    self.history = json.load(f)
            except:
                self.history = []


if __name__ == "__main__":
    root = tk.Tk()
    app = TemperatureConverter(root)
    root.mainloop()
