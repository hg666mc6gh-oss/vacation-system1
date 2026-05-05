import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, date
import calendar

FILE = "data.json"
ANNUAL_LIMIT = 28

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

# ---------- LOGIC ----------
def calc_days(start, end):
    d1 = datetime.strptime(start, "%Y-%m-%d")
    d2 = datetime.strptime(end, "%Y-%m-%d")
    return (d2 - d1).days + 1

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

def used_days(data, name):
    return sum(v["days"] for v in data["vacations"] if v["name"] == name)

# ---------- EMPLOYEES ----------
def add_employee():
    data = load_data()
    name = emp_entry.get().strip()

    if not name:
        return

    if name in data["employees"]:
        messagebox.showerror("Ошибка", "Сотрудник уже есть")
        return

    data["employees"].append(name)
    save_data(data)
    refresh_employees()

def delete_employee():
    data = load_data()
    name = combo_emp.get()

    if name in data["employees"]:
        data["employees"].remove(name)

        # удалить его отпуска тоже
        data["vacations"] = [v for v in data["vacations"] if v["name"] != name]

        save_data(data)
        refresh_employees()
        refresh_table()
        draw_calendar()

# ---------- VACATION ----------
def add_vacation():
    data = load_data()

    name = combo_emp.get()
    start = start_entry.get()
    end = end_entry.get()

    if not name or not start or not end:
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
    refresh_table()
    draw_calendar()

# ---------- TABLE ----------
def refresh_table():
    data = load_data()
    tree.delete(*tree.get_children())

    for i, v in enumerate(data["vacations"]):
        tree.insert("", "end", iid=i, values=(
            v["name"], v["start"], v["end"], v["days"]
        ))

# ---------- EMP UI ----------
def refresh_employees():
    data = load_data()
    combo_emp["values"] = data["employees"]

# ---------- CALENDAR ----------
def draw_calendar():
    for w in cal_frame.winfo_children():
        w.destroy()

    data = load_data()

    today = date.today()
    y = today.year
    m = today.month

    cal = calendar.monthcalendar(y, m)

    tk.Label(cal_frame, text=f"{calendar.month_name[m]} {y}", font=("Arial", 14)).pack()

    grid = tk.Frame(cal_frame)
    grid.pack()

    for i, day in enumerate(["Пн","Вт","Ср","Чт","Пт","Сб","Вс"]):
        tk.Label(grid, text=day, width=10).grid(row=0, column=i)

    for r, week in enumerate(cal):
        for c, day in enumerate(week):
            if day == 0:
                continue

            text = str(day)

            # проверка отпусков
            for v in data["vacations"]:
                s = datetime.strptime(v["start"], "%Y-%m-%d")
                e = datetime.strptime(v["end"], "%Y-%m-%d")
                current = date(y, m, day)

                if s.date() <= current <= e.date():
                    text += f"\n{v['name']}"

            tk.Label(grid, text=text, relief="groove", width=10, height=3).grid(row=r+1, column=c)

# ---------- UI ----------
root = tk.Tk()
root.title("Учёт отпусков PRO")
root.geometry("900x600")

data = load_data()

# employees
top = tk.Frame(root)
top.pack()

emp_entry = tk.Entry(top)
emp_entry.grid(row=0, column=0)

tk.Button(top, text="Добавить сотрудника", command=add_employee).grid(row=0, column=1)
tk.Button(top, text="Удалить сотрудника", command=delete_employee).grid(row=0, column=2)

combo_emp = ttk.Combobox(top)
combo_emp.grid(row=1, column=0)

# vacation input
start_entry = tk.Entry(top)
end_entry = tk.Entry(top)

start_entry.grid(row=1, column=1)
end_entry.grid(row=1, column=2)

tk.Button(top, text="Добавить отпуск", command=add_vacation).grid(row=1, column=3)

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

refresh_employees()
refresh_table()
draw_calendar()

root.mainloop()
