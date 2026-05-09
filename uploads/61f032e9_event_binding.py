import tkinter as tk
from tkinter import messagebox

from gui import label

root = tk.Tk()
root.title("Event handling")
root.geometry("400x400")


def say_hi():
   print("hi")
   label.configure(text="Hi")

def on_key(event):
    print(f"key pressed: {event.char}")
    label.configure(text=f"key pressed: {event.char}")


button = tk.Button(root, text="Say Hi", command=say_hi)
button.pack(pady=20)

label=tk.Label(root,text="press a key or click the button")
label.pack(pady=20)

root.bind("<Key>", on_key)

root.mainloop()