import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import time
import json
import os
import subprocess
import threading
import sys
import winsound  # Windows only sound library

# --- CONFIGURATION & AESTHETICS ---
COLORS = {
    'bg_primary': '#006400',    # Dark Calculator Green
    'bg_display': '#002800',    # Almost Black Green
    'text_lcd':   '#00FF00',    # Bright Green LCD
    'text_label': '#00AA00',    # Dimmer Green
    'btn_face':   '#008000',    # Medium Green
    'btn_text':   '#FFFFFF',    # White Text
    'alert':      '#FF0000'     # Red for alarm
}

FONT_LCD = ("Consolas", 24, "bold")
FONT_UI = ("Segoe UI", 10, "bold")
FONT_BTN = ("Segoe UI", 9, "bold")

DATA_FILE = os.path.join(os.getenv('APPDATA'), 'TriggerTimer', 'timers.json')

class TriggerTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trigger Timer x86")
        self.root.geometry("450x600")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.resizable(False, False)
        
        # Data Store
        self.timers = [] # List of dicts
        self.ensure_data_dir()
        
        # UI Setup
        self.setup_header()
        self.setup_display_area()
        self.setup_controls()
        self.setup_statusbar()
        
        # Load Data
        self.load_timers()
        self.refresh_timer_list()
        
        # Start Clock Loop
        self.root.after(1000, self.tick)

        # Admin Warning (Once per session)
        self.show_admin_warning()

    def ensure_data_dir(self):
        directory = os.path.dirname(DATA_FILE)
        if not os.path.exists(directory):
            os.makedirs(directory)

    def show_admin_warning(self):
        msg = ("ADMINISTRATOR PRIVILEGES NOTE:\n\n"
               "Some system commands (like shutdown) require this app to be "
               "run as Administrator.\n\n"
               "If commands fail, restart this app with elevated privileges.")
        messagebox.showinfo("System Check", msg)

    # --- UI CONSTRUCTION ---
    def setup_header(self):
        header_frame = tk.Frame(self.root, bg=COLORS['bg_primary'], pady=10)
        header_frame.pack(fill='x')
        
        lbl_title = tk.Label(header_frame, text="TRIGGER TIMER", 
                             font=("Impact", 18, "italic"),
                             bg=COLORS['bg_primary'], fg="white")
        lbl_title.pack()
        
        lbl_sub = tk.Label(header_frame, text="PYTHON x86 EDITION", 
                           font=("Arial", 8),
                           bg=COLORS['bg_primary'], fg=COLORS['text_label'])
        lbl_sub.pack()

    def setup_display_area(self):
        self.display_frame = tk.Frame(self.root, bg=COLORS['bg_display'], 
                                      bd=4, relief="sunken")
        self.display_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        self.timer_container = tk.Frame(self.display_frame, bg=COLORS['bg_display'])
        self.timer_container.pack(fill='both', expand=True)

    def setup_controls(self):
        btn_frame = tk.Frame(self.root, bg=COLORS['bg_primary'], pady=15)
        btn_frame.pack(fill='x', padx=20)
        
        btn_add = tk.Button(btn_frame, text="+ ADD TIMER", 
                            bg=COLORS['btn_face'], fg=COLORS['btn_text'],
                            font=FONT_BTN, relief="raised", bd=3,
                            command=self.open_add_dialog)
        btn_add.pack(fill='x', ipady=5)

    def setup_statusbar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        lbl_status = tk.Label(self.root, textvariable=self.status_var,
                              bg=COLORS['bg_display'], fg=COLORS['text_lcd'],
                              font=("Consolas", 8), anchor='w')
        lbl_status.pack(fill='x', side='bottom')

    # --- LOGIC ---
    def tick(self):
        active_count = 0
        needs_save = False
        
        for timer in self.timers:
            if timer['running'] and timer['remaining'] > 0:
                timer['remaining'] -= 1
                active_count += 1
                
                if timer['remaining'] <= 0:
                    self.trigger_alarm(timer)
                    timer['running'] = False
                    needs_save = True
        
        self.status_var.set(f"Active Timers: {active_count} | System Ready")
        self.refresh_timer_ui_values()
        
        if needs_save:
            self.save_timers()
            self.refresh_timer_list()
            
        self.root.after(1000, self.tick)

    def trigger_alarm(self, timer):
        threading.Thread(target=lambda: winsound.Beep(800, 500)).start()
        self.execute_command(timer['command'])

    # --- UPDATED EXECUTION CODE ---
    def execute_command(self, cmd_str):
        def run():
            try:
                subprocess.Popen(["cmd.exe", "/k", cmd_str])
                print(f"Executed: {cmd_str}")
            except Exception as e:
                print(f"Error: {e}")
                
        threading.Thread(target=run).start()

    # --- DIALOGS & ACTIONS ---
    def open_add_dialog(self):
        name = simpledialog.askstring("New Timer", "Timer Name:")
        if not name: return
        
        duration_str = simpledialog.askstring("New Timer", "Duration (HH:MM:SS):", initialvalue="00:05:00")
        if not duration_str: return
        
        try:
            h, m, s = map(int, duration_str.split(':'))
            total_seconds = h * 3600 + m * 60 + s
        except ValueError:
            messagebox.showerror("Error", "Invalid format. Use HH:MM:SS")
            return

        cmd = simpledialog.askstring("Action", "CMD Command:", initialvalue="echo Timer Complete")
        if not cmd: return

        new_timer = {
            'id': int(time.time() * 1000),
            'name': name,
            'duration': total_seconds,
            'remaining': total_seconds,
            'command': cmd,
            'running': False
        }
        
        self.timers.append(new_timer)
        self.save_timers()
        self.refresh_timer_list()

    def toggle_timer(self, timer_id):
        for t in self.timers:
            if t['id'] == timer_id:
                if t['remaining'] == 0:
                    t['remaining'] = t['duration']
                t['running'] = not t['running']
        self.save_timers()
        self.refresh_timer_list()

    def delete_timer(self, timer_id):
        self.timers = [t for t in self.timers if t['id'] != timer_id]
        self.save_timers()
        self.refresh_timer_list()

    # --- RENDERING ---
    def refresh_timer_list(self):
        for widget in self.timer_container.winfo_children():
            widget.destroy()

        for t in self.timers:
            frame = tk.Frame(self.timer_container, bg=COLORS['bg_display'], 
                             bd=1, relief="raised", pady=5)
            frame.pack(fill='x', pady=2)
            
            info_frame = tk.Frame(frame, bg=COLORS['bg_display'])
            info_frame.pack(side='left', padx=10)
            
            name_lbl = tk.Label(info_frame, text=t['name'], 
                                fg=COLORS['text_label'], bg=COLORS['bg_display'],
                                font=("Segoe UI", 8, "bold"))
            name_lbl.pack(anchor='w')
            
            time_str = time.strftime('%H:%M:%S', time.gmtime(t['remaining']))
            fg_color = COLORS['alert'] if t['remaining'] == 0 else COLORS['text_lcd']
            
            lcd = tk.Label(info_frame, text=time_str, 
                           fg=fg_color, bg=COLORS['bg_display'],
                           font=FONT_LCD)
            lcd.pack(anchor='w')

            t['ui_label'] = lcd 

            btn_frame = tk.Frame(frame, bg=COLORS['bg_display'])
            btn_frame.pack(side='right', padx=5)
            
            btn_txt = "PAUSE" if t['running'] else ("RESET" if t['remaining'] == 0 else "START")
            tk.Button(btn_frame, text=btn_txt, width=6,
                      command=lambda i=t['id']: self.toggle_timer(i)).pack(side='left', padx=2)
            
            tk.Button(btn_frame, text="X", bg='#800000', fg='white', width=3,
                      command=lambda i=t['id']: self.delete_timer(i)).pack(side='left')

    def refresh_timer_ui_values(self):
        for t in self.timers:
            if 'ui_label' in t and t['ui_label'].winfo_exists():
                time_str = time.strftime('%H:%M:%S', time.gmtime(t['remaining']))
                t['ui_label'].config(text=time_str)
                
                if t['remaining'] == 0:
                    t['ui_label'].config(fg=COLORS['alert'])
                else:
                    t['ui_label'].config(fg=COLORS['text_lcd'])

    # --- PERSISTENCE ---
    def save_timers(self):
        clean_timers = []
        for t in self.timers:
            copy = t.copy()
            if 'ui_label' in copy: del copy['ui_label']
            clean_timers.append(copy)
            
        with open(DATA_FILE, 'w') as f:
            json.dump(clean_timers, f)

    def load_timers(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                self.timers = json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    app = TriggerTimerApp(root)
    root.mainloop()
