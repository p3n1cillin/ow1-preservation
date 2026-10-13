"""Local preservation accounts for the private OW1 server.

These are our own accounts, unrelated to Battle.net. Each has a display name,
a battle tag derived from it (`Name#<account id>`), a numeric account id used
as the low half of the account/game-account EntityIds and lobby identities,
and an optional password kept only as a salted PBKDF2-SHA256 hash.
The store is a small JSON file outside Git (default `.local/accounts.json`).
"""
import hashlib
import hmac
import json
import os
import re
from pathlib import Path

FIRST_ID = 1001
MAX_ACCOUNTS = 1000
ITERATIONS = 200_000
NAME_RE = re.compile(r'[A-Za-z][A-Za-z0-9]{2,11}')
DEFAULT_STORE = Path(__file__).absolute().parents[1] / '.local' / 'accounts.json'


def _hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS).hex()


class AccountStore:
    def __init__(self, path=DEFAULT_STORE):
        self.path = Path(path)
        self.accounts = []
        self.next_id = FIRST_ID
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if not isinstance(data, dict) or not isinstance(data.get('accounts'), list):
                raise ValueError('account store format')
            self.accounts = data['accounts']
            for account in self.accounts:
                self._validate(account)
            highest = max([a['account_id'] for a in self.accounts], default=FIRST_ID - 1)
            self.next_id = max(int(data.get('next_id', FIRST_ID)), highest + 1)

    @staticmethod
    def _validate(account):
        if not NAME_RE.fullmatch(account.get('name', '')):
            raise ValueError('account name: 3-12 letters/digits, starting with a letter')
        if type(account.get('account_id')) is not int or not FIRST_ID <= account['account_id'] < 2**32:
            raise ValueError('account id bounds')
        if account.get('battle_tag') != f"{account['name']}#{account['account_id']}":
            raise ValueError('battle tag mismatch')

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps({'next_id': self.next_id, 'accounts': self.accounts}, indent=2) + '\n', encoding='utf-8')
        os.replace(temp, self.path)

    def find(self, name):
        for account in self.accounts:
            if account['name'].lower() == name.lower():
                return account
        return None

    def create(self, name, password=None):
        if self.find(name):
            raise ValueError(f'account {name!r} already exists')
        if len(self.accounts) >= MAX_ACCOUNTS:
            raise ValueError('account store is full')
        account_id = self.next_id
        account = dict(name=name, account_id=account_id, battle_tag=f'{name}#{account_id}')
        if password:
            salt = os.urandom(16)
            account.update(salt=salt.hex(), password=_hash(password, salt))
        self._validate(account)
        self.accounts.append(account)
        self.next_id = account_id + 1
        self.save()
        return account

    def verify(self, name, password):
        account = self.find(name)
        if account is None:
            raise ValueError(f'no account {name!r}')
        if 'password' in account:
            expected = _hash(password or '', bytes.fromhex(account['salt']))
            if not hmac.compare_digest(expected, account['password']):
                raise ValueError('wrong password')
        return account

    def delete(self, name):
        account = self.find(name)
        if account is None:
            raise ValueError(f'no account {name!r}')
        self.accounts.remove(account)
        self.save()
