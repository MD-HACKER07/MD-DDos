import customtkinter as ctk
import re
import time
from collections import deque

from attacks.layer4 import Layer4
from attacks.layer7 import Layer7
from attack_manager import AttackManager
from attacks.utils import Tools

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MD-DDos GUI")
        self.geometry("1000x750")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.attack_manager = None
        self.stats_data = deque(maxlen=60) # Store last 60 seconds of data
        self.last_req_count = 0

        # --- Main Frame ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- Title ---
        self.title_label = ctk.CTkLabel(self.main_frame, text="MD-DDos Control Panel", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(12, 0), padx=10)

        self.dev_label = ctk.CTkLabel(self.main_frame, text="Dev by MD ABU SHALEM ALAM, From Sanjivani University", font=ctk.CTkFont(size=12))
        self.dev_label.pack(pady=(0, 10), padx=10)

        # --- Top Frame (Inputs and Controls) ---
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(pady=10, padx=10, fill="x")
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)

        # --- Input Frame ---
        self.input_frame = ctk.CTkFrame(self.top_frame)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Target
        self.target_label = ctk.CTkLabel(self.input_frame, text="Target (URL or IP:Port)")
        self.target_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.target_entry = ctk.CTkEntry(self.input_frame, placeholder_text="http://example.com", width=250)
        self.target_entry.grid(row=0, column=1, padx=10, pady=5)

        # Method
        attack_methods = sorted(list(Layer4.METHODS | Layer7.METHODS))
        self.method_label = ctk.CTkLabel(self.input_frame, text="Attack Method")
        self.method_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.method_menu = ctk.CTkComboBox(self.input_frame, values=attack_methods)
        self.method_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.method_menu.set(attack_methods[0])

        # Threads
        self.threads_label = ctk.CTkLabel(self.input_frame, text="Threads: 1")
        self.threads_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.threads_slider = ctk.CTkSlider(self.input_frame, from_=1, to=1000, number_of_steps=999, command=self.update_threads_label)
        self.threads_slider.set(1)
        self.threads_slider.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Duration
        self.duration_label = ctk.CTkLabel(self.input_frame, text="Duration (s): 60")
        self.duration_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.duration_slider = ctk.CTkSlider(self.input_frame, from_=1, to=1200, number_of_steps=1199, command=self.update_duration_label)
        self.duration_slider.set(60)
        self.duration_slider.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # --- Control Frame ---
        self.control_frame = ctk.CTkFrame(self.top_frame)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.start_button = ctk.CTkButton(self.control_frame, text="Start Attack", command=self.start_attack, height=40)
        self.start_button.pack(pady=10, padx=20, fill="x")

        self.stop_button = ctk.CTkButton(self.control_frame, text="Stop Attack", command=self.stop_attack, state="disabled", height=40)
        self.stop_button.pack(pady=10, padx=20, fill="x")

        # --- Stats Frame ---
        self.stats_frame = ctk.CTkFrame(self.main_frame)
        self.stats_frame.pack(pady=10, padx=10, fill="x")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.rps_label = ctk.CTkLabel(self.stats_frame, text="RPS: 0", font=ctk.CTkFont(size=18, weight="bold"))
        self.rps_label.grid(row=0, column=0, padx=10, pady=10)

        self.requests_label = ctk.CTkLabel(self.stats_frame, text="Total Requests: 0", font=ctk.CTkFont(size=18, weight="bold"))
        self.requests_label.grid(row=0, column=1, padx=10, pady=10)

        self.data_label = ctk.CTkLabel(self.stats_frame, text="Total Data: 0 B", font=ctk.CTkFont(size=18, weight="bold"))
        self.data_label.grid(row=0, column=2, padx=10, pady=10)

        # --- Bottom Frame (Graph and Logs) ---
        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.bottom_frame.grid_columnconfigure(0, weight=2)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)

        # --- Graph Frame ---
        self.graph_frame = ctk.CTkFrame(self.bottom_frame)
        self.graph_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.fig, self.ax = plt.subplots(facecolor='#2B2B2B')
        self.ax.set_facecolor('#2B2B2B')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('#2B2B2B')
        self.ax.spines['right'].set_color('#2B2B2B')
        self.ax.set_title("Requests per Second", color='white')
        self.ax.set_xlabel("Time (s)", color='white')
        self.ax.set_ylabel("RPS", color='white')
        self.line, = self.ax.plot([], [], color='#1F6AA5', linewidth=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # --- Log Frame ---
        self.log_frame = ctk.CTkFrame(self.bottom_frame)
        self.log_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.log_textbox = ctk.CTkTextbox(self.log_frame)
        self.log_textbox.pack(fill="both", expand=True)

    def update_threads_label(self, value):
        self.threads_label.configure(text=f"Threads: {int(value)}")

    def update_duration_label(self, value):
        self.duration_label.configure(text=f"Duration (s): {int(value)}")

    def log_message(self, message):
        clean_message = re.sub(r'\x1b\[[0-9;]*m', '', message)
        self.log_textbox.insert("end", clean_message + "\n")
        self.log_textbox.see("end")

    def update_stats(self, requests, bytes_sent):
        rps = requests - self.last_req_count
        self.last_req_count = requests
        self.stats_data.append(rps)
        
        # Update graph
        self.line.set_data(range(len(self.stats_data)), list(self.stats_data))
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()

        # Update labels
        self.rps_label.configure(text=f"RPS: {rps}")
        self.requests_label.configure(text=f"Total Requests: {Tools.humanformat(requests)}")
        self.data_label.configure(text=f"Total Data: {Tools.humanbytes(bytes_sent)}")

    def start_attack(self):
        target = self.target_entry.get()
        method = self.method_menu.get()
        threads = int(self.threads_slider.get())
        duration = int(self.duration_slider.get())

        if not target:
            self.log_message("Error: Target is required.")
            return

        self.stats_data.clear()
        self.last_req_count = 0
        self.log_textbox.delete("1.0", "end")

        self.attack_manager = AttackManager(
            target_str=target,
            method=method,
            threads=threads,
            duration=duration,
            on_log=lambda msg: self.after(0, self.log_message, msg),
            on_stats_update=lambda req, b: self.after(0, self.update_stats, req, b)
        )
        self.attack_manager.start()

        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_attack(self):
        if self.attack_manager and self.attack_manager.is_alive():
            self.attack_manager.stop()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()


