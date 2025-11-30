import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
import hashlib
import requests

class PasswordProject:
    def __init__(self, root):
        self.root = root
        self.root.title("PESU Mini Project - Advanced Security Audit")
        self.root.geometry("550x550")
        self.root.resizable(False, False)

        self.bg_color = "#f5f5f5"
        self.root.configure(bg=self.bg_color)
        
        # --- UI LAYOUT ---
        tk.Label(root, text="Password Strength & Breach Checker", 
                 font=("Arial", 16, "bold"), bg=self.bg_color).pack(pady=15)

        input_frame = tk.Frame(root, bg=self.bg_color)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Enter Password:", bg=self.bg_color, font=("Arial", 11)).grid(row=0, column=0, padx=5)
        
        self.pass_entry = ttk.Entry(input_frame, show="*", font=("Arial", 11), width=25)
        self.pass_entry.grid(row=0, column=1, padx=5)

        self.show_var = tk.IntVar()
        tk.Checkbutton(input_frame, text="Show", variable=self.show_var, 
                       command=self.toggle_password, bg=self.bg_color).grid(row=0, column=2, padx=5)

        ttk.Button(root, text="Analyze Security", command=self.run_analysis).pack(pady=10)

        # Status Label for API
        self.api_status = tk.Label(root, text="", bg=self.bg_color, fg="#666")
        self.api_status.pack()

        # Score & Progress
        self.score_label = tk.Label(root, text="Rating: Waiting...", font=("Arial", 12, "bold"), bg=self.bg_color)
        self.score_label.pack(pady=5)

        self.progress = ttk.Progressbar(root, length=400, mode='determinate', maximum=8)
        self.progress.pack(pady=5)

        # Feedback Text Box
        self.feedback_box = tk.Text(root, height=14, width=60, font=("Consolas", 10))
        self.feedback_box.pack(pady=15, padx=20)
        self.feedback_box.config(state="disabled")

    def toggle_password(self):
        if self.show_var.get():
            self.pass_entry.config(show="")
        else:
            self.pass_entry.config(show="*")

    def check_pwned_api(self, password):
        """Checks if password exists in data breaches using k-Anonymity."""
        try:
            # Hash password with SHA1
            sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = sha1pass[:5], sha1pass[5:]
            
            # Send only first 5 chars to API
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            res = requests.get(url, timeout=2)
            
            if res.status_code == 200:
                hashes = (line.split(':') for line in res.text.splitlines())
                for h, count in hashes:
                    if h == suffix:
                        return int(count) # Found match
            return 0 # Not found
        except:
            return -1 # Internet error

    def run_analysis(self):
        password = self.pass_entry.get()
        if not password:
            messagebox.showwarning("Error", "Enter a password first.")
            return

        self.api_status.config(text="Checking database...", fg="blue")
        self.root.update()

        # --- 1. YOUR ORIGINAL LOGIC ---
        score = 0
        feedback = {'positive': [], 'negative': []}

        # Length
        length = len(password)
        if length >= 12:
            score += 3
            feedback['positive'].append("Excellent length (12+ chars)")
        elif length >= 8:
            score += 2
            feedback['positive'].append("Good length (8-11 chars)")
        else:
            feedback['negative'].append("Too short (aim for 8+ chars)")

        # Regex Checks
        if re.search(r'[a-z]', password):
            score += 1
            feedback['positive'].append("Contains lowercase")
        else:
            feedback['negative'].append("Add lowercase letters")

        if re.search(r'[A-Z]', password):
            score += 1
            feedback['positive'].append("Contains uppercase")
        else:
            feedback['negative'].append("Add uppercase letters")

        if re.search(r'[0-9]', password):
            score += 1
            feedback['positive'].append("Contains numbers")
        else:
            feedback['negative'].append("Add numbers")

        if re.search(r'[\W_]', password):
            score += 2
            feedback['positive'].append("Contains special characters")
        else:
            feedback['negative'].append("Add special characters (!@#)")

        # Sequence Check (abc, 123)
        found_seq = False
        for i in range(len(password) - 2):
            p1, p2, p3 = password[i:i+3]
            if (p1.isalpha() and p2.isalpha() and p3.isalpha()) or \
               (p1.isdigit() and p2.isdigit() and p3.isdigit()):
                if (ord(p2) == ord(p1) + 1 and ord(p3) == ord(p2) + 1) or \
                   (ord(p2) == ord(p1) - 1 and ord(p3) == ord(p2) - 1):
                    score = max(0, score - 2)
                    if not found_seq:
                        feedback['negative'].append(f"Avoid sequences like '{p1}{p2}{p3}'")
                        found_seq = True

        # Repetition Check (aaa)
        found_rep = False
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                score = max(0, score - 2)
                if not found_rep:
                    feedback['negative'].append(f"Avoid repeating characters like '{password[i]*3}'")
                    found_rep = True
        
        # --- 2. API CHECK (The Override) ---
        breach_count = self.check_pwned_api(password)
        is_leaked = False
        
        if breach_count > 0:
            is_leaked = True
            score = 0 # Force score to 0
            self.api_status.config(text=f"⚠️ FOUND IN {breach_count} DATA BREACHES", fg="red")
        elif breach_count == 0:
            self.api_status.config(text="✅ Not found in public breaches", fg="green")
            feedback['positive'].append("Clean: Not found in hack databases")
        else:
            self.api_status.config(text="⚠️ Internet Error - Skipped API check", fg="#cc7a00")

        # --- 3. FINAL RESULTS ---
        score = max(0, score) # prevent negative
        
        if is_leaked:
            level = "COMPROMISED"
            color = "red"
        elif score <= 2:
            level = "Very Weak"
            color = "red"
        elif score <= 4:
            level = "Weak"
            color = "#ff9900"
        elif score <= 6:
            level = "Medium"
            color = "#cccc00"
        elif score <= 7:
            level = "Strong"
            color = "blue"
        else:
            level = "Very Strong"
            color = "green"

        self.score_label.config(text=f"Rating: {level} ({score}/8)", fg=color)
        self.progress['value'] = score

        self.feedback_box.config(state="normal")
        self.feedback_box.delete(1.0, tk.END)

        if is_leaked:
            self.feedback_box.insert(tk.END, "🚨 CRITICAL WARNING 🚨\n", "danger")
            self.feedback_box.insert(tk.END, f"This password has been exposed {breach_count} times.\n")
            self.feedback_box.insert(tk.END, "Hackers have this password. DO NOT USE IT.\n\n")

        if feedback['positive']:
            self.feedback_box.insert(tk.END, "✅ GOOD STUFF:\n")
            for item in feedback['positive']:
                self.feedback_box.insert(tk.END, f"  - {item}\n")
            self.feedback_box.insert(tk.END, "\n")
            
        if feedback['negative']:
            self.feedback_box.insert(tk.END, "❌ IMPROVEMENTS:\n")
            for item in feedback['negative']:
                self.feedback_box.insert(tk.END, f"  - {item}\n")

        self.feedback_box.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordProject(root)
    root.mainloop()