import  datetime

class BankAccount:
    def __init__(self, name, initial_balance , pin):
        self.name = name
        self.balance = initial_balance
        self.pin = pin


        self.trans_hst = []
        self.log_transaction(f"Account created with ${initial_balance}")

    def save_to_file(self):

        filename = f"{self.name}_history.txt"

        with open(filename, 'w') as file:
            file.write(f"--Transaction History for {self.name}---\n")
            file.write(f"Account Balance: ${self.balance}\n")
            file.write("---------------------------------------------------\n")

            for t in self.trans_hst:
                line = f"[{t['time']}] [{t['event']}] | Bal: ${t['balance_factor']}\n"
                file.write(line)

        print(f"\n[System] Data saved to {filename}")


    def deposit(self, amount):
        if amount>0:
            self.balance+= amount
            self.log_transaction(f"Success! New Balance: ${self.balance}")

        else:
            print("Error: Deposit amount is invalid!")

    
    def withdraw(self, amount , pin):
        if self.pin != pin:
            print(f"The pin in invalid!")
            return False
    
        if amount>self.balance:
            print(f"The balance is insufficient!")
            return False
        

        self.balance -= amount
        self.log_transaction(f"Withdrew: ${amount}")
        print(f"Success! New Balance is ${self.balance}")


    def log_transaction(self, des):
        timestap = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = {
            "time": timestap,
            "event": des,
            "balance_factor": self.balance
        }

        self.trans_hst.append(entry)

    
    def print_statement(self):

        print(f"\n---Statement for {self.name}---")
        for t in self.trans_hst:
            print(f"[{t['time']}] [{t['event']}] | Bal: ${t['balance_factor']}")
            print("-----------------------------------")





class SavingsAccount(BankAccount):
    def __init__(self,name, initial_balance, pin,  Rate= 0.05):
        super().__init__( name, initial_balance, pin)

        self.interest_rate = Rate
        self.min_balance = 100

    def apply_interest(self):
        interest_amount = self.balance*self.interest_rate
        self.balance += interest_amount

        self.log_transaction(f"Interest Applied! ${interest_amount:.2f}")
        print(f"Interest added! ${self.balance:.2f}")


    def withdraw(self, amount, entered_pin):
        if(self.balance - amount < self.min_balance):
            print(f"Error: Saving account cannot drop below $100")
            return False

        return super().withdraw(amount, entered_pin)
    




# if __name__ == "__main__":
#     navya_acc = BankAccount("Navya", 1000, 1234)

#     navya_acc.deposit(500)
#     navya_acc.withdraw(200, 1234)
#     navya_acc.withdraw(2000, 1234) # Should fail (Insufficient funds)
#     navya_acc.withdraw(100, 9999)

#     navya_acc.print_statement()

if __name__ == "__main__":
    print("--- TESTING SAVINGS ACCOUNT ---")
    # Create a Savings Account (Notice the 5% interest default)
    my_savings = SavingsAccount("Navya Savings", 2000, 5555)

    # 1. Test Deposit (Inherited from Parent)
    my_savings.deposit(500)

    # 2. Test Interest (New Child Method)
    my_savings.apply_interest()

    # 3. Test Withdrawal Limit (Overridden Method)
    # This should FAIL because 2625 - 2600 = 25, which is < 100
    print("\nAttempting to empty the account...")
    my_savings.withdraw(2600, 5555) 

    # 4. View Statement
    my_savings.print_statement()

    # 5. Save to hard drive
    my_savings.save_to_file()
