from argparse import ArgumentParser
from uuid import uuid4
from flask import Flask, jsonify, request
from blockchain import Blockchain

app = Flask(__name__)
node_identifier = str(uuid4()).replace("-", "")
blockchain = Blockchain()


@app.get("/chain")
def full_chain():
    return jsonify({"chain": blockchain.chain, "length": len(blockchain.chain)}), 200


@app.get("/transactions/pending")
def pending_transactions():
    return jsonify({
        "pending_transactions": blockchain.current_transactions,
        "count": len(blockchain.current_transactions),
    }), 200


@app.get("/block/<int:index>")
def get_block(index):
    for block in blockchain.chain:
        if block["index"] == index:
            return jsonify({"block": block, "hash": blockchain.hash(block)}), 200
    return jsonify({"error": f"Blok o indeksie {index} nie istnieje"}), 404


@app.post("/transactions/new")
def new_transaction():
    if not request.is_json:
        return jsonify({"error": "Wymagany nagłówek Content-Type: application/json"}), 400

    values = request.get_json(silent=True)
    if values is None or not isinstance(values, dict):
        return jsonify({"error": "Niepoprawny format danych JSON"}), 400

    required = {"sender", "recipient", "amount"}
    if not required.issubset(values.keys()):
        return jsonify({"error": "Brak wymaganych pól: sender, recipient, amount"}), 400

    if set(values.keys()) != required:
        return jsonify({"error": "Wykryto dodatkowe, nieoczekiwane pola w żądaniu"}), 400

    try:
        index = blockchain.new_transaction(
            values["sender"], values["recipient"], values["amount"]
        )
        return jsonify({"message": f"Transakcja zostanie dodana do bloku {index}"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.post("/mine")
def mine():
    block = blockchain.mine(node_identifier)
    return jsonify({
        "message": "Wydobyto nowy blok",
        "block": block,
        "hash": blockchain.hash(block),
    }), 200


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", default=5000, type=int)
    args = parser.parse_args()
    app.run(host="127.0.0.1", port=args.port)