import tkinter as tk
from tkinter import ttk
import time

root = tk.Tk()
root.title("Progress Bar Example")

progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.pack(pady=20)

def update_progress():
    for i in range(101):
        progress_bar["value"] = i
        root.update_idletasks()
        time.sleep(0.1) 

update_button = tk.Button(root, text="Start Progress", command=update_progress)
update_button.pack()

root.mainloop()