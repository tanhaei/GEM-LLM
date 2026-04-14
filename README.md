# **GEM-LLM: Identifying Contextual Equivalent Mutants via LLMs**

**GEM-LLM** is a hybrid framework designed to solve the Equivalent Mutant Problem (EMP) in mutation testing. By combining the semantic reasoning power of Large Language Models (LLMs) with the formal rigor of SMT solvers, GEM-LLM identifies "Contextual Equivalence"—mutants that are functionally identical only when considering global program invariants and environmental constraints.

## **🚀 Key Features**

* **Global Invariant Extraction**: Uses inter-procedural program slicing to capture calling-context information.  
* **Neural-Formal Hybrid**: Bridges the gap between LLM reasoning and SMT-based formal verification (Z3).  
* **High Precision**: Achieves 98% precision in identifying equivalent mutants on the Defects4J benchmark.  
* **Model Agnostic**: Supports OpenAI (GPT-4o) and local deployments (Llama-3, Gemma 3) for privacy-sensitive environments.

## **📂 Repository Structure**

```
GEM-LLM/  
├── core/  
│   ├── slicer/             \# Java-based static analysis (Soot)  
│   ├── reasoning/          \# LLM Engine & CoT Prompting  
│   └── verification/       \# SMT Encoding & Z3 Solving logic  
├── data/  
│   ├── subjects/           \# Defects4J source projects (checkout here)  
│   └── outputs/            \# Raw JSON detection results  
├── evaluation/             \# Statistical analysis & plotting scripts  
├── scripts/                \# Automation & Setup scripts  
├── paper/                  \# Generated figures and LaTeX sources  
└── README.md
```

## **🛠️ Setup & Installation**

### **1\. Prerequisites**

* **Java JDK 1.8** (Required for Soot)  
* **Python 3.9+**  
* **Maven** (For building the Java slicer)  
* **Defects4J** (To checkout the benchmark projects)

### **2\. Installation**

Clone the repository and install dependencies:

```bash
git clone https://github.com/tanhaei/GEM-LLM.git  
cd GEM-LLM  
pip install -r requirements.txt
```

Optional local-model support requires installing Hugging Face runtime dependencies separately (for example `transformers` and a compatible backend such as `torch`).

Build the Java Slicer:

```bash
cd core/slicer  
mvn clean install  
cd ../..
```

### **3\. Environment Variables**

If using OpenAI, set your API key:

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## **🏃 Running Experiments**

### **Phase 1: Static Analysis**

Checkout a project from Defects4J and run the slicer:

```bash
defects4j checkout -p Lang -v 1b -w data/subjects/Lang_1b  
./scripts/run_slicer.sh data/subjects/Lang_1b Lang_1b data/outputs/Lang_1b_slice.json
```

### **Phase 2 & 3: Identification & Verification**

Run the reasoning engine and SMT solver:

```bash
python3 core/reasoning/engine.py --project Lang --version 1b --slice-file data/outputs/Lang_1b_slice.json
```

## **📊 Reproducibility**

To reproduce the figures and tables from the paper:
 
```bash
python3 evaluation/plots.py
```

This will generate the following figures in the paper/ directory:

* **Ablation Study**: Impact of Global Context and SMT.  
* **Performance Frontier**: EDR vs. Precision trade-off.  
* **Sensitivity Analysis**: Impact of LLM Temperature ($\\tau$).

## **📝 Citation**

If you use this work in your research, please cite:

## **⚖️ License**

This project is licensed under the **MIT License** \- see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.