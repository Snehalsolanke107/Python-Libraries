import json
import os
import re
from datetime import datetime

class Transaction:

    def __init__(self, transaction_id, account_no,transaction_type, amount, balance_after,date=None):

        self.transaction_id = transaction_id
        self.account_no = account_no
        self.type = transaction_type
        self.amount = amount
        self.balance_after = balance_after

        if date is None:
            self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.date = date

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "account_no": self.account_no,
            "type": self.type,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "date": self.date
        }

    def display_transaction(self):
        print(
            f"{self.transaction_id:<15}"
            f"{self.type:<12}"
            f"₹{self.amount:,.2f}     "
            f"₹{self.balance_after:,.2f}"
        )

class Account:

    MIN_INITIAL_DEPOSIT = 500

    def __init__(self, account_no, name, mobile,account_type, balance):

        self.account_no = account_no
        self.name = name
        self.mobile = mobile
        self.account_type = account_type
        self.balance = float(balance)

    def deposit(self, amount):

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        previous_balance = self.balance
        self.balance += amount

        return previous_balance, self.balance

    def withdraw(self, amount):

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount > self.balance:
            raise ValueError("Insufficient Balance.")

        previous_balance = self.balance
        self.balance -= amount

        return previous_balance, self.balance

    def check_balance(self):
        print("\n========== ACCOUNT BALANCE ==========")
        print("Account Number :", self.account_no)
        print("Customer Name  :", self.name)
        print(f"Current Balance: ₹{self.balance:,.2f}")

    def display_details(self):
        print("\n========== ACCOUNT DETAILS ==========")
        print("Account Number :", self.account_no)
        print("Customer Name  :", self.name)
        print("Mobile Number  :", self.mobile)
        print("Account Type   :", self.account_type)
        print(f"Balance        : ₹{self.balance:,.2f}")

    def to_dict(self):
        return {
            "account_no": self.account_no,
            "name": self.name,
            "mobile": self.mobile,
            "account_type": self.account_type,
            "balance": self.balance
        }

class Bank:

    def __init__(self, filename="bank_data.json"):

        self.filename = filename
        self.accounts = {}
        self.transactions = []

        self.load_data()

    def load_data(self):

        if not os.path.exists(self.filename):
            self.save_data()
            return

        try:
            with open(self.filename, "r") as file:
                data = json.load(file)

            for item in data.get("accounts", []):
                account = Account(
                    item["account_no"],
                    item["name"],
                    item["mobile"],
                    item["account_type"],
                    item["balance"]
                )

                self.accounts[account.account_no] = account

            for item in data.get("transactions", []):
                transaction = Transaction(
                    item["transaction_id"],
                    item["account_no"],
                    item["type"],
                    item["amount"],
                    item["balance_after"],
                    item.get("date")
                )

                self.transactions.append(transaction)

        except (json.JSONDecodeError, OSError) as error:
            raise RuntimeError(
                f"Could not load bank data: {error}"
            ) from error

    def save_data(self):

        data = {
            "accounts": [
                account.to_dict()
                for account in self.accounts.values()
            ],
            "transactions": [
                transaction.to_dict()
                for transaction in self.transactions
            ]
        }

        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    def generate_id(self, prefix, existing_ids):

        numbers = []

        for value in existing_ids:
            if value.startswith(prefix):
                suffix = value[len(prefix):]

                if suffix.isdigit():
                    numbers.append(int(suffix))

        next_number = max(numbers, default=1000) + 1

        return f"{prefix}{next_number}"

    def search_account(self, account_no):

        return self.accounts.get(account_no)

    def create_account(self, name, mobile,
                       account_type, initial_deposit):

        name = name.strip()
        mobile = mobile.strip()
        account_type = account_type.strip().title()

        if not name:
            raise ValueError("Customer name cannot be empty.")

        if not re.fullmatch(r"\d{10}", mobile):
            raise ValueError(
                "Mobile number must contain exactly 10 digits."
            )

        if account_type not in ("Savings", "Current"):
            raise ValueError(
                "Account type must be Savings or Current."
            )

        if initial_deposit < Account.MIN_INITIAL_DEPOSIT:
            raise ValueError(
                f"Minimum initial deposit is "
                f"₹{Account.MIN_INITIAL_DEPOSIT}."
            )

        account_no = self.generate_id(
            "ACC",
            self.accounts.keys()
        )

        account = Account(
            account_no,
            name,
            mobile,
            account_type,
            initial_deposit
        )

        self.accounts[account_no] = account

        self.add_transaction(
            account_no,
            "DEPOSIT",
            initial_deposit,
            account.balance
        )

        self.save_data()

        return account

    def add_transaction(self, account_no,
                        transaction_type, amount,
                        balance_after):

        transaction_id = self.generate_id(
            "TXN",
            [t.transaction_id for t in self.transactions]
        )

        transaction = Transaction(
            transaction_id,
            account_no,
            transaction_type,
            amount,
            balance_after
        )

        self.transactions.append(transaction)

        return transaction

    def deposit_money(self, account_no, amount):

        account = self.search_account(account_no)

        if account is None:
            raise ValueError("Account not found.")

        previous_balance, new_balance = account.deposit(amount)

        transaction = self.add_transaction(
            account_no,
            "DEPOSIT",
            amount,
            new_balance
        )

        self.save_data()

        print("\nDeposit Successful!")
        print(f"Previous Balance: ₹{previous_balance:,.2f}")
        print(f"Deposit Amount  : ₹{amount:,.2f}")
        print(f"New Balance     : ₹{new_balance:,.2f}")
        print("Transaction ID  :", transaction.transaction_id)

    def withdraw_money(self, account_no, amount):

        account = self.search_account(account_no)

        if account is None:
            raise ValueError("Account not found.")

        previous_balance, new_balance = account.withdraw(amount)

        transaction = self.add_transaction(
            account_no,
            "WITHDRAW",
            amount,
            new_balance
        )

        self.save_data()

        print("\nWithdrawal Successful!")
        print(f"Previous Balance: ₹{previous_balance:,.2f}")
        print(f"Withdrawal      : ₹{amount:,.2f}")
        print(f"Remaining Balance: ₹{new_balance:,.2f}")
        print("Transaction ID  :", transaction.transaction_id)

    def view_transaction_history(self, account_no):

        account = self.search_account(account_no)

        if account is None:
            print("Account not found.")
            return

        history = [
            transaction
            for transaction in self.transactions
            if transaction.account_no == account_no
        ]

        print("\n================ TRANSACTION HISTORY ================")
        print("Account Number:", account_no)
        print("Customer Name :", account.name)

        if not history:
            print("No transactions found.")
            return

        print("-" * 65)
        print(
            f"{'Transaction ID':<15}"
            f"{'Type':<12}"
            f"{'Amount':<18}"
            f"{'Balance After':<18}"
        )
        print("-" * 65)

        for transaction in history:
            transaction.display_transaction()
            print("Date:", transaction.date)

        print("-" * 65)


def get_amount(message):

    while True:
        try:
            amount = float(input(message))

            if amount <= 0:
                print("Amount must be greater than zero.")
                continue

            return amount

        except ValueError:
            print("Please enter a valid numeric amount.")


def get_account(bank):

    account_no = input("Enter Account Number: ").strip()
    account = bank.search_account(account_no)

    if account is None:
        print("Account not found.")

    return account


def main():

    bank = Bank()

    print("Bank data loaded successfully.")

    while True:

        print("\n========== BANK MANAGEMENT SYSTEM ==========")
        print("1. Create Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Check Balance")
        print("5. View Account Details")
        print("6. View Transaction History")
        print("7. Exit")

        choice = input("Enter your choice: ").strip()

        try:

            if choice == "1":

                name = input("Enter Customer Name: ")
                mobile = input("Enter Mobile Number: ")
                account_type = input(
                    "Enter Account Type (Savings/Current): "
                )

                initial_deposit = get_amount(
                    "Enter Initial Deposit: ₹"
                )

                account = bank.create_account(
                    name,
                    mobile,
                    account_type,
                    initial_deposit
                )

                print("\nAccount Created Successfully!")
                account.display_details()

            elif choice == "2":

                account = get_account(bank)

                if account is not None:
                    amount = get_amount("Enter Deposit Amount: ₹")
                    bank.deposit_money(account.account_no, amount)

            elif choice == "3":

                account = get_account(bank)

                if account is not None:
                    amount = get_amount(
                        "Enter Withdrawal Amount: ₹"
                    )

                    bank.withdraw_money(account.account_no, amount)

            elif choice == "4":

                account = get_account(bank)

                if account is not None:
                    account.check_balance()

            elif choice == "5":

                account = get_account(bank)

                if account is not None:
                    account.display_details()

            elif choice == "6":

                account_no = input(
                    "Enter Account Number: "
                ).strip()

                bank.view_transaction_history(account_no)

            elif choice == "7":

                bank.save_data()
                print("Bank data saved successfully.")
                print("Thank you for using the Bank Management System!")
                break

            else:
                print("Invalid choice. Please enter 1 to 7.")

        except ValueError as error:
            print("Transaction Failed:", error)

        except OSError as error:
            print("File operation failed:", error)


if __name__ == "__main__":
    main()