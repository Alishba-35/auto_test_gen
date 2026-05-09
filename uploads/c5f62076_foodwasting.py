import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime, timedelta   # also required
def connect_db():
    try:
        conn = sqlite3.connect("food_waste.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            quantity REAL,
            location TEXT,
            expiry_date TEXT,
            status TEXT DEFAULT 'Available'
        )
        """)

        conn.commit()
        return conn, cursor

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))
        exit()


conn, cursor = connect_db()


# ───────────────────────── LOGIC ─────────────────────────
def validate_quantity(event):
    val = entry_qty.get()
    if val and not val.replace(".", "", 1).isdigit():
        messagebox.showerror("Error", "Quantity must be numeric!")
        entry_qty.focus_set()


def check_expiry_alerts():
    cursor.execute("SELECT name, expiry_date FROM food_items WHERE status='Available'")
    items = cursor.fetchall()

    tomorrow = datetime.now() + timedelta(days=1)

    alerts = []
    for name, date_str in items:
        try:
            exp = datetime.strptime(date_str, "%Y-%m-%d")
            if exp <= tomorrow:
                alerts.append(f"{name} (Expiry: {date_str})")
        except:
            pass

    if alerts:
        messagebox.showwarning("Expiry Alert", "\n".join(alerts))


def add_record():
    name = entry_name.get().strip()
    ftype = entry_type.get().strip()
    qty = entry_qty.get().strip()
    loc = entry_location.get().strip()
    exp = entry_expiry.get().strip()

    # Validation
    if not all([name, ftype, qty, loc, exp]):
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        qty = float(qty)
        if qty <= 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Quantity must be positive number")
        return

    try:
        exp_date = datetime.strptime(exp, "%Y-%m-%d")
        if exp_date < datetime.now():
            messagebox.showerror("Error", "Expiry date cannot be in the past")
            return
    except:
        messagebox.showerror("Error", "Invalid date format (YYYY-MM-DD)")
        return

    # Duplicate check
    cursor.execute(
        "SELECT * FROM food_items WHERE name=? AND expiry_date=?",
        (name, exp)
    )
    if cursor.fetchone():
        messagebox.showerror("Error", "Duplicate record!")
        return

    # Insert
    cursor.execute("""
        INSERT INTO food_items (name, type, quantity, location, expiry_date)
        VALUES (?, ?, ?, ?, ?)
    """, (name, ftype, qty, loc, exp))

    conn.commit()

    if exp_date <= datetime.now() + timedelta(days=1):
        messagebox.showwarning("Alert", "⚠ Food expiring within 24 hours!")

    messagebox.showinfo("Success", "Record Added Successfully")

    clear_fields()
    load_records()


def clear_fields():
    entry_name.delete(0, tk.END)
    entry_type.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_location.delete(0, tk.END)
    entry_expiry.delete(0, tk.END)


def load_records():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT name, type, quantity, location, expiry_date, status FROM food_items")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)


# ───────────────────────── GUI ─────────────────────────
root = tk.Tk()
root.title("Food Waste Management System")
root.geometry("650x520")
root.configure(bg="#dcdcdc")

# HEADER
header = tk.Frame(root, bg="#6b8e23", height=70)
header.pack(fill="x")

tk.Label(
    header,
    text="Food Waste Management System",
    bg="#6b8e23",
    fg="white",
    font=("Arial", 16, "bold")
).pack(pady=20)

# NOTEBOOK (Tabs)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab1 = tk.Frame(notebook, bg="#dcdcdc")
tab2 = tk.Frame(notebook, bg="#dcdcdc")

notebook.add(tab1, text="Submit Food")
notebook.add(tab2, text="View Records")

# ───────── FORM (matches your image) ─────────
form = tk.Frame(tab1, bg="#dcdcdc")
form.pack(pady=20)

tk.Label(form, text="Food Name", bg="#dcdcdc").pack()
entry_name = tk.Entry(form, width=25)
entry_name.pack(pady=5)

tk.Label(form, text="Type", bg="#dcdcdc").pack()
entry_type = tk.Entry(form, width=25)
entry_type.pack(pady=5)

tk.Label(form, text="Quantity", bg="#dcdcdc").pack()
entry_qty = tk.Entry(form, width=25)
entry_qty.pack(pady=5)
entry_qty.bind("<FocusOut>", validate_quantity)

tk.Label(form, text="Location", bg="#dcdcdc").pack()
entry_location = tk.Entry(form, width=25)
entry_location.pack(pady=5)

tk.Label(form, text="Expiry Date (YYYY-MM-DD)", bg="#dcdcdc").pack()
entry_expiry = tk.Entry(form, width=25)
entry_expiry.pack(pady=5)

# BUTTONS (same style as image)
btn_frame = tk.Frame(tab1, bg="#dcdcdc")
btn_frame.pack(pady=20)

tk.Button(
    btn_frame, text="Add Record",
    bg="#28a745", fg="white", width=15, height=2,
    command=add_record
).grid(row=0, column=0, padx=10)

tk.Button(
    btn_frame, text="View Records",
    bg="#007bff", fg="white", width=15, height=2,
    command=lambda: notebook.select(tab2)
).grid(row=0, column=1, padx=10)

tk.Button(
    btn_frame, text="Clear Fields",
    bg="#dc3545", fg="white", width=15, height=2,
    command=clear_fields
).grid(row=0, column=2, padx=10)

# ───────── RECORD TABLE ─────────
columns = ("Name", "Type", "Qty", "Location", "Expiry", "Status")

tree = ttk.Treeview(tab2, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)

tree.pack(fill="both", expand=True, padx=10, pady=10)

tk.Button(tab2, text="Refresh", command=load_records).pack(pady=5)

# ───────── STARTUP ─────────
load_records()
root.after(1000, check_expiry_alerts)

def on_close():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()