import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, date
import calendar
import random
import csv

FILE = "data.json"
LIMIT = 28

# ---------- DATA ----------
def load_data():
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "employees" not in data:
            data["employees"] = []
        if "vacations" not in data:
            data["vacations"] = []

        return data

    except:
        return {"employees": [], "vacations": []}

def save_data(data):
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ---------- COLOR ----------
def color(name):
    random.seed(name)
    return f"#{random.randint(80,200):02x}{random.randint(80,200):02x}{random.randint(80,200):02x}"

RED = "#ff4d4d"

# ---------- DATE SAFE ----------
def parse(d):
    try:
        return datetime.strptime(d, "%d.%m.%Y")
    except:
        return datetime.strptime(d, "%Y-%m-%d")

# ---------- LOGIC ----------
def used_days(data, name):
    return sum(v["days"] for v in data["vacations"] if v["name"] == name)

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
    refresh()

def delete_emp():
    data = load_data()

    sel = emp_listbox.curselection()
    for i in reversed(sel):
        name = data["employees"][i]
        data["employees"].remove(name)
        data["vacations"] = [v for v in data["vacations"] if v["name"] != name]

    save_data(data)
    refresh()

# ---------- VAC ----------
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
        messagebox.showerror("Ошибка", "Дата")
        return

    if de < ds:
        return

    if overlap(data, name, s, e):
        return

    days = (de - ds).days + 1

    if used_days(data, name) + days > LIMIT:
        return

    data["vacations"].append({
        "name": name,
        "start": s,
        "end": e,
        "days": days
    })

    save_data(data)
    refresh()

# ---------- CSV EXPORT (без pandas) ----------
def export_excel():
    data = load_data()

    path = filedialog.asksaveasfilename(defaultextension=".csv")
    if not path:
        return

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "start", "end", "days"])

        for v in data["vacations"]:
            writer.writerow([v["name"], v["start"], v["end"], v["days"]])

    messagebox.showinfo("OK", "CSV создан")

# ---------- CALENDAR ----------
def draw():
    for w in cal_frame.winfo_children():
        w.destroy()

    data = load_data()

    try:
        y = int(year.get())
    except:
        y = date.today().year

    selected = combo.get()

    tk.Label(cal_frame, text=f"{y} SAFE ENTERPRISE", font=("Arial", 18)).pack()

    grid = tk.Frame(cal_frame)
    grid.pack()

    for m in range(1, 13):
        mf = tk.Frame(grid, bd=1, relief="solid")
        mf.grid(row=(m-1)//4, column=(m-1)%4)

        tk.Label(mf, text=calendar.month_name[m]).pack()

        cal = calendar.monthcalendar(y, m)

        for week in cal:
            row = tk.Frame(mf)
            row.pack()

            for d in week:
                if d == 0:
                    tk.Label(row, text=" ", width=3).pack(side="left")
                    continue

                cur = date(y, m, d)

                count = 0

                for v in data["vacations"]:
                    if selected and v["name"] != selected:
                        continue

                    s = parse(v["start"]).date()
                    e = parse(v["end"]).date()

                    if s <= cur <= e:
                        count += 1

                if count > 1:
                    bg = RED
                elif count == 1:
                    bg = color(selected)
                else:
                    bg = "white"

                tk.Label(row, text=str(d), width=3, bg=bg, relief="ridge").pack(side="left")

# ---------- REFRESH ----------
def refresh():
    data = load_data()

    combo["values"] = data["employees"]

    emp_listbox.delete(0, tk.END)
    for e in data["employees"]:
        emp_listbox.insert(tk.END, e)

    draw()

# ---------- UI ----------
root = tk.Tk()
root.title("HR SAFE ENTERPRISE")
root.geometry("1100x800")

emp_entry = tk.Entry(root)
emp_entry.pack()

tk.Button(root, text="Add", command=add_emp).pack()
tk.Button(root, text="Del", command=delete_emp).pack()

emp_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE)
emp_listbox.pack()

combo = ttk.Combobox(root)
combo.pack()

start = tk.Entry(root)
end = tk.Entry(root)

start.pack()
end.pack()

tk.Button(root, text="Add vac", command=add_vac).pack()

year = tk.StringVar(value=str(date.today().year))
tk.Entry(root, textvariable=year).pack()

tk.Button(root, text="Refresh", command=draw).pack()
tk.Button(root, text="Export CSV", command=export_excel).pack()

cal_frame = tk.Frame(root)
cal_frame.pack(fill="both", expand=True)

refresh()
root.mainloop()
