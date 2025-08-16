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
            raise ValueError("Ниже абсолютного нуля!")
        return celsius + 273.15

    @staticmethod
    def k_to_c(kelvin):
        if kelvin < 0:
            raise ValueError("Ниже абсолютного нуля!")
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

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        # Фрейм для ввода
        input_frame = ttk.Frame(self.root, padding="10")
        input_frame.pack(fill=tk.X)

        # Переключатель режимов
        mode_frame = ttk.LabelFrame(input_frame, text="Режим конвертации")
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
        ttk.Label(input_frame, text="Введите температуру:").pack(anchor=tk.W)
        entry = ttk.Entry(input_frame, textvariable=self.input_var)
        entry.pack(fill=tk.X, pady=5)
        entry.bind("<Return>", lambda e: self.convert())

        # Кнопка конвертации
        ttk.Button(
            input_frame, text="Конвертировать",
            command=self.convert
        ).pack(pady=10)

        # Результат
        self.result_label = ttk.Label(
            input_frame, text="",
            font=("Arial", 12, "bold")
        )
        self.result_label.pack()

        # История
        history_frame = ttk.LabelFrame(self.root, text="История конвертаций", padding="10")
        history_frame.pack(fill=tk.BOTH, pady=5, expand=True, padx=10)

        self.history_tree = ttk.Treeview(
            history_frame,
            columns=("time", "input", "result"),
            show="headings",
            height=5
        )

        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("input", text="Ввод")
        self.history_tree.heading("result", text="Результат")

        self.history_tree.column("time", width=80)
        self.history_tree.column("input", width=100)
        self.history_tree.column("result", width=150)

        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопка очистки истории
        ttk.Button(
            history_frame, text="Очистить историю",
            command=self.clear_history
        ).pack(pady=5)

        self.update_history_display()

    def convert(self):
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

        if len(self.history) > 10:  # Ограничиваем историю 10 последними записями
            self.history = self.history[:10]

        self.save_history()
        self.update_history_display()

    def update_history_display(self):
        self.history_tree.delete(*self.history_tree.get_children())
        for item in self.history:
            self.history_tree.insert("", tk.END, values=item)

    def clear_history(self):
        self.history = []
        self.save_history()
        self.update_history_display()

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
