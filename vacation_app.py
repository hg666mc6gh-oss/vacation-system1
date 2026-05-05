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

# ---------- COLORS ----------
def get_color(name):
    random.seed(name)
    r = random.randint(80, 200)
    g = random.randint(80, 200)
    b = random.randint(80, 200)
    return f"#{r:02x}{g:02x}{b:02x}"

# ---------- LOGIC ----------
def days_between(s, e):
    d1 = datetime.strptime(s, "%Y-%m-%d")
    d2 = datetime.strptime(e, "%Y-%m-%d")
    return (d2 - d1).days + 1

def used_days(data, name):
    return sum(v["days"] for v in data["vacations"] if v["name"] == name)

def overlap(data, name, s, e):
    s1 = datetime.strptime(s, "%Y-%m-%d").date()
    e1 = datetime.strptime(e, "%Y-%m-%d").date()

    for v in data["vacations"]:
        if v["name"] == name:
            s2 = datetime.strptime(v["start"], "%Y-%m-%d").date()
            e2 = datetime.strptime(v["end"], "%Y-%m-%d").date()

            if s1 <= e2 and e1 >= s2:
                return True
    return False

# ---------- EMPLOYEES ----------
def add_employee():
    data = load_data()
    name = emp_entry.get().strip()

    if not name:
        messagebox.showerror("Ошибка", "Введите имя сотрудника")
        return

    if name in data["employees"]:
        messagebox.showerror("Ошибка", "Сотрудник уже существует")
        return

    data["employees"].append(name)
    save_data(data)
    refresh()

def delete_employee():
    data = load_data()
    name = combo_emp.get()

    if name in data["employees"]:
        data["employees"].remove(name)
        data["vacations"] = [v for v in data["vacations"] if v["name"] != name]
        save_data(data)
        refresh()

# ---------- VACATION ----------
def add_vacation():
    data = load_data()

    name = combo_emp.get().strip()
    s = start_entry.get().strip()
    e = end_entry.get().strip()

    if name not in data["employees"]:
        messagebox.showerror("Ошибка", "Выбери сотрудника")
        return

    if not name or not s or not e:
        messagebox.showerror("Ошибка", "Заполни все поля")
        return

    try:
        ds = datetime.strptime(s, "%Y-%m-%d")
        de = datetime.strptime(e, "%Y-%m-%d")
    except:
        messagebox.showerror("Ошибка", "Формат даты: YYYY-MM-DD")
        return

    if de < ds:
        messagebox.showerror("Ошибка", "Дата окончания раньше начала")
        return

    if overlap(data, name, s, e):
        messagebox.showerror("Ошибка", "Пересечение отпусков")
        return

    days = days_between(s, e)

    if used_days(data, name) + days > LIMIT:
        messagebox.showerror("Ошибка", "Превышен лимит 28 дней")
        return

    data["vacations"].append({
        "name": name,
        "start": s,
        "end": e,
        "days": days
    })

    save_data(data)
    refresh()

# ---------- TABLE ----------
def refresh_table():
    data = load_data()
    tree.delete(*tree.get_children())

    for i, v in enumerate(data["vacations"]):
        tree.insert("", "end", iid=i, values=(
            v["name"], v["start"], v["end"], v["days"]
        ))

# ---------- EMP ----------
def refresh_emp():
    data = load_data()
    combo_emp["values"] = data["employees"]

    if data["employees"]:
        combo_emp.set(data["employees"][0])

# ---------- CALENDAR ----------
def draw_calendar():
    for w in cal_frame.winfo_children():
        w.destroy()

    if not month_var.get().isdigit() or not year_var.get().isdigit():
        messagebox.showerror("Ошибка", "Некорректный месяц или год")
        return

    data = load_data()

    y = int(year_var.get())
    m = int(month_var.get())

    cal = calendar.monthcalendar(y, m)

    tk.Label(
        cal_frame,
        text=f"{calendar.month_name[m]} {y}",
        font=("Arial", 16, "bold")
    ).pack()

    grid = tk.Frame(cal_frame)
    grid.pack()

    days = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]

    for i, d in enumerate(days):
        tk.Label(grid, text=d, width=14, bg="#ddd").grid(row=0, column=i)

    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            if day == 0:
                continue

            current = date(y, m, day)

            text = str(day)
            bg = "white"

            for v in data["vacations"]:
                s = datetime.strptime(v["start"], "%Y-%m-%d").date()
                e = datetime.strptime(v["end"], "%Y-%m-%d").date()

                if s <= current <= e:
                    text += f"\n{v['name']}"
                    bg = get_color(v["name"])

            tk.Label(
                grid,
                text=text,
                width=14,
                height=3,
                relief="solid",
                bg=bg
            ).grid(row=r+1, column=c)

# ---------- REFRESH ----------
def refresh():
    refresh_emp()
    refresh_table()
    draw_calendar()

# ---------- UI ----------
root = tk.Tk()
root.title("HR Vacation PRO MAX FIXED")
root.geometry("1100x700")

top = tk.Frame(root)
top.pack()

# employees
emp_entry = tk.Entry(top)
emp_entry.grid(row=0, column=0)

tk.Button(top, text="Добавить сотрудника", command=add_employee).grid(row=0, column=1)
tk.Button(top, text="Удалить сотрудника", command=delete_employee).grid(row=0, column=2)

combo_emp = ttk.Combobox(top)
combo_emp.grid(row=1, column=0)

# vacation
start_entry = tk.Entry(top)
end_entry = tk.Entry(top)

start_entry.grid(row=1, column=1)
end_entry.grid(row=1, column=2)

tk.Button(top, text="Добавить отпуск", command=add_vacation).grid(row=1, column=3)

# calendar controls
month_var = tk.StringVar(value=str(date.today().month))
year_var = tk.StringVar(value=str(date.today().year))

tk.Entry(top, textvariable=month_var, width=5).grid(row=2, column=0)
tk.Entry(top, textvariable=year_var, width=5).grid(row=2, column=1)

tk.Button(top, text="Обновить календарь", command=draw_calendar).grid(row=2, column=2)

# table
tree = ttk.Treeview(root, columns=("n","s","e","d"), show="headings")
tree.heading("n", text="Сотрудник")
tree.heading("s", text="Начало")
tree.heading("e", text="Конец")
tree.heading("d", text="Дней")
tree.pack(fill="x")

# calendar
cal_frame = tk.Frame(root)
cal_frame.pack(fill="both", expand=True)

refresh()
root.mainloop()
