import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, date
import calendar
import random

FILE = "data.json"
LIMIT = 28

# ---------------- DATA ----------------
def load_data():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"employees": [], "vacations": []}

def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------------- THEME ----------------
theme = {"dark": False}

def set_theme():
    if theme["dark"]:
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("Treeview", background="#2b2b2b", fieldbackground="#2b2b2b", foreground="white")
        root.configure(bg="#1e1e1e")
    else:
        style.configure("TLabel", background="#f4f4f4", foreground="black")
        style.configure("TFrame", background="#f4f4f4")
        style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
        root.configure(bg="#f4f4f4")

# ---------------- COLOR ----------------
def color(name):
    random.seed(name)
    return f"#{random.randint(90,210):02x}{random.randint(90,210):02x}{random.randint(90,210):02x}"

RED = "#ff4d4d"

# ---------------- DATE ----------------
def parse(d):
    return datetime.strptime(d, "%d.%m.%Y")

# ---------------- LOGIC ----------------
def overlap(data, name, s, e):
    s1 = parse(s).date()
    e1 = parse(e).date()

    for v in data["vacations"]:
        if v["name"] == name:
            s2 = parse(v["start"]).date()
            e2 = parse(v["end"]).date()
            if s1 <= e2 and e1 >= s2:
                return True
    return False

# ---------------- EMP ----------------
def add_emp():
    data = load_data()
    name = emp_entry.get().strip()

    if not name or name in data["employees"]:
        return

    data["employees"].append(name)
    save_data(data)
    refresh()

def delete_emp():
    data = load_data()

    for item in emp_tree.selection():
        name = emp_tree.item(item)["values"][0]
        data["employees"].remove(name)
        data["vacations"] = [v for v in data["vacations"] if v["name"] != name]

    save_data(data)
    refresh()

# ---------------- VAC ----------------
def add_vac():
    data = load_data()

    name = combo.get()
    s = start.get()
    e = end.get()

    if name not in data["employees"]:
        return

    try:
        ds = parse(s)
        de = parse(e)
    except:
        return

    if overlap(data, name, s, e):
        messagebox.showwarning("Конфликт", "Пересечение отпусков")
        return

    data["vacations"].append({
        "name": name,
        "start": s,
        "end": e,
        "days": (de - ds).days + 1
    })

    save_data(data)
    draw_calendar()

# ---------------- CALENDAR ----------------
def draw_calendar():
    for w in cal_frame.winfo_children():
        w.destroy()

    data = load_data()
    y = int(year.get())

    tk.Label(cal_frame, text=f"📅 {y}", font=("Arial", 16, "bold")).pack()

    grid = tk.Frame(cal_frame)
    grid.pack()

    for m in range(1, 13):
        box = tk.LabelFrame(grid, text=calendar.month_name[m])
        box.grid(row=(m-1)//4, column=(m-1)%4)

        cal = calendar.monthcalendar(y, m)

        for week in cal:
            row = tk.Frame(box)
            row.pack()

            for d in week:
                if d == 0:
                    tk.Label(row, text="  ").pack(side="left")
                    continue

                cur = date(y, m, d)
                names = []

                for v in data["vacations"]:
                    s = parse(v["start"]).date()
                    e = parse(v["end"]).date()
                    if s <= cur <= e:
                        names.append(v["name"])

                bg = RED if len(names) > 1 else (color(names[0]) if names else "white")

                tk.Label(row, text=str(d), width=3, bg=bg).pack(side="left")

# ---------------- EMP UPDATE ----------------
def refresh():
    data = load_data()

    combo["values"] = data["employees"]

    emp_tree.delete(*emp_tree.get_children())

    for e in data["employees"]:
        emp_tree.insert("", "end", values=(e,))

    draw_calendar()

# ---------------- UI ----------------
root = tk.Tk()
root.title("HR FINAL FIX")
root.geometry("1200x850")

style = ttk.Style()

tk.Button(root, text="🌙 Тема", command=lambda: toggle()).pack()

def toggle():
    theme["dark"] = not theme["dark"]
    set_theme()
    draw_calendar()

# EMP
emp_entry = tk.Entry(root)
emp_entry.pack()

tk.Button(root, text="Добавить", command=add_emp).pack()

emp_tree = ttk.Treeview(root, columns=("name"), show="headings", height=5)
emp_tree.heading("name", text="ФИО")
emp_tree.pack()

tk.Button(root, text="Удалить", command=delete_emp).pack()

# VAC
combo = ttk.Combobox(root)
combo.pack()

start = tk.Entry(root)
start.pack()

end = tk.Entry(root)
end.pack()

tk.Button(root, text="Добавить отпуск", command=add_vac).pack()

year = tk.StringVar(value=str(date.today().year))
tk.Entry(root, textvariable=year).pack()

tk.Button(root, text="Обновить", command=draw_calendar).pack()

cal_frame = tk.Frame(root)
cal_frame.pack(fill="both", expand=True)

set_theme()
refresh()
root.mainloop()
