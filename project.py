import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# -----------------------------
# Student Class
# -----------------------------
class Student:
    def __init__(self, name, subjects, marks):
        if not name or not name.strip():
            raise ValueError("Student name cannot be empty.")
        if len(subjects) != len(marks):
            raise ValueError("Subjects and marks must have the same length.")
        if not subjects:
            raise ValueError("At least one subject is required.")

        self.name = name.strip()
        self.subjects = list(subjects)
        self.marks = list(marks)

    def calculate_average(self):
        if not self.marks:
            return 0
        return sum(self.marks) / len(self.marks)

    def print_average(self):
        print(f"{self.name}'s average marks: {self.calculate_average():.2f}")

    def to_dict(self):
        return {
            "name": self.name,
            "subjects": self.subjects,
            "marks": self.marks
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["subjects"], data["marks"])

    def __str__(self):
        return f"{self.name}: {self.subjects} -> {self.marks}"


# -----------------------------
# StudentReport Class
# -----------------------------
class StudentReport:
    def __init__(self, filename="student_report.json"):
        self.filename = Path(filename)
        self.students = []

    def add_student(self, student):
        self.students.append(student)

    def save_to_file(self):
        data = [student.to_dict() for student in self.students]
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_from_file(self):
        if not self.filename.exists():
            self.students = []
            return

        with self.filename.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.students = [Student.from_dict(item) for item in data]

    def print_report(self):
        if not self.students:
            print("No student records found.")
            return

        for student in self.students:
            print(f"{student.name} average: {student.calculate_average():.2f}")


# -----------------------------
# Account Class
# -----------------------------
class Account:
    def __init__(self, account_no, balance=0):
        if not account_no or not str(account_no).strip():
            raise ValueError("Account number cannot be empty.")
        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")

        self.account_no = str(account_no).strip()
        self.balance = float(balance)

    def credit(self, amount):
        if amount <= 0:
            print("Credit amount must be positive.")
            return
        self.balance += float(amount)
        print(f"Credited {amount}. New balance: {self.balance:.2f}")

    def debit(self, amount):
        if amount <= 0:
            print("Debit amount must be positive.")
            return
        if float(amount) > self.balance:
            print("Insufficient funds.")
            return
        self.balance -= float(amount)
        print(f"Debited {amount}. New balance: {self.balance:.2f}")

    def print_balance(self):
        print(f"Account {self.account_no} balance: {self.balance:.2f}")

    def to_dict(self):
        return {
            "account_no": self.account_no,
            "balance": self.balance
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["account_no"], data["balance"])


# -----------------------------
# Bank Class
# -----------------------------
class Bank:
    def __init__(self, filename="bank_data.json"):
        self.filename = Path(filename)
        self.accounts = {}

    def add_account(self, account):
        if account.account_no in self.accounts:
            raise ValueError("Account number already exists.")
        self.accounts[account.account_no] = account

    def get_account(self, account_no):
        return self.accounts.get(account_no)

    def credit(self, account_no, amount):
        account = self.get_account(account_no)
        if account is None:
            print("Account not found.")
            return
        account.credit(amount)

    def debit(self, account_no, amount):
        account = self.get_account(account_no)
        if account is None:
            print("Account not found.")
            return
        account.debit(amount)

    def save_to_file(self):
        data = {key: value.to_dict() for key, value in self.accounts.items()}
        with self.filename.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load_from_file(self):
        if not self.filename.exists():
            self.accounts = {}
            return

        with self.filename.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.accounts = {
            key: Account.from_dict(value)
            for key, value in data.items()
        }

    def print_all_balances(self):
        if not self.accounts:
            print("No accounts available.")
            return

        for account in self.accounts.values():
            account.print_balance()


# -----------------------------
# Simple GUI
# -----------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Report & Bank Manager")
        self.root.geometry("700x500")

        self.student_report = StudentReport("student_report.json")
        self.bank = Bank("bank_data.json")

        try:
            self.student_report.load_from_file()
            self.bank.load_from_file()
        except Exception:
            pass

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.student_tab = ttk.Frame(self.notebook)
        self.bank_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.student_tab, text="Students")
        self.notebook.add(self.bank_tab, text="Bank")

        self.build_student_tab()
        self.build_bank_tab()
        self.refresh_student_list()
        self.refresh_bank_list()

    def build_student_tab(self):
        tk.Label(self.student_tab, text="Student Name").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.student_name = tk.Entry(self.student_tab, width=30)
        self.student_name.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.student_tab, text="Subjects (comma separated)").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.student_subjects = tk.Entry(self.student_tab, width=30)
        self.student_subjects.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.student_tab, text="Marks (comma separated)").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.student_marks = tk.Entry(self.student_tab, width=30)
        self.student_marks.grid(row=2, column=1, padx=10, pady=5)

        tk.Button(self.student_tab, text="Add Student", command=self.add_student_gui).grid(row=3, column=0, columnspan=2, pady=10)

        self.student_listbox = tk.Listbox(self.student_tab, width=70, height=15)
        self.student_listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def build_bank_tab(self):
        tk.Label(self.bank_tab, text="Account Number").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.account_no = tk.Entry(self.bank_tab, width=25)
        self.account_no.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.bank_tab, text="Initial Balance").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.initial_balance = tk.Entry(self.bank_tab, width=25)
        self.initial_balance.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self.bank_tab, text="Create Account", command=self.add_account_gui).grid(row=2, column=0, columnspan=2, pady=10)

        tk.Label(self.bank_tab, text="Amount").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.amount_entry = tk.Entry(self.bank_tab, width=25)
        self.amount_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(self.bank_tab, text="Deposit", command=self.deposit_gui).grid(row=4, column=0, padx=10, pady=5)
        tk.Button(self.bank_tab, text="Withdraw", command=self.withdraw_gui).grid(row=4, column=1, padx=10, pady=5)

        self.bank_listbox = tk.Listbox(self.bank_tab, width=70, height=15)
        self.bank_listbox.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def add_student_gui(self):
        try:
            name = self.student_name.get()
            subjects = [s.strip() for s in self.student_subjects.get().split(",") if s.strip()]
            marks = [float(m.strip()) for m in self.student_marks.get().split(",") if m.strip()]

            student = Student(name, subjects, marks)
            self.student_report.add_student(student)
            self.student_report.save_to_file()
            self.refresh_student_list()
            messagebox.showinfo("Success", f"Student {student.name} added.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_account_gui(self):
        try:
            account_no = self.account_no.get()
            balance = float(self.initial_balance.get())
            account = Account(account_no, balance)
            self.bank.add_account(account)
            self.bank.save_to_file()
            self.refresh_bank_list()
            messagebox.showinfo("Success", f"Account {account_no} created.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def deposit_gui(self):
        try:
            account_no = self.account_no.get()
            amount = float(self.amount_entry.get())
            self.bank.credit(account_no, amount)
            self.bank.save_to_file()
            self.refresh_bank_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def withdraw_gui(self):
        try:
            account_no = self.account_no.get()
            amount = float(self.amount_entry.get())
            self.bank.debit(account_no, amount)
            self.bank.save_to_file()
            self.refresh_bank_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_student_list(self):
        self.student_listbox.delete(0, tk.END)
        for student in self.student_report.students:
            self.student_listbox.insert(
                tk.END,
                f"{student.name} | Average: {student.calculate_average():.2f}"
            )

    def refresh_bank_list(self):
        self.bank_listbox.delete(0, tk.END)
        for account in self.bank.accounts.values():
            self.bank_listbox.insert(
                tk.END,
                f"Account: {account.account_no} | Balance: {account.balance:.2f}"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()