import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, date
import calendar
import random

FILE = "data.json"
LIMIT = 28

# ---------- DATA ----------
def load_data():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"employees": [], "vacations": []}

def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- SAFE PARSE ----------
def parse(d):
    if not d:
        return None
    try:
        return datetime.strptime(d, "%d.%m.%Y")
    except:
        try:
            return datetime.strptime(d, "%Y-%m-%d")
        except:
            return None

# ---------- COLORS ----------
def color(name):
    random.seed(name)
    return f"#{random.randint(90,210):02x}{random.randint(90,210):02x}{random.randint(90,210):02x}"

RED = "#ff4d4d"

# ---------- LOGIC ----------
def overlap(data, name, s, e):
    s1 = parse(s)
    e1 = parse(e)
    if not s1 or not e1:
        return False

    s1 = s1.date()
    e1 = e1.date()

    for v in data["vacations"]:
        if v["name"] == name:
            s2 = parse(v["start"]).date()
            e2 = parse(v["end"]).date()

            if s1 <= e2 and e1 >= s2:
                return True
    return False

# ---------- EMP ----------
def add_emp():
    data = load_data()
    name = emp_entry.get().strip()

    if not name:
        return

    if name in data["employees"]:
        return

    data["employees"].append(name)
    save_data(data)
    refresh_employees()

def delete_emp():
    data = load_data()

    for i in reversed(emp_listbox.curselection()):
        name = data["employees"][i]
        data["employees"].remove(name)
        data["vacations"] = [v for v in data["vacations"] if v["name"] != name]

    save_data(data)
    refresh_employees()
    refresh_calendar()

# ---------- VAC ----------
def add_vac():
    data = load_data()

    name = combo.get()
    s = start.get()
    e = end.get()

    if name not in data["employees"]:
        return

    ds = parse(s)
    de = parse(e)

    if not ds or not de:
        return

    if de < ds:
        return

    if overlap(data, name, s, e):
        messagebox.showwarning("Конфликт", "Пересечение отпусков")
        return

    days = (de - ds).days + 1

    data["vacations"].append({
        "name": name,
        "start": s,
        "end": e,
        "days": days
    })

    save_data(data)
    refresh_calendar()

# ---------- CALENDAR (OPTIMIZED) ----------
def refresh_calendar():
    for w in cal_inner.winfo_children():
        w.destroy()

    data = load_data()

    try:
        y = int(year.get())
    except:
        y = date.today().year

    tk.Label(cal_inner, text=f"📅 {y}", font=("Segoe UI", 18, "bold")).pack()

    grid = tk.Frame(cal_inner)
    grid.pack()

    for m in range(1, 13):
        box = tk.LabelFrame(grid, text=calendar.month_name[m])
        box.grid(row=(m-1)//4, column=(m-1)%4, padx=6, pady=6)

        cal = calendar.monthcalendar(y, m)

        for week in cal:
            row = tk.Frame(box)
            row.pack()

            for d in week:
                if d == 0:
                    tk.Label(row, text="   ").pack(side="left")
                    continue

                cur = date(y, m, d)

                names = []

                for v in data["vacations"]:
                    s = parse(v["start"])
                    e = parse(v["end"])
                    if not s or not e:
                        continue

                    s = s.date()
                    e = e.date()

                    if s <= cur <= e:
                        names.append(v["name"])

                if len(names) > 1:
                    bg = RED
                elif len(names) == 1:
                    bg = color(names[0])
                else:
                    bg = "white"

                tk.Label(row, text=str(d), width=3, bg=bg).pack(side="left")

# ---------- EMP REFRESH ----------
def refresh_employees():
    data = load_data()

    combo["values"] = data["employees"]

    emp_listbox.delete(0, tk.END)
    for e in data["employees"]:
        emp_listbox.insert(tk.END, e)

    refresh_calendar()

# ---------- UI ----------
root = tk.Tk()
root.title("HR ENTERPRISE OPTIMIZED")
root.geometry("1200x850")

# EMP
emp_entry = tk.Entry(root)
emp_entry.pack()

tk.Button(root, text="Добавить", command=add_emp).pack()
tk.Button(root, text="Удалить", command=delete_emp).pack()

emp_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
emp_listbox.pack()

# VAC
combo = ttk.Combobox(root)
combo.pack()

start = tk.Entry(root)
start.pack()

end = tk.Entry(root)
end.pack()

tk.Button(root, text="Добавить отпуск", command=add_vac).pack()

# YEAR
year = tk.StringVar(value=str(date.today().year))
tk.Entry(root, textvariable=year).pack()

tk.Button(root, text="Обновить", command=refresh_calendar).pack()

# CALENDAR
cal_inner = tk.Frame(root)
cal_inner.pack(fill="both", expand=True)

refresh_employees()
root.mainloop()
