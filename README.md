# 🛡️ Advanced Password Strength & Breach Analyzer

### UE25CS151A - Python Mini Project (PES University)

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![GUI](https://img.shields.io/badge/Interface-Tkinter-orange)
![Security](https://img.shields.io/badge/Security-SHA1%20Hashing-green)

## 📌 Overview
This project is a sophisticated **Password Security Audit Tool** developed as part of the First Year Python Course. Unlike standard checkers that only measure length, this tool performs a **3-layer analysis**:
1.  **Complexity:** Checks for character variety (Upper/Lower/Numbers/Symbols).
2.  **Behavioral Patterns:** Detects human-prone weaknesses like keyboard sequences (`abc`, `123`) and repetitions (`aaa`).
3.  **Live Breach Detection:** Integrates with the **Have I Been Pwned API** to check if the password has actually been exposed in real-world data hacks.

---

## 🚀 Features
* **Live Breach Check:** instantly verifies if your password exists in a database of over 600 million leaked credentials.
* **Privacy-First:** Uses **k-Anonymity** and **SHA-1 Hashing**. The password *never* leaves the local machine.
* **Smart Pattern Recognition:** Identifies sequential weaknesses (e.g., `qwerty`, `123456`) using ASCII logic.
* **Interactive GUI:** Clean, responsive interface built with `tkinter` featuring dynamic progress bars and color-coded feedback.
* **Detailed Feedback:** Provides actionable advice on how to fix specific weaknesses (e.g., "Avoid sequences," "Add special characters").

---

## 📸 Screenshots

| Weak / Leaked Password 🔴 | Strong Password 🟢 |
|:-------------------------:|:------------------:|
| <img width="550" height="578" alt="image" src="https://github.com/user-attachments/assets/e2fb24c3-2f41-40b4-a647-d3fa23185f04" /> | <img width="552" height="581" alt="image" src="https://github.com/user-attachments/assets/a7d4e140-3019-4e84-9390-cfde2c5562ce" /> |

---

## 🛠️ Installation & Usage

### 1. Prerequisites
You need **Python 3.x** installed. The project uses the `requests` library for API communication.

```bash
pip install requests
