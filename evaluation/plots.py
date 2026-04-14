from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "paper"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("default")
plt.rcParams.update(
    {
        "font.size": 12,
        "font.family": "serif",
        "axes.labelsize": 14,
        "axes.titlesize": 16,
        "figure.titlesize": 18,
    }
)


def plot_ablation_study() -> None:
    data = {
        "Configuration": ["Full GEM-LLM", "W/O SMT Verification", "W/O Global Context"],
        "EDR (%)": [28.5, 31.2, 8.4],
        "Precision (%)": [98.0, 58.0, 96.5],
    }
    df = pd.DataFrame(data)
    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.bar(df["Configuration"], df["EDR (%)"], alpha=0.7, label="EDR (%)")
    ax1.set_ylabel("Equivalence Detection Rate (EDR %)", fontweight="bold")
    ax1.set_ylim(0, 45)

    ax2 = ax1.twinx()
    ax2.plot(df["Configuration"], df["Precision (%)"], marker="D", markersize=10, linewidth=2.5, label="Precision (%)")
    ax2.set_ylabel("Precision (%)", fontweight="bold")
    ax2.set_ylim(40, 105)

    plt.title("Ablation Study: Component Impact")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "ablation_study.png", dpi=300)
    plt.close(fig)


def plot_sensitivity_analysis() -> None:
    temp = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    precision = np.array([98.5, 98.0, 95.0, 82.0, 68.0, 55.0])

    fig = plt.figure(figsize=(8, 5))
    plt.plot(temp, precision, marker="o", linewidth=2)
    plt.axvline(0.2, linestyle="--", label="Optimal tau=0.2")
    plt.xlabel("LLM Temperature (tau)")
    plt.ylabel("Precision (%)")
    plt.title("Sensitivity Analysis: Impact of Temperature")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "sensitivity_analysis.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    plot_ablation_study()
    plot_sensitivity_analysis()
    print(f">>> All paper figures generated in {OUTPUT_DIR}")
