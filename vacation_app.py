import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime

DATA_FILE = "data.json"
ANNUAL_LIMIT = 28

# ---------- DATA ----------
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"employees": ["Иванов", "Петров", "Сидоров"], "vacations": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- LOGIC ----------
def calc_days(start, end):
    d1 = datetime.strptime(start, "%Y-%m-%d")
    d2 = datetime.strptime(end, "%Y-%m-%d")
    return (d2 - d1).days + 1

def used_days(data, name):
    return sum(v["days"] for v in data["vacations"] if v["name"] == name)

def overlap(data, name, start, end):
    ns = datetime.strptime(start, "%Y-%m-%d")
    ne = datetime.strptime(end, "%Y-%m-%d")

    for v in data["vacations"]:
        if v["name"] == name:
            s = datetime.strptime(v["start"], "%Y-%m-%d")
            e = datetime.strptime(v["end"], "%Y-%m-%d")
            if ns <= e and ne >= s:
                return True
    return False

# ---------- ACTIONS ----------
def refresh():
    data = load_data()
    tree.delete(*tree.get_children())

    for i, v in enumerate(data["vacations"]):
        tree.insert("", "end", iid=i, values=(
            v["name"], v["start"], v["end"], v["days"]
        ))

def add():
    data = load_data()

    name = combo.get()
    start = start_entry.get()
    end = end_entry.get()

    if not name or not start or not end:
        messagebox.showerror("Ошибка", "Заполни все поля")
        return

    if overlap(data, name, start, end):
        messagebox.showerror("Ошибка", "Пересечение отпусков")
        return

    days = calc_days(start, end)

    if used_days(data, name) + days > ANNUAL_LIMIT:
        messagebox.showerror("Ошибка", "Превышен лимит отпуска")
        return

    data["vacations"].append({
        "name": name,
        "start": start,
        "end": end,
        "days": days
    })

    save_data(data)
    refresh()

# ---------- UI ----------
root = tk.Tk()
root.title("Учёт отпусков")
root.geometry("750x500")

data = load_data()

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Сотрудник").grid(row=0, column=0)
tk.Label(frame, text="Начало (YYYY-MM-DD)").grid(row=0, column=1)
tk.Label(frame, text="Конец").grid(row=0, column=2)

combo = ttk.Combobox(frame, values=data["employees"])
combo.grid(row=1, column=0)

start_entry = tk.Entry(frame)
end_entry = tk.Entry(frame)

start_entry.grid(row=1, column=1)
end_entry.grid(row=1, column=2)

tk.Button(frame, text="Добавить", command=add).grid(row=1, column=3)

tree = ttk.Treeview(root, columns=("n","s","e","d"), show="headings")
tree.heading("n", text="Сотрудник")
tree.heading("s", text="Начало")
tree.heading("e", text="Конец")
tree.heading("d", text="Дней")

tree.pack(fill="both", expand=True)

refresh()
root.mainloop()
