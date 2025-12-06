# ⏱️ Trigger Time — Multi-Timer Command Executor (Python)

Trigger Time is a simple but powerful Python script that lets you set multiple timers, each tied to its own command.  
When a timer runs out, **boom — the command executes automatically**. Perfect for automation, reminders, tasks, or just feeling like a hacker from a sci-fi movie.

---

## 🚀 Features
- Set **multiple timers** at once  
- Each timer can run a **different CMD command**  
- Runs independently using threads  
- Lightweight and easy to use  
- Perfect for Windows command automation

---

## 📦 Requirements
- Python 3.x  
- Windows OS (because it uses CMD commands)  

No extra libraries needed 

---

## 🛠️ How It Works
1. You run `trigger_time.py`
2. Script asks:
   - How many timers you want
   - Timer duration (in seconds)
   - The command to run when time is up
3. Each timer gets its own thread
4. When a timer finishes, your command executes through `os.system()`

---


