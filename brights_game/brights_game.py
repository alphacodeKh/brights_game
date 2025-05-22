import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
from PIL import Image, ImageTk, ImageDraw
import os

class BrightBitsGame:
    def create_bulb_image(self, is_on, size=64):
        """Створює зображення лампочки (увімкненої або вимкненої)"""
        # Створюємо базове зображення
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Кольори
        bulb_color = "#FFC125" if is_on else "#E0E0E0"  # жовтий для включеної, сірий для вимкненої
        outline_color = "#333333"  # темно-сірий контур
        
        # Малюємо колбу лампочки (коло)
        bulb_radius = size // 2 - 8
        draw.ellipse((size//2 - bulb_radius, 4, size//2 + bulb_radius, 4 + 2*bulb_radius), 
                    fill=bulb_color, outline=outline_color, width=2)
        
        # Малюємо основу лампочки (трапеція)
        base_width = bulb_radius * 1.2
        base_height = size // 4
        base_top = 4 + 2*bulb_radius
        base_bottom = base_top + base_height
        
        # Координати трапеції
        base_coords = [
            (size//2 - base_width//2, base_top),  # верхній лівий
            (size//2 + base_width//2, base_top),  # верхній правий
            (size//2 + base_width//3, base_bottom),  # нижній правий
            (size//2 - base_width//3, base_bottom)   # нижній лівий
        ]
        draw.polygon(base_coords, fill="#A0A0A0", outline=outline_color, width=2)
        
        # Повертаємо зображення у форматі для Tkinter
        return ImageTk.PhotoImage(image)
    
    def toggle_bulb(self, index):
        """Переключає стан лампочки"""
        self.bulb_values[index] = 1 - self.bulb_values[index]  # Інвертуємо значення (0->1, 1->0)
        self.update_bulb(index)
        
        # Якщо ми в режимі decimal_to_binary, оновлюємо поле введення
        if self.game_mode == "decimal_to_binary":
            binary_str = ''.join(str(bit) for bit in self.bulb_values)
            self.binary_entry.delete(0, tk.END)
            self.binary_entry.insert(0, binary_str.lstrip('0') or '0')  # Видаляємо провідні нулі, але залишаємо хоча б один нуль
    
    def update_bulb(self, index):
        """Оновлює візуальне відображення лампочки"""
        bulb_label, bit_var, _ = self.bulbs[index]
        if self.bulb_values[index] == 1:
            bulb_label.config(image=self.bulb_on_image)
            bit_var.set("1")
        else:
            bulb_label.config(image=self.bulb_off_image)
            bit_var.set("0")
    
    def __init__(self, root):
        self.root = root
        self.root.title("BrightBits: Вивчайте двійкову систему весело та легко!")
        self.root.geometry("800x700")  # Збільшуємо висоту для лампочок
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Встановлення іконки програми (якщо файл існує)
        try:
            self.root.iconbitmap("brightbits_icon.ico")
        except:
            pass
        
        # Змінні
        self.current_level = 1
        self.score = 0
        self.time_left = 60
        self.timer_running = False
        self.current_decimal = 0
        self.current_binary = ""
        self.game_mode = "decimal_to_binary"  # або "binary_to_decimal"
        
        # Створення основних кадрів
        self.create_menu_frame()
        self.create_game_frame()
        self.create_tutorial_frame()
        self.create_leaderboard_frame()
        
        # За промовчанням показуємо меню
        self.show_menu()
        
    def create_menu_frame(self):
        self.menu_frame = tk.Frame(self.root, bg="#f0f0f0")
        
        # Заголовок
        title_label = tk.Label(self.menu_frame, text="BrightBits", font=("Helvetica", 48, "bold"), bg="#f0f0f0", fg="#3498db")
        title_label.pack(pady=(50, 10))
        
        subtitle_label = tk.Label(self.menu_frame, text="Вивчайте двійкову систему весело та легко!", font=("Helvetica", 16), bg="#f0f0f0", fg="#2c3e50")
        subtitle_label.pack(pady=(0, 50))
        
        # Кнопки меню
        button_style = {"font": ("Helvetica", 14), "bg": "#3498db", "fg": "white", "width": 20, "height": 2, "cursor": "hand2", "borderwidth": 0}
        
        play_button = tk.Button(self.menu_frame, text="Грати", command=self.setup_game, **button_style)
        play_button.pack(pady=10)
        
        tutorial_button = tk.Button(self.menu_frame, text="Навчання", command=self.show_tutorial, **button_style)
        tutorial_button.pack(pady=10)
        
        leaderboard_button = tk.Button(self.menu_frame, text="Таблиця лідерів", command=self.show_leaderboard, **button_style)
        leaderboard_button.pack(pady=10)
        
        exit_button = tk.Button(self.menu_frame, text="Вихід", command=self.root.quit, **button_style)
        exit_button.pack(pady=10)
        
        # Версія гри
        version_label = tk.Label(self.menu_frame, text="v1.0", font=("Helvetica", 8), bg="#f0f0f0", fg="#7f8c8d")
        version_label.pack(side=tk.BOTTOM, pady=10)
        
    def create_game_frame(self):
        self.game_frame = tk.Frame(self.root, bg="#f0f0f0")
        
        # Верхня інформаційна панель
        info_frame = tk.Frame(self.game_frame, bg="#3498db")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.level_label = tk.Label(info_frame, text="Рівень: 1", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white")
        self.level_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.score_label = tk.Label(info_frame, text="Очок: 0", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white")
        self.score_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.timer_label = tk.Label(info_frame, text="Час: 60", font=("Helvetica", 12, "bold"), bg="#3498db", fg="white")
        self.timer_label.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Основна частина гри
        self.task_label = tk.Label(self.game_frame, text="Переведіть число в двійкову систему:", font=("Helvetica", 14), bg="#f0f0f0")
        self.task_label.pack(pady=(30, 10))
        
        self.number_label = tk.Label(self.game_frame, text="", font=("Helvetica", 48, "bold"), bg="#f0f0f0", fg="#2c3e50")
        self.number_label.pack(pady=10)
        
        # Фрейм для лампочок
        self.bulbs_frame = tk.Frame(self.game_frame, bg="#f0f0f0")
        self.bulbs_frame.pack(pady=20)
        
        # Створюємо зображення для лампочок (ввімкнених та вимкнених)
        self.bulb_on_image = self.create_bulb_image(True)
        self.bulb_off_image = self.create_bulb_image(False)
        
        # Створюємо 8 лампочок (за замовчуванням вимкнених)
        self.bulbs = []
        self.bulb_values = [0] * 8  # стани лампочок (0 - вимкнена, 1 - включена)
        
        for i in range(8):
            bulb_frame = tk.Frame(self.bulbs_frame, bg="#f0f0f0")
            bulb_frame.grid(row=0, column=i, padx=5)
            
            # Значення розряду (128, 64, 32, ...)
            power_value = 2**(7-i)
            value_label = tk.Label(bulb_frame, text=str(power_value), font=("Helvetica", 10), bg="#f0f0f0")
            value_label.pack()
            
            # Зображення лампочки
            bulb_label = tk.Label(bulb_frame, image=self.bulb_off_image, bg="#f0f0f0")
            bulb_label.pack(pady=5)
            
            # Стан (0 або 1)
            bit_var = tk.StringVar(value="0")
            bit_label = tk.Label(bulb_frame, textvariable=bit_var, font=("Helvetica", 16, "bold"), bg="#f0f0f0")
            bit_label.pack()
            
            # Кнопка для перемикання
            toggle_button = tk.Button(bulb_frame, text="Натиснути", 
                                     command=lambda idx=i: self.toggle_bulb(idx))
            toggle_button.pack(pady=5)
            
            self.bulbs.append((bulb_label, bit_var, toggle_button))
        
        # Поле для введення десяткової відповіді
        self.binary_input_frame = tk.Frame(self.game_frame, bg="#f0f0f0")
        self.binary_input_frame.pack(pady=20)
        
        self.answer_label = tk.Label(self.binary_input_frame, text="Введіть число:", font=("Helvetica", 14), bg="#f0f0f0")
        self.answer_label.pack(side=tk.LEFT, padx=5)
        
        self.binary_entry = tk.Entry(self.binary_input_frame, font=("Helvetica", 24), width=12, justify='center')
        self.binary_entry.pack(side=tk.LEFT, padx=5)
        self.binary_entry.bind("<Return>", lambda event: self.check_answer())
        
        # Кнопка перевірки відповіді
        self.check_button = tk.Button(self.game_frame, text="Перевірити", font=("Helvetica", 14), 
                                     bg="#2ecc71", fg="white", width=15, height=1, 
                                     cursor="hand2", borderwidth=0, command=self.check_answer)
        self.check_button.pack(pady=10)
        
        # Кнопка повернення в меню
        self.back_button = tk.Button(self.game_frame, text="В меню", font=("Helvetica", 12), 
                                    bg="#95a5a6", fg="white", width=10, 
                                    cursor="hand2", borderwidth=0, command=self.show_menu)
        self.back_button.pack(side=tk.BOTTOM, pady=20)
        
        # Підказка
        self.hint_label = tk.Label(self.game_frame, text="", font=("Helvetica", 10), bg="#f0f0f0", fg="#7f8c8d")
        self.hint_label.pack(side=tk.BOTTOM, pady=(0, 10))
    
    def create_tutorial_frame(self):
        self.tutorial_frame = tk.Frame(self.root, bg="#f0f0f0")
        
        tutorial_title = tk.Label(self.tutorial_frame, text="Як грати в BrightBits", font=("Helvetica", 24, "bold"), bg="#f0f0f0", fg="#3498db")
        tutorial_title.pack(pady=(20, 30))
        
        # Створюємо віджет з прокручуванням для вмісту
        tutorial_canvas = tk.Canvas(self.tutorial_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tutorial_frame, orient="vertical", command=tutorial_canvas.yview)
        tutorial_content = tk.Frame(tutorial_canvas, bg="#f0f0f0")
        
        tutorial_canvas.configure(yscrollcommand=scrollbar.set)
        tutorial_canvas.pack(side="left", fill="both", expand=True, padx=(20, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 20))
        
        tutorial_canvas.create_window((0, 0), window=tutorial_content, anchor="nw")
        tutorial_content.bind("<Configure>", lambda e: tutorial_canvas.configure(scrollregion=tutorial_canvas.bbox("all")))
        
        # Вміст навчання
        tutorial_texts = [
            ("Що таке двійкова система числення?", 
            "Двійкова система - це система числення з основою 2, яка використовує лише дві цифри: 0 і 1. " 
            "Комп'ютери використовують двійкову систему для зберігання та обробки всієї інформації."),
            
            ("Як переводити числа з десяткової системи в двійкову?", 
            "Щоб перевести число з десяткової системи в двійкову, потрібно послідовно ділити його на 2 і "
            "записувати залишки від розподілу у зворотному порядку.\n\n" 
            "Приклад: Перекладемо число 13 у двійкову систему\n" 
            "13 ÷ 2 = 6 (залишок 1)\n" 
            "6 ÷ 2 = 3 (залишок 0)\n" 
            "3 ÷ 2 = 1 (залишок 1)\n" 
            "1 ÷ 2 = 0 (залишок 1)\n" 
            "Результат (читаємо знизу вгору): 1101"),
            
            ("Як переводити числа з двійкової системи до десяткової?", 
            "Щоб перевести число з двійкової системи в десяткову, потрібно помножити кожну цифру на 2 ступені," 
            "відповідної позиції цієї цифри (справа ліворуч, починаючи з нуля), і скласти результати.\n\n" 
            "Приклад: Перекладемо число 1101 у десяткову систему\n" 
            "1×2^3 + 1×2^2 + 0×2^1 + 1×2^0 = 8 + 4 + 0 + 1 = 13"),
            
            ("Як грати в BrightBits?", 
            "У грі вам потрібно переводити числа з десяткової системи в двійкову або навпаки." 
            "За кожну правильну відповідь ви отримуєте очки. Чим вищий рівень, тим складніше завдання та " 
            "Більше очок за правильні відповіді. Але будьте уважні - у вас обмежений час!")
        ]
        
        for title, text in tutorial_texts:
            section_title = tk.Label(tutorial_content, text=title, font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
            section_title.pack(anchor="w", pady=(20, 5))
            
            section_text = tk.Label(tutorial_content, text=text, font=("Helvetica", 12), bg="#f0f0f0", fg="#2c3e50", 
                                  justify="left", wraplength=700)
            section_text.pack(anchor="w", pady=(0, 10))
        
        # Таблиця для візуалізації ступенів двійки
        powers_title = tk.Label(tutorial_content, text="Таблиця ступенів двійки", font=("Helvetica", 16, "bold"), bg="#f0f0f0", fg="#2c3e50")
        powers_title.pack(anchor="w", pady=(20, 10))
        
        powers_frame = tk.Frame(tutorial_content, bg="#f0f0f0")
        powers_frame.pack(fill="x", pady=(0, 20))
        
        for i in range(8):
            power_label = tk.Label(powers_frame, text=f"2^{7-i}", font=("Helvetica", 12), bg="#e8f6fe", fg="#2c3e50", width=5, padx=5, pady=5)
            power_label.grid(row=0, column=i, padx=2, pady=2)
            
            value_label = tk.Label(powers_frame, text=str(2**(7-i)), font=("Helvetica", 12), bg="#f0f0f0", fg="#2c3e50", width=5, padx=5, pady=5)
            value_label.grid(row=1, column=i, padx=2, pady=2)
        
        # Кнопка повернення
        back_button = tk.Button(tutorial_content, text="Повернутись до меню", font=("Helvetica", 14), 
                               bg="#3498db", fg="white", width=20, height=1, 
                               cursor="hand2", borderwidth=0, command=self.show_menu)
        back_button.pack(pady=30)
        
    def create_leaderboard_frame(self):
        self.leaderboard_frame = tk.Frame(self.root, bg="#f0f0f0")
        
        leaderboard_title = tk.Label(self.leaderboard_frame, text="Таблиця лідерів", font=("Helvetica", 24, "bold"), bg="#f0f0f0", fg="#3498db")
        leaderboard_title.pack(pady=(20, 30))
        
        # Створюємо кадр для таблиці
        table_frame = tk.Frame(self.leaderboard_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        table_frame.pack(padx=50, pady=10, fill="both")
        
        # Заголовки стовпців
        header_bg = "#3498db"
        header_fg = "white"
        tk.Label(table_frame, text="Місце", font=("Helvetica", 12, "bold"), bg=header_bg, fg=header_fg, width=10, padx=10, pady=5).grid(row=0, column=0)
        tk.Label(table_frame, text="Ім'я", font=("Helvetica", 12, "bold"), bg=header_bg, fg=header_fg, width=20, padx=10, pady=5).grid(row=0, column=1)
        tk.Label(table_frame, text="Очок", font=("Helvetica", 12, "bold"), bg=header_bg, fg=header_fg, width=10, padx=10, pady=5).grid(row=0, column=2)
        
        # Завантаження результатів із файлу (або демо-дані)
        self.leaderboard_data = self.load_leaderboard()
        
        # Відображення даних таблиці
        for i, (name, score) in enumerate(self.leaderboard_data[:10], 1):
            row_bg = "#f0f9ff" if i % 2 == 0 else "#ffffff"
            tk.Label(table_frame, text=str(i), font=("Helvetica", 12), bg=row_bg, fg="#2c3e50", padx=10, pady=5).grid(row=i, column=0, sticky="nsew")
            tk.Label(table_frame, text=name, font=("Helvetica", 12), bg=row_bg, fg="#2c3e50", padx=10, pady=5).grid(row=i, column=1, sticky="nsew")
            tk.Label(table_frame, text=str(score), font=("Helvetica", 12), bg=row_bg, fg="#2c3e50", padx=10, pady=5).grid(row=i, column=2, sticky="nsew")
        
        # Кнопка повернення
        back_button = tk.Button(self.leaderboard_frame, text="Повернутись до меню", font=("Helvetica", 14), 
                               bg="#3498db", fg="white", width=20, height=1, 
                               cursor="hand2", borderwidth=0, command=self.show_menu)
        back_button.pack(pady=30)
    
    def load_leaderboard(self):
        # У реальному додатку тут буде завантаження з файлу 
        # Для демонстрації використовуємо тестові дані
        return [
            ("Саша", 1250),
            ("Маша", 980),
            ("Петя", 820),
            ("Даша", 750),
            ("Коля", 620),
            ("Оля", 580),
            ("Вася", 450),
            ("Катя", 320),
            ("Дима", 270),
            ("Аня", 150)
        ]
    
    def save_score(self, name, score):
        # У реальному додатку тут буде збережено файл
        self.leaderboard_data.append((name, score))
        self.leaderboard_data.sort(key=lambda x: x[1], reverse=True)
    
    def show_menu(self):
        # Зупиняємо таймер, якщо він запущений
        self.timer_running = False
        
        # Приховуємо всі кадри
        self.game_frame.pack_forget()
        self.tutorial_frame.pack_forget()
        self.leaderboard_frame.pack_forget()
        
        # Показуємо меню
        self.menu_frame.pack(fill="both", expand=True)
    
    def show_tutorial(self):
        # Приховуємо всі кадри
        self.menu_frame.pack_forget()
        self.game_frame.pack_forget()
        self.leaderboard_frame.pack_forget()
        
        # Показуємо навчання
        self.tutorial_frame.pack(fill="both", expand=True)
    
    def show_leaderboard(self):
        # Приховуємо всі кадри
        self.menu_frame.pack_forget()
        self.game_frame.pack_forget()
        self.tutorial_frame.pack_forget()
        
        # Показуємо таблицю лідерів
        self.leaderboard_frame.pack(fill="both", expand=True)
    
    def setup_game(self):
        # Налаштовуємо нову гру
        self.current_level = 1
        self.score = 0
        self.time_left = 60
        
        # Оновлюємо мітки
        self.level_label.config(text=f"Рівень: {self.current_level}")
        self.score_label.config(text=f"Очок: {self.score}")
        self.timer_label.config(text=f"Час: {self.time_left}")
        
        # Генеруємо перше завдання
        self.generate_task()
        
        # Приховуємо меню та показуємо гру
        self.menu_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        
        # Запускаємо таймер
        self.timer_running = True
        self.update_timer()
        
        # Встановлюємо фокус у полі введення
        self.binary_entry.delete(0, tk.END)
        self.binary_entry.focus()
    
    def generate_task(self):
        # Вибираємо режим гри в залежності від рівня
        if self.current_level % 3 == 0:  # кожен третій рівень змінюємо режим
            self.game_mode = "binary_to_decimal" if self.game_mode == "decimal_to_binary" else "decimal_to_binary"
        
        if self.game_mode == "decimal_to_binary":
            # Генеруємо десяткове число (складність залежить від рівня)
            max_value = min(2**(3 + self.current_level) - 1, 255)  # максимум 8 біт
            self.current_decimal = random.randint(1, max_value)
            self.current_binary = bin(self.current_decimal)[2:]  # прибираємо префікс '0b'
            
            # Оновлюємо інтерфейс
            self.task_label.config(text="Переведіть число в двійкову систему:")
            self.number_label.config(text=str(self.current_decimal))
            self.hint_label.config(text="Увімкніть відповідні лампочки")
            self.answer_label.config(text="Двійкове число:")
            
            # Вимикаємо всі лампочки
            for i in range(8):
                self.bulb_values[i] = 0
                self.update_bulb(i)
            
        else:  # binary_to_decimal
            # Генеруємо двійкове число (складність залежить від рівня)
            bits = min(3 + self.current_level, 8)  # максимум 8 біт
            self.current_binary = bin(random.randint(1, 2**bits - 1))[2:]  # прибираємо префікс '0b'
            self.current_decimal = int(self.current_binary, 2)
            
            # Оновлюємо інтерфейс
            self.task_label.config(text="Переведіть число до десяткової системи:")
            self.hint_label.config(text="Погляньте на лампочки та введіть десяткове число")
            self.answer_label.config(text="Десятичне число:")
            
            # Встановлюємо лампочки згідно з двійковим числом
            binary_padded = self.current_binary.zfill(8)  # доповнюємо нулями зліва до 8 біт
            
            for i in range(8):
                self.bulb_values[i] = int(binary_padded[i])
                self.update_bulb(i)
                
            # Показуємо двійкове число замість генерації нового
            self.number_label.config(text="")
        
        # Очищаємо поле введення
        self.binary_entry.delete(0, tk.END)
    
    def check_answer(self):
        user_answer = self.binary_entry.get().strip()
        
        # Перевіряємо, що відповідь не порожня 
        if not user_answer: 
            if self.game_mode == "decimal_to_binary": 
                # Для режиму переведення в двійкову систему використовуємо стан лампочок 
                bulb_binary = ''.join(str(bit) for bit in self.bulb_values) 
                user_answer = bulb_binary.lstrip('0') or '0' # Видаляємо провідні нулі, але залишаємо хоча б один нуль 
            else: 
                messagebox.showinfo("Увага", "Будь ласка, введіть відповідь!") 
                return
        
        # Перевіряємо правильність відповіді 
        if self.game_mode == "decimal_to_binary": 
            # У режимі decimal_to_binary перевіряємо стан лампочок 
            bulb_binary = ''.join(str(bit) for bit in self.bulb_values) 
            bulb_binary = bulb_binary.lstrip('0') or '0' # Видаляємо провідні нулі, але залишаємо хоча б один нуль 
            is_correct = bulb_binary == self.current_binary 
        else: # binary_to_decimal 
            # Перевіряємо, що введено число 
            try: 
                user_decimal = int(user_answer) 
                is_correct = user_decimal == self.current_decimal 
            except ValueError: 
                messagebox.showinfo("Помилка", "Будь ласка, введіть десяткове число!") 
                return
        
        if is_correct:
            # Правильна відповідь
            points = self.current_level * 10
            self.score += points
            self.score_label.config(text=f"Очок: {self.score}")
            
            # Збільшуємо рівень кожні 3 правильні відповіді
            if self.score % (30 * self.current_level) == 0:
                self.current_level += 1
                self.level_label.config(text=f"Рівень: {self.current_level}")
                bonus_time = min(10, self.current_level * 2)  # бонусний час за новий рівень
                self.time_left += bonus_time
                messagebox.showinfo("Вітаємо!", f"Ви досягли рівня {self.current_level}!\nБонусний час: +{bonus_time} сек.")
            else:
                messagebox.showinfo("Вірно!", f"Ви заробили {points} очок!")
            
            # Генеруємо нове завдання
            self.generate_task()
        else:
            # Невірна відповідь
            correct_answer = self.current_binary if self.game_mode == "decimal_to_binary" else str(self.current_decimal)
            messagebox.showinfo("Невірно!", f"Правильна відповідь: {correct_answer}")
            
            # Штраф часу
            time_penalty = min(5, self.current_level)
            self.time_left = max(1, self.time_left - time_penalty)
            
            # Генеруємо нове завдання
            self.generate_task()
    
    def update_timer(self):
        if self.timer_running:
            self.time_left -= 1
            self.timer_label.config(text=f"Час: {self.time_left}")
            
            if self.time_left <= 0:
                self.timer_running = False
                messagebox.showinfo("Час вийшов!", f"Ваш результат: {self.score} очок!")
                
                # Запитуємо ім'я для таблиці лідерів, якщо результат хороший
                if self.score > 0:
                    name = tk.simpledialog.askstring("Таблиця лідерів", "Введіть ваше ім'я:")
                    if name:
                        self.save_score(name, self.score)
                
                self.show_menu()
                return
            
            # Продовжуємо оновлювати таймер
            self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    game = BrightBitsGame(root)
    root.mainloop()

