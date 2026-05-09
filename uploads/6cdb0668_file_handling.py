import tkinter as tk
from tkinter import filedialog, messagebox

root = tk.Tk()
root.title("File Handling")
root.geometry("500x500")

text_area = tk.Text(root, wrap='word', width=60, height=20)
text_area.pack(pady=20)

# Keep track of the last opened file
last_file_path = None

def open_file():
    global last_file_path
    file_path = filedialog.askopenfilename(
        initialdir=r"C:\Users\UA\OneDrive\Desktop\alishba\sdc",
        title="Open File",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_path:
        try:
            with open(file_path, "r") as file:
                content = file.read()
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, content)
            last_file_path = file_path  # Save the file path
            messagebox.showinfo("File Handling", f"File '{file_path}' has been opened")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file.\n{e}")

def write_file():
    global last_file_path
    if last_file_path:
        # If a file was previously opened, overwrite it directly
        try:
            with open(last_file_path, "w") as file:
                content = text_area.get(1.0, tk.END)
                file.write(content)
            messagebox.showinfo("File Handling", f"File '{last_file_path}' has been saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file.\n{e}")
    else:
        # If no file was opened yet, ask for location (Save As)
        file_path = filedialog.asksaveasfilename(
            initialdir=r"C:\Users\UA\OneDrive\Desktop\alishba\sdc",
            title="Save File",
            defaultextension=".txt",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if file_path:
            try:
                with open(file_path, "w") as file:
                    content = text_area.get(1.0, tk.END)
                    file.write(content)
                last_file_path = file_path
                messagebox.showinfo("File Handling", f"File '{file_path}' has been saved")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file.\n{e}")

# Buttons
tk.Button(root, text="Open File", command=open_file, width=20).pack(pady=10)
tk.Button(root, text="Save File", command=write_file, width=20).pack(pady=10)

root.mainloop()