import matplotlib.pyplot as plt
import io
import base64

x_difficulty = [1, 2, 3, 4, 5, 6]

y_teoria = [16, 223, 4596, 47205, 1136743, 50486879]

y_komputer = [0.0001, 0.0010, 0.0212, 0.2109, 8.3638, 328.3615]

plt.figure(figsize=(8, 5))

plt.plot(x_difficulty, y_teoria, label="Wartości teoretyczne ($16^d$)", color="blue", linestyle="--", marker="o")
plt.scatter(x_difficulty, y_komputer, label="Wyniki eksperymentalne (Średni nonce)", color="red", zorder=5, s=80)

plt.yscale("log")

plt.xlabel("Trudność ($d$)", fontsize=11)
plt.ylabel("Liczba prób / Wartość nonce (skala logarytmiczna)", fontsize=11)
plt.title("Porównanie teoretycznej liczby prób z wynikami eksperymentalnymi", fontsize=12, fontweight="bold")
plt.grid(True, which="both", linestyle=":", alpha=0.6)
plt.legend(fontsize=10)

plt.show()