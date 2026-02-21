import tkinter as tk
from tkinter import messagebox

class LoginFrame(tk.Frame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        self.entry_username = tk.Entry(self)
        self.entry_username.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=10)
        self.entry_password = tk.Entry(self, show="*")
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(self, text="Login", command=self.check_credentials)\
            .grid(row=2, column=0, columnspan=2, pady=20)

    def check_credentials(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()

        if username == "admin" and password == "password":
            messagebox.showinfo("Login Successful", "Welcome, admin!")
            self.on_login_success()
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
