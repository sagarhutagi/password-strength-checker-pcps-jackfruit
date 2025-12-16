import wx
import hashlib
import requests
import re
import threading

# --- SAI (API Security) ---
class SecurityAPI:
    @staticmethod
    def check_breach(password):
        try:
            sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = sha1pass[:5], sha1pass[5:]
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            res = requests.get(url, timeout=3)
            if res.status_code == 200:
                hashes = (line.split(':') for line in res.text.splitlines())
                for h, count in hashes:
                    if h == suffix: return int(count)
            return 0
        except:
            return -1

# --- SACHCHIT (Core Logic) ---
class PasswordUtils:
    @staticmethod
    def get_score(password):
        score = 0
        feedback = {'good': [], 'bad': []}
        
        # Length Check
        if len(password) >= 12: 
            score += 3
            feedback['good'].append("Excellent length (12+ chars)")
        elif len(password) >= 8: 
            score += 2
            feedback['good'].append("Good length")
        else: 
            feedback['bad'].append("Too short (use 8+ chars)")

        # Pattern Checks
        if re.search(r'[a-z]', password): 
            score += 1
            feedback['good'].append("Contains lowercase")
        else: 
            feedback['bad'].append("Add lowercase letters")

        if re.search(r'[A-Z]', password): 
            score += 1
            feedback['good'].append("Contains uppercase")
        else: 
            feedback['bad'].append("Add uppercase letters")

        if re.search(r'[0-9]', password): 
            score += 1
            feedback['good'].append("Contains numbers")
        else: 
            feedback['bad'].append("Add numbers")

        if re.search(r'[\W_]', password): 
            score += 2
            feedback['good'].append("Contains special characters")
        else: 
            feedback['bad'].append("Add special characters (!@#)")

        return min(8, score), feedback

# --- SAGAR ---
class AppWindow(wx.Frame):
    def __init__(self):
        super().__init__(None, title='PESU Security Audit', size=(500, 650))
        self.SetBackgroundColour(wx.Colour(250, 250, 250))
        self.init_ui()
        self.Center()

    def init_ui(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        title = wx.StaticText(panel, label="Password & Breach Checker")
        title.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(title, 0, wx.ALL | wx.CENTER, 20)

        # Input Area
        self.hbox_pass = wx.BoxSizer(wx.HORIZONTAL)
        self.txt_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD, size=(250, 30))
        self.hbox_pass.Add(self.txt_pass, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
        
        self.chk_show = wx.CheckBox(panel, label="Show")
        self.chk_show.Bind(wx.EVT_CHECKBOX, self.on_toggle_show)
        self.hbox_pass.Add(self.chk_show, 0, wx.ALIGN_CENTER_VERTICAL)
        
        vbox.Add(self.hbox_pass, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)

        # Button
        self.btn_check = wx.Button(panel, label="Analyze Security", size=(160, 40))
        self.btn_check.Bind(wx.EVT_BUTTON, self.on_check)
        vbox.Add(self.btn_check, 0, wx.ALL | wx.CENTER, 10)

        # Status Label
        self.lbl_status = wx.StaticText(panel, label="Ready")
        vbox.Add(self.lbl_status, 0, wx.ALL | wx.CENTER, 5)

        # Score Label (ADDED HERE)
        self.lbl_score = wx.StaticText(panel, label="Rating: Waiting...")
        self.lbl_score.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(self.lbl_score, 0, wx.ALL | wx.CENTER, 5)

        # Gauge (Out of 8)
        self.gauge = wx.Gauge(panel, range=8, size=(400, 15))
        vbox.Add(self.gauge, 0, wx.ALL | wx.CENTER, 15)

        # Feedback Text Box
        self.txt_log = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2, size=(420, 250))
        vbox.Add(self.txt_log, 1, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(vbox)

    def on_toggle_show(self, event):
        val = self.txt_pass.GetValue()
        style = 0 if self.chk_show.GetValue() else wx.TE_PASSWORD
        new_txt = wx.TextCtrl(self.txt_pass.GetParent(), value=val, style=style, size=(250, 30))
        self.hbox_pass.Replace(self.txt_pass, new_txt)
        self.txt_pass.Destroy()
        self.txt_pass = new_txt
        self.hbox_pass.Layout()

# --- PRADYUN ---

    def on_check(self, event):
        password = self.txt_pass.GetValue()
        if not password: return

        self.lbl_status.SetLabel("Checking Database...")
        self.lbl_status.SetForegroundColour(wx.BLUE)
        self.btn_check.Disable()
        threading.Thread(target=self.process_logic, args=(password,), daemon=True).start()

    def process_logic(self, password):
        breaches = SecurityAPI.check_breach(password)
        score, feedback = PasswordUtils.get_score(password)
        wx.CallAfter(self.update_ui, score, feedback, breaches)

    def update_ui(self, score, feedback, breaches):
        self.btn_check.Enable()
        self.txt_log.Clear()
        
        # 1. API Results
        if breaches > 0:
            score = 0 # Fail immediately
            self.lbl_status.SetLabel(f"⚠️ LEAKED {breaches} TIMES")
            self.lbl_status.SetForegroundColour(wx.RED)
            self.txt_log.SetDefaultStyle(wx.TextAttr(wx.RED))
            self.txt_log.AppendText(f"CRITICAL WARNING: This password appears in {breaches} data breaches.\n\n")
        elif breaches == 0:
            self.lbl_status.SetLabel("✅ Safe (Not in public breaches)")
            self.lbl_status.SetForegroundColour(wx.Colour(0, 100, 0))
        else:
            self.lbl_status.SetLabel("⚠️ API Offline")
            self.lbl_status.SetForegroundColour(wx.Colour(200, 100, 0))

        self.gauge.SetValue(score)

        # 2. Update Score Text (ADDED HERE)
        if score <= 2: rating, color = "Very Weak", wx.RED
        elif score <= 4: rating, color = "Weak", wx.Colour(255, 140, 0) # Orange
        elif score <= 6: rating, color = "Medium", wx.Colour(200, 200, 0) # Yellow
        else: rating, color = "Strong", wx.Colour(0, 128, 0) # Green

        self.lbl_score.SetLabel(f"Rating: {rating} ({score}/8)")
        self.lbl_score.SetForegroundColour(color)
        
        # 3. Display "Good Stuff" (Green)
        if feedback['good']:
            self.txt_log.SetDefaultStyle(wx.TextAttr(wx.Colour(0, 100, 0))) # Dark Green
            self.txt_log.AppendText("✅ GOOD STUFF:\n")
            for item in feedback['good']:
                self.txt_log.AppendText(f" + {item}\n")
            self.txt_log.AppendText("\n")

        # 4. Display "Improvements" (Red/Orange)
        if feedback['bad']:
            self.txt_log.SetDefaultStyle(wx.TextAttr(wx.Colour(200, 0, 0))) # Dark Red
            self.txt_log.AppendText("❌ IMPROVEMENTS:\n")
            for item in feedback['bad']:
                self.txt_log.AppendText(f" - {item}\n")

if __name__ == '__main__':
    app = wx.App()
    frame = AppWindow()
    frame.Show()
    app.MainLoop()
