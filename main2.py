import hashlib
import json
from time import time
import copy


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
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Kwota musi być liczbą dodatnią")
        if not isinstance(sender, str) or not sender.strip():
            raise ValueError("Nadawca musi być niepustym ciągiem znaków")
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("Odbiorca musi być niepustym ciągiem znaków")
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
        reward = {"sender": "0", "recipient": miner_address, "amount": 1.0}
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

    def valid_chain(self, chain):
        for i in range(1, len(chain)):
            previous, block = chain[i - 1], chain[i]
            if block["previous_hash"] != self.hash(previous):
                return False
            if not self.hash(block).startswith("0" * self.difficulty):
                return False
        return True


if __name__ == "__main__":

    print("2.1: WYDOBYCIE BLOKÓW TESTOWYCH")
    bc_demo = Blockchain(difficulty=4)

    bc_demo.mine(miner_address="Alice")

    bc_demo.new_transaction("Alice", "Bob", 0.5)
    bc_demo.mine(miner_address="miner-1")

    bc_demo.new_transaction("Bob", "Carol", 0.2)
    bc_demo.mine(miner_address="miner-1")

    for block in bc_demo.chain:
        print(f"Blok {block['index']} | Nonce: {block['nonce']} | Hash: {bc_demo.hash(block)}")
    print("-" * 70)


    print("\n2.2: BADANIE WPŁYWU TRUDNOŚCi")

    print(f"{'Trudność':<10} | {'Średni nonce':<15} | {'Średni czas [s]':<15} | {'Wydajność [H/s]':<15}")
    print("-" * 65)

    for d in range(1, 7):
        test_bc = Blockchain(difficulty=d)

        blocks_to_mine = 1 if d == 6 else 5

        total_nonce = 0
        total_time = 0.0

        for _ in range(blocks_to_mine):
            test_bc.current_transactions = [{"sender": "A", "recipient": "B", "amount": 10}]
            block_data = {
                "index": len(test_bc.chain) + 1,
                "timestamp": time(),
                "transactions": test_bc.current_transactions,
                "nonce": 0,
                "previous_hash": test_bc.hash(test_bc.last_block),
            }
            start_t = time()
            test_bc.proof_of_work(block_data)
            duration = time() - start_t

            total_nonce += block_data["nonce"]
            total_time += duration

        avg_nonce = total_nonce / blocks_to_mine
        avg_time = total_time / blocks_to_mine if total_time > 0 else 0.0001
        speed = total_nonce / total_time if total_time > 0 else 0

        print(f"{d:<10} | {int(avg_nonce):<15} | {avg_time:<15.4f} | {int(speed):<15}")
    print("-" * 70)


    print("\n2.3: ATAK NA INTEGRALNOŚĆ ŁAŃCUCHA")
    attack_bc = Blockchain(difficulty=4)
    attack_bc.mine("miner")
    attack_bc.mine("miner")

    attack_bc.chain[1]["transactions"].append({"sender": "miner", "recipient": "Alice", "amount": 5.0})
    attack_bc.proof_of_work(attack_bc.chain[1])

    print(f"Stan przed atakiem: valid_chain() -> {attack_bc.valid_chain(attack_bc.chain)}")
    attack_bc.chain[1]["transactions"][-1]["amount"] = 500.0
    print(f"Po manipulacji kwotą: valid_chain() -> {attack_bc.valid_chain(attack_bc.chain)}")

    def simulate_attacker(blockchain, start_block_idx, diff_value):
        blockchain.difficulty = diff_value
        start_time = time()
        for i in range(start_block_idx, len(blockchain.chain)):
            if i > start_block_idx:
                blockchain.chain[i]["previous_hash"] = blockchain.hash(blockchain.chain[i - 1])
            blockchain.proof_of_work(blockchain.chain[i])
        return time() - start_time

    bc_copy4 = copy.deepcopy(attack_bc)
    time_d4 = simulate_attacker(bc_copy4, 1, 4)
    print(f"Czas potrzebny na sfałszowanie całego łańcucha (d=4): {time_d4:.4f} s")

    bc_copy5 = copy.deepcopy(attack_bc)
    time_d5 = simulate_attacker(bc_copy5, 1, 5)
    print(f"Czas potrzebny na sfałszowanie całego łańcucha (d=5): {time_d5:.4f} s")
    print("-" * 70)


    print("\n2.4: TESTY SYSTEMU WALIDACJI TRANSAKCJI")
    valid_test = Blockchain(difficulty=1)
    valid_test.mine("Alice")
    print(f"Początkowe saldo Alice: {valid_test.get_balance('Alice')} BTC")

    try:
        print("Test 1: Kwota ujemna (-10)...")
        valid_test.new_transaction("Alice", "Bob", -10)
    except ValueError as e:
        print(f"Błąd walidacji: {e}")

    try:
        print("Test 2: Puste adresy...")
        valid_test.new_transaction(" ", "Bob", 1)
    except ValueError as e:
        print(f"Błąd walidacji: {e}")

    try:
        print("Test 3: Nadawca równy odbiorcy...")
        valid_test.new_transaction("Alice", "Alice", 0.1)
    except ValueError as e:
        print(f"Błąd walidacji: {e}")

    try:
        print("Test 4: Brak środków na koncie (próba wysłania 50 przy saldzie 1)...")
        valid_test.new_transaction("Alice", "Bob", 50)
    except ValueError as e:
        print(f"Błąd walidacji: {e}")