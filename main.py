import hashlib
import json
from time import time


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = {
            "index": 1,
            "timestamp": 0,
            "transactions": [],
            "nonce": 0,
            "previous_hash": "0" * 64
        }
        self.chain.append(genesis)

    @staticmethod
    def hash(block):
        # sort_keys=True gwarantuje deterministyczną kolejność pól
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, transactions):
        block = {
            "nonce": 0,  # <- po zamianie
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": transactions,
            "previous_hash": self.hash(self.last_block),
        }
        self.chain.append(block)
        return block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block["previous_hash"] != self.hash(previous_block):
                return False, current_block["index"]

        return True, None


if __name__ == "__main__":
    bc = Blockchain()

    bc.add_block(["Alice -> Bob: 5"])
    bc.add_block(["Bob -> Carol: 2"])


    bc.add_block(["Carol -> Alice: 3"])
    bc.add_block(["Bob -> Carol: 1"])
    bc.add_block(["Alice -> Bob: 7"])

    print("=== ZAWARTOŚĆ ŁAŃCUCHA BLOCKCHAIN ===")
    for block in bc.chain:
        print(json.dumps(block, indent=2, ensure_ascii=False))
        print("hash:", Blockchain.hash(block))
        print("-" * 70)

    #test integralności

    is_valid, error_block_index = bc.is_chain_valid()
    print(f"Czy łańcuch blockchain jest poprawny? -> {is_valid}")
    print(f"Numer pierwszego błędnego bloku: -> {error_block_index}")

    #ręczna modyfikacja
    bc.chain[1]["transactions"][0] = "Alice -> Bob: 500"
    print("-" * 60)

    #test po modyfikacji
    valid, err_idx = bc.is_chain_valid()
    print(f"Czy łańcuch nadal jest poprawny? -> {valid} (Wykryto błąd w bloku: {err_idx})")
    print("-" * 60)

    #nowy nadpis pętla i test
    for i in range(2, len(bc.chain)):
        bc.chain[i]["previous_hash"] = bc.hash(bc.chain[i - 1])

    valid, err_idx = bc.is_chain_valid()
    print(f"Czy po wielokrotnej 'naprawie' łańcuch jest poprawny? -> {valid}")
    print(f"Wykryto błąd w bloku: -> {err_idx}")
    print("-" * 60)

    #final
    index_ostatniego = len(bc.chain) - 1

    #zmiana transakcji w ostatnim bloku na fałszywą
    bc.chain[index_ostatniego]["transactions"] = ["PROBA OSZUSTWA"]

    #sprawdzenie wykrycia zmiany
    valid, err_idx = bc.is_chain_valid()
    print(f"Czy po mod. łańcuch jest poprawny? -> {valid}")
    print(f"Wykryto błąd w bloku: -> {err_idx}")
    print("-" * 60)