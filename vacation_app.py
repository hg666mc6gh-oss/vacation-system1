import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from datetime import datetime, date
import calendar
import random
import pandas as pd

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

# ---------- COLORS ----------
def color(name):
    random.seed(name)
    return f"#{random.randint(80,200):02x}{random.randint(80,200):02x}{random.randint(80,200):02x}"

RED = "#ff4d4d"

# ---------- DATE ----------
def parse(d):
    return datetime.strptime(d, "%d.%m.%Y")

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
        messagebox.showerror("Ошибка", "Уже есть")
        return

    data["employees"].append(name)
    save_data(data)
    refresh()

def delete_emp():
    data = load_data()

    sel = emp_listbox.curselection()
    if not sel:
        return

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
        messagebox.showerror("Ошибка", "Выбери сотрудника")
        return

    try:
        ds = parse(s)
        de = parse(e)
    except:
        messagebox.showerror("Ошибка", "DD.MM.YYYY")
        return

    if de < ds:
        messagebox.showerror("Ошибка", "Дата ошибки")
        return

    if overlap(data, name, s, e):
        messagebox.showerror("Ошибка", "Пересечение")
        return

    days = (de - ds).days + 1

    if used_days(data, name) + days > LIMIT:
        messagebox.showerror("Ошибка", "Лимит 28")
        return

    data["vacations"].append({
        "name": name,
        "start": s,
        "end": e,
        "days": days
    })

    save_data(data)
    refresh()

# ---------- EXCEL ----------
def export_excel():
    data = load_data()

    if not data["vacations"]:
        messagebox.showinfo("Info", "Нет данных")
        return

    df = pd.DataFrame(data["vacations"])

    path = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if path:
        df.to_excel(path, index=False)
        messagebox.showinfo("OK", "Готово")

# ---------- EMP FILTER ----------
def get_selected_employees():
    sel = emp_listbox.curselection()
    data = load_data()

    if not sel:
        return data["employees"]

    return [data["employees"][i] for i in sel]

# ---------- CALENDAR ----------
def draw():
    for w in cal_frame.winfo_children():
        w.destroy()

    data = load_data()

    try:
        y = int(year.get())
    except:
        y = date.today().year

    selected = get_selected_employees()

    tk.Label(cal_frame, text=f"{y} ENTERPRISE FIXED", font=("Arial", 18, "bold")).pack()

    grid = tk.Frame(cal_frame)
    grid.pack()

    for m in range(1, 13):
        mf = tk.Frame(grid, bd=1, relief="solid")
        mf.grid(row=(m-1)//4, column=(m-1)%4, padx=3, pady=3)

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

                names = []

                for v in data["vacations"]:
                    if v["name"] not in selected:
                        continue

                    s = parse(v["start"]).date()
                    e = parse(v["end"]).date()

                    if s <= cur <= e:
                        names.append(v["name"])

                if len(names) > 1:
                    bg = RED
                elif len(names) == 1:
                    bg = color(names[0])
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
root.title("HR ENTERPRISE FIXED ULTIMATE")
root.geometry("1200x850")

emp_entry = tk.Entry(root)
emp_entry.pack()

tk.Button(root, text="Добавить", command=add_emp).pack()
tk.Button(root, text="Удалить", command=delete_emp).pack()

emp_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=6)
emp_listbox.pack()

combo = ttk.Combobox(root)
combo.pack()

start = tk.Entry(root)
end = tk.Entry(root)

start.pack()
end.pack()

tk.Button(root, text="Добавить отпуск", command=add_vac).pack()

year = tk.StringVar(value=str(date.today().year))
tk.Entry(root, textvariable=year).pack()

tk.Button(root, text="Обновить", command=draw).pack()
tk.Button(root, text="Excel", command=export_excel).pack()

cal_frame = tk.Frame(root)
cal_frame.pack(fill="both", expand=True)

refresh()
root.mainloop()
