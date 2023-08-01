import unittest
from unittest.mock import Mock


print = Mock()


class Account:
    def __init__(self, balance, account_number):
        self._balance = balance
        self._account_number = account_number

    @classmethod
    def create_account(cls, account_number):
        return cls(0.0, account_number)

    def deposit(self, amount):
        if amount > 0:
            self._balance += amount
        else:
            raise ValueError('Amount must be positive')

    def withdraw(self, amount):
        if amount > 0:
            self._balance -= amount
        else:
            raise ValueError('Amount must be positive')

    def get_balance(self):
        return self._balance

    def get_account_number(self):
        return self._account_number

    def __str__(self):
        return (f'Account number: {self._account_number}'
                f', balance: {self._balance}')


class SavingsAccount(Account):
    def __init__(self, balance, account_number, interest: float):
        super().__init__(balance, account_number)
        self.interest = interest

    def add_interest(self):
        self._balance += self._balance * self.interest

    @classmethod
    def create_account(cls, account_number):
        return cls(0.0, account_number, 0.02)


class CurrentAccount(Account):
    def __init__(self, balance, account_number, overdraft_limit):
        super().__init__(balance, account_number)
        self._overdraft_limit = overdraft_limit

    @classmethod
    def create_account(cls, account_number):
        return cls(0.0, account_number, 0.)

    def get_limit(self):
        return self._overdraft_limit


ACCOUNT_TYPES = {'account': Account,
                 'savings': SavingsAccount,
                 'current': CurrentAccount}


class Bank:
    def __init__(self, accounts: list[Account]):
        self._accounts = accounts

    def update(self):
        for acc in self._accounts:
            if isinstance(acc, SavingsAccount):
                acc.add_interest()
            elif isinstance(acc, CurrentAccount):
                if acc._balance < 0:
                    print(f'Account {acc.get_account_number()}'
                          f'is in overdraft by {-acc.get_balance()}, '
                          'remaining limit is '
                          f'{acc.get_limit() + acc.get_balance()}')

    def open_account(self, account_type: str, account_number):
        account_type = account_type.lower()
        if account_type in ACCOUNT_TYPES:
            if account_number not in self.get_account_numbers():
                self._accounts.append(ACCOUNT_TYPES[account_type]
                                      .create_account(account_number))
            else:
                raise ValueError('Given account number is already used')
        else:
            raise KeyError('Non-existing account type')

    def get_account_numbers(self):
        return {acc.get_account_number() for acc in self._accounts}

    def close_account(self, account_number):
        acc = [acc for acc in self._accounts
               if acc.get_account_number() == account_number]
        self._accounts.remove(*acc)

    def pay_dividends(self, amount):
        for acc in self._accounts:
            acc.deposit(amount)


def get_account_by_number(bank: Bank, account_number: int) -> Account:
    account = [
                acc for acc in bank._accounts
                if acc.get_account_number() == account_number
                ][0]
    return account


def test_bank_open_account_1():
    account_counter = 0
    bank = Bank([])
    for acc_type in list(ACCOUNT_TYPES.keys()):
        for case in [str.upper, str.lower, str.title]:
            account_type = case(acc_type)

            bank.open_account(
                account_type=account_type,
                account_number=account_counter)

            current_account = get_account_by_number(bank, account_counter)

            account_counter += 1

            # Check correct creation of accounts using different cases
            assert isinstance(current_account, ACCOUNT_TYPES[acc_type]), \
                (f'account_type=\'{acc_type} in {case.__name__}'
                 f' should create {ACCOUNT_TYPES[acc_type]}'
                 ' class object in _accounts list of Bank class'
                 )


test_bank_open_account_1()


class TestBankOpenAccount2(unittest.TestCase):
    def test_existing_account_number(self):
        account_type = 'account'
        account_number = 1
        bank = Bank([])
        bank.open_account(account_type=account_type,
                          account_number=account_number)

        with self.assertRaises(ValueError):
            bank.open_account(account_type=account_type,
                              account_number=account_number)

    def test_wrong_acc_type(self):
        account_type = 'acount '
        account_number = 1
        bank = Bank([])

        with self.assertRaises(KeyError):
            bank.open_account(account_type=account_type,
                              account_number=account_number)

    def test_account_balance(self):
        account_type = 'account'
        account_number = 1
        expected_balance = 0.
        bank = Bank([])
        bank.open_account(account_type=account_type,
                          account_number=account_number)

        self.assertEqual(
            get_account_by_number(bank, account_number).get_balance(),
            expected_balance
        )


def test_bank_open_account_3():
    account_type = 'savings'
    account_number = 0
    bank = Bank([])
    initialy_added_balance = 1000.
    expected_balance = 1020.
    bank.open_account(account_type=account_type,
                      account_number=account_number)

    bank.pay_dividends(initialy_added_balance)
    bank.update()

    account = get_account_by_number(bank, account_number)

    assert account.get_balance() == expected_balance, \
        (
        f'Balance on savings account should get its {account.interest}'
        ' interest on bank\'s update() call'
         )


test_bank_open_account_3()


def test_bank_open_account_4():
    account_type = 'current'
    account_number = 0
    bank = Bank([])
    initialy_withdrawn_from_balance = 5.
    bank.open_account(account_type=account_type,
                      account_number=account_number)

    account = get_account_by_number(bank, account_number)

    account.withdraw(initialy_withdrawn_from_balance)

    bank.update()
    print.assert_called_once()


test_bank_open_account_4()

unittest.main()
