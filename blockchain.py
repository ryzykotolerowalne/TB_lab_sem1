import hashlib
import json
from time import time


class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = []
        self.current_transactions = []
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = {
            "index": 1,
            "timestamp": 0,
            "transactions": [],
            "nonce": 0,
            "previous_hash": "0" * 64,
        }
        self.chain.append(genesis)

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            for tx in block["transactions"]:
                if tx["recipient"] == address:
                    balance += tx["amount"]
                if tx["sender"] == address:
                    balance -= tx["amount"]
        for tx in self.current_transactions:
            if tx["recipient"] == address:
                balance += tx["amount"]
            if tx["sender"] == address:
                balance -= tx["amount"]
        return balance

    def new_transaction(self, sender, recipient, amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Kwota musi być liczbą")
        if amount <= 0 or amount > 1_000_000_000 or amount != amount:
            raise ValueError("Kwota musi być dodatnia i mieścić się w dozwolonym zakresie")
        if not isinstance(sender, str) or not sender.strip():
            raise ValueError("Niepoprawny nadawca")
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("Niepoprawny odbiorca")
        if sender == recipient:
            raise ValueError("Nadawca i odbiorca nie mogą być tacy sami")
        if sender != "0" and self.get_balance(sender) < amount:
            raise ValueError("Brak wystarczających środków na koncie")

        self.current_transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )
        return self.last_block["index"] + 1

    def proof_of_work(self, block):
        block["nonce"] = 0
        computed_hash = self.hash(block)
        while not computed_hash.startswith("0" * self.difficulty):
            block["nonce"] += 1
            computed_hash = self.hash(block)
        return computed_hash

    def mine(self, miner_address):
        reward = {"sender": "0", "recipient": miner_address, "amount": 1}
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": [reward] + self.current_transactions,
            "nonce": 0,
            "previous_hash": self.hash(self.last_block),
        }
        self.proof_of_work(block)
        self.current_transactions = []
        self.chain.append(block)
        return block