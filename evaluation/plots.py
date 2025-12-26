import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set Journal Style (Q1 Standards)
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.size': 12, 'font.family': 'serif',
    'axes.labelsize': 14, 'axes.titlesize': 16,
    'figure.titlesize': 18
})

def plot_ablation_study():
    """Generates Figure 2: Ablation Results [cite: 334, 364]"""
    data = {
        'Configuration': ['Full GEM-LLM', 'W/O SMT Verification', 'W/O Global Context'],
        'EDR (%)': [28.5, 31.2, 8.4],
        'Precision (%)': [98.0, 58.0, 96.5]
    }
    df = pd.DataFrame(data)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # EDR Bars
    color_edr = '#2c3e50'
    ax1.bar(df['Configuration'], df['EDR (%)'], color=color_edr, alpha=0.7, label='EDR (%)')
    ax1.set_ylabel('Equivalence Detection Rate (EDR %)', fontweight='bold')
    ax1.set_ylim(0, 45)
    
    # Precision Line
    ax2 = ax1.twinx()
    color_prec = '#e74c3c'
    ax2.plot(df['Configuration'], df['Precision (%)'], marker='D', markersize=10, 
             color=color_prec, linewidth=2.5, label='Precision (%)')
    ax2.set_ylabel('Precision (%)', fontweight='bold', color=color_prec)
    ax2.set_ylim(40, 105)
    
    plt.title('Ablation Study: Component Impact')
    plt.savefig('paper/ablation_study.png', dpi=300)

def plot_sensitivity_analysis():
    """Generates Figure on Temperature Sensitivity [cite: 405]"""
    temp = np.array([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    precision = np.array([98.5, 98.0, 95.0, 82.0, 68.0, 55.0])
    
    plt.figure(figsize=(8, 5))
    plt.plot(temp, precision, marker='o', color='#2980b9', linewidth=2)
    plt.axvline(0.2, color='red', linestyle='--', label='Optimal tau=0.2')
    plt.xlabel('LLM Temperature (tau)')
    plt.ylabel('Precision (%)')
    plt.title('Sensitivity Analysis: Impact of Temperature')
    plt.legend()
    plt.savefig('paper/sensitivity_analysis.png', dpi=300)

if __name__ == "__main__":
    plot_ablation_study()
    plot_sensitivity_analysis()
    print(">>> All paper figures generated in /paper directory.")
