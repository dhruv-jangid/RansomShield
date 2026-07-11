# 🛡️ RansomShield
### ML-Powered Ransomware Detection & Protection System

> An intelligent ransomware detection and protection system that combines Machine Learning, entropy analysis, honeypot monitoring, file behavior analysis, and real-time filesystem monitoring to proactively detect and prevent ransomware attacks.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-success)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

# 📌 Overview

RansomShield is an intelligent cybersecurity application developed to detect ransomware before large-scale file encryption occurs.

Unlike traditional signature-based antivirus software, RansomShield performs **behavior-based detection** using multiple independent security layers.

The system continuously monitors filesystem activity, analyzes file entropy, detects suspicious file extensions, observes abnormal process behavior, verifies file reputation, monitors honeypot files, and finally uses a trained Machine Learning model to classify ransomware behavior in real time.

The project was built to demonstrate how Artificial Intelligence can strengthen endpoint security through automated threat detection.

---

# 🚀 Key Features

✔ Real-Time File Monitoring

✔ Machine Learning-Based Detection

✔ Random Forest Classification

✔ Entropy Analysis

✔ SHA-256 File Hashing

✔ Honeypot File Monitoring

✔ Suspicious Extension Detection

✔ Behavioral File Analysis

✔ Process Monitoring

✔ Automatic Threat Reporting

✔ PDF Report Generation

✔ CSV Logging

✔ GUI Interface (Tkinter)

✔ Offline Detection

---

# 🏗️ System Architecture

```
                 User Files
                      │
                      ▼
        Real-Time Filesystem Monitor
             (Watchdog Observer)
                      │
                      ▼
          Multi-Layer Detection Engine
                      │
      ┌───────────────┼────────────────┐
      │               │                │
      ▼               ▼                ▼

 Entropy       Honeypot Monitor    Extension Scanner

      ▼               ▼                ▼

 Process Analysis   Reputation Check   SHA-256

              ▼
     Feature Extraction

              ▼

 Machine Learning Model
   (Random Forest)

              ▼

 Threat Classification

              ▼

 Alert + Logging + Reports
```

---

# 🔥 Problem Statement

Modern ransomware encrypts files within seconds.

Traditional antivirus software often relies on known malware signatures, making it ineffective against zero-day ransomware variants.

The objective of this project is to provide an intelligent endpoint protection system capable of detecting ransomware behavior before significant damage occurs.

---

# 💡 Proposed Solution

RansomShield combines Machine Learning with multiple heuristic detection techniques.

Instead of relying on a single detection method, the application performs layered security checks.

These include:

- Entropy Analysis
- Behavioral Analysis
- Honeypot Detection
- File Extension Monitoring
- Reputation Verification
- Machine Learning Classification

The combined score is used to determine whether a file or process is malicious.

---

# 🧠 Machine Learning Pipeline

### Algorithm

Random Forest Classifier

### Dataset

Custom ransomware behavioral dataset.

Contains multiple ransomware indicators including:

- File entropy
- File size
- Extension
- Encryption behavior
- File modification rate
- Honeypot interaction
- Process behavior

### Data Preprocessing

- Missing value handling
- Feature scaling
- Label encoding
- Dataset balancing

### Model Training

- Train-Test Split
- Feature Engineering
- Hyperparameter tuning
- Random Forest Training

### Performance

| Metric | Value |
|---------|--------|
| Accuracy | 95%+ |
| Precision | High |
| Recall | High |
| F1 Score | High |

---

# 🔐 Detection Layers

## Layer 1 — Entropy Detection

Encrypted files have significantly higher entropy.

The entropy detector calculates Shannon Entropy to determine whether a file appears encrypted.

---

## Layer 2 — Honeypot Detection

Fake files are strategically placed throughout monitored directories.

If these files are modified, the system immediately flags potential ransomware activity.

---

## Layer 3 — Extension Detection

Detects suspicious extensions such as

```
.locked
.encrypted
.crypted
```

---

## Layer 4 — Behavior Analysis

Monitors abnormal file activity including:

- Rapid file creation
- Multiple file modifications
- High write frequency
- Sudden extension changes

---

## Layer 5 — Machine Learning Classification

All extracted features are passed into a trained Random Forest classifier.

The classifier predicts whether the observed behavior is benign or malicious.

---

# 📂 Project Structure

```
RansomShield/

│

├── src/

│ ├── alert_manager.py

│ ├── backup_manager.py

│ ├── behavior.py

│ ├── dataset_collector.py

│ ├── entropy_detector.py

│ ├── extension_detector.py

│ ├── gui.py

│ ├── honeypot.py

│ ├── logger.py

│ ├── ml_detector.py

│ ├── monitor.py

│ ├── reputation_engine.py

│

├── data/

│

├── reports/

│

├── logs/

│

├── main.py

├── train_model.py

├── requirements.txt

└── README.md
```

---

# 🛠️ Tech Stack

### Programming Language

- Python

### Machine Learning

- Scikit-Learn
- Random Forest

### Monitoring

- Watchdog

### GUI

- Tkinter

### Reporting

- ReportLab

### Packaging

- PyInstaller

### Version Control

- Git
- GitHub

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/dhruv-jangid/RansomShield-ML-Ransomware-Detection.git
```

Move into the project

```bash
cd RansomShield-ML-Ransomware-Detection
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python main.py
```

---

# 📸 Screenshots

> Add screenshots here

- Home Screen
- Detection Alert
- PDF Report
- Monitoring Dashboard

---

# 📄 Report Generation

The application automatically generates:

- Security Reports
- Threat Logs
- CSV Analysis
- PDF Reports

---

# 🎯 Future Improvements

- Deep Learning Detection
- Cloud Threat Intelligence
- VirusTotal API Integration
- YARA Rule Detection
- Real-Time Email Alerts
- Docker Deployment
- Web Dashboard
- SIEM Integration
- Windows Service Support

---

# 👨‍💻 Author

**Dhruv Jangid**

B.Tech CSE (Cybersecurity & Forensics)

UPES, Dehradun

GitHub:
https://github.com/dhruv-jangid

LinkedIn:
https://linkedin.com/in/dhruvjangid-it

---

# ⭐ If you found this project useful, consider giving it a Star!
