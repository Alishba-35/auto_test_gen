import unittest
import tkinter as tk
from tkinter import ttk

import foodwasting as app

# Disable messageboxes immediately
app.messagebox.showerror = lambda *a, **k: None
app.messagebox.showinfo = lambda *a, **k: None
app.messagebox.showwarning = lambda *a, **k: None


class TestFoodWasteApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()

        # Mock entries
        app.entry_name = tk.Entry(cls.root)
        app.entry_type = tk.Entry(cls.root)
        app.entry_qty = tk.Entry(cls.root)
        app.entry_location = tk.Entry(cls.root)
        app.entry_expiry = tk.Entry(cls.root)

        # Proper Treeview
        app.tree = ttk.Treeview(
            cls.root,
            columns=("Name","Type","Qty","Location","Expiry","Status"),
            show="headings"
        )

        cls.root.update()

        # Dummy DB
        class DummyCursor:
            def __init__(self):
                self.data = []

            def execute(self, query, params=None):
                if "INSERT" in query:
                    self.data.append(params)

            def fetchone(self):
                return None

            def fetchall(self):
                return self.data

        class DummyConn:
            def commit(self):
                pass

        app.cursor = DummyCursor()
        app.conn = DummyConn()

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def clear_entries(self):
        app.entry_name.delete(0, tk.END)
        app.entry_type.delete(0, tk.END)
        app.entry_qty.delete(0, tk.END)
        app.entry_location.delete(0, tk.END)
        app.entry_expiry.delete(0, tk.END)

    def test_valid_input(self):
        self.clear_entries()

        app.entry_name.insert(0, "Apple")
        app.entry_type.insert(0, "Fruit")
        app.entry_qty.insert(0, "5")
        app.entry_location.insert(0, "Kitchen")
        app.entry_expiry.insert(0, "2099-12-31")

        app.add_record()

        self.assertEqual(len(app.cursor.data), 1)

    def test_empty_fields(self):
        self.clear_entries()

        app.entry_name.insert(0, "")
        app.entry_type.insert(0, "Fruit")
        app.entry_qty.insert(0, "5")
        app.entry_location.insert(0, "Kitchen")
        app.entry_expiry.insert(0, "2099-12-31")

        app.add_record()

        self.assertEqual(len(app.cursor.data), 0)

    def test_invalid_quantity(self):
        self.clear_entries()

        app.entry_name.insert(0, "Milk")
        app.entry_type.insert(0, "Dairy")
        app.entry_qty.insert(0, "abc")
        app.entry_location.insert(0, "Fridge")
        app.entry_expiry.insert(0, "2099-12-31")

        app.add_record()

        self.assertEqual(len(app.cursor.data), 0)

    def test_clear_fields(self):
        app.entry_name.insert(0, "Test")
        app.clear_fields()

        self.assertEqual(app.entry_name.get(), "")


if __name__ == "__main__":
    unittest.main()