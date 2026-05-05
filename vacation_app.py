import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime, date
import calendar
import random

FILE = "data.json"

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

def apply_theme():
    bg = "#1e1e1e" if theme["dark"] else "#f4f4f4"
    fg = "#ffffff" if theme["dark"] else "#000000"

    root.configure(bg=bg)

    for w in root.winfo_children():
        try:
            w.configure(bg=bg, fg=fg)
        except:
            pass

# ---------------- COLORS ----------------
def color(name):
    random.seed(name)
    return f"#{random.randint(80,220):02x}{random.randint(80,220):02x}{random.randint(80,220):02x}"

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
    refresh_all()

def delete_emp():
    data = load_data()

    for item in emp_tree.selection():
        name = emp_tree.item(item)["values"][0]
        data["employees"].remove(name)
        data["vacations"] = [v for v in data["vacations"] if v["name"] != name]

    save_data(data)
    refresh_all()

# ---------------- VAC ----------------
def add_vac():
    data = load_data()

    name = combo.get()
    s = start.get()
    e = end.get()

    if name not in data["employees"]:
        messagebox.showerror("Ошибка", "Выберите сотрудника")
        return

    try:
        ds = parse(s)
        de = parse(e)
    except:
        messagebox.showerror("Ошибка", "Дата DD.MM.YYYY")
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
    refresh_all()

# ---------------- CALENDAR ----------------
def draw_calendar():
    for w in cal_frame.winfo_children():
        w.destroy()

    data = load_data()

    try:
        y = int(year.get())
    except:
        y = date.today().year

    selected = emp_tree.selection()
    selected_names = [emp_tree.item(i)["values"][0] for i in selected]

    tk.Label(cal_frame, text=f"📅 {y}", font=("Arial", 16, "bold")).pack()

    grid = tk.Frame(cal_frame)
    grid.pack()

    for m in range(1, 13):
        box = tk.LabelFrame(grid, text=calendar.month_name[m])
        box.grid(row=(m-1)//4, column=(m-1)%4, padx=5, pady=5)

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

                # логика подсветки
                if len(selected_names) > 0:
                    visible = [n for n in names if n in selected_names]
                else:
                    visible = names

                if len(visible) > 1:
                    bg = RED
                elif len(visible) == 1:
                    bg = color(visible[0])
                else:
                    bg = "white"

                tk.Label(row, text=str(d), width=3, bg=bg).pack(side="left")

# ---------------- TABLES ----------------
def refresh_tables():
    data = load_data()

    combo["values"] = data["employees"]

    emp_tree.delete(*emp_tree.get_children())
    for e in data["employees"]:
        emp_tree.insert("", "end", values=(e,))

    vac_tree.delete(*vac_tree.get_children())
    for v in data["vacations"]:
        vac_tree.insert("", "end", values=(
            v["name"],
            v["start"],
            v["end"],
            v["days"]
        ))

# ---------------- REFRESH ----------------
def refresh_all():
    refresh_tables()
    draw_calendar()
    apply_theme()

# ---------------- UI ----------------
root = tk.Tk()
root.title("HR ARCHITECTURE PRO")
root.geometry("1300x900")

# SIDEBAR NAV
sidebar = tk.Frame(root, width=200, bg="#2c2f33")
sidebar.pack(side="left", fill="y")

main = tk.Frame(root)
main.pack(side="right", fill="both", expand=True)

pages = []

# ---------------- PAGE EMP ----------------
emp_page = tk.Frame(main)
pages.append(emp_page)

tk.Label(emp_page, text="Сотрудники", font=("Arial", 14, "bold")).pack()

emp_entry = tk.Entry(emp_page)
emp_entry.pack(fill="x")

tk.Button(emp_page, text="Добавить", command=add_emp).pack()
tk.Button(emp_page, text="Удалить", command=delete_emp).pack()

emp_tree = ttk.Treeview(emp_page, columns=("name",), show="headings", height=6)
emp_tree.heading("name", text="ФИО")
emp_tree.pack(fill="x")

# ---------------- PAGE VAC ----------------
vac_page = tk.Frame(main)
pages.append(vac_page)

tk.Label(vac_page, text="Отпуска", font=("Arial", 14, "bold")).pack()

combo = ttk.Combobox(vac_page)
combo.pack(fill="x")

tk.Label(vac_page, text="Начало").pack()
start = tk.Entry(vac_page)
start.pack(fill="x")

tk.Label(vac_page, text="Конец").pack()
end = tk.Entry(vac_page)
end.pack(fill="x")

tk.Button(vac_page, text="Добавить отпуск", command=add_vac).pack()

vac_tree = ttk.Treeview(
    vac_page,
    columns=("name", "start", "end", "days"),
    show="headings"
)

vac_tree.heading("name", text="ФИО")
vac_tree.heading("start", text="Начало")
vac_tree.heading("end", text="Конец")
vac_tree.heading("days", text="Дней")
vac_tree.pack(fill="x")

# ---------------- PAGE CALENDAR ----------------
cal_page = tk.Frame(main)
pages.append(cal_page)

cal_frame = tk.Frame(cal_page)
cal_frame.pack(fill="both", expand=True)

year = tk.StringVar(value=str(date.today().year))
tk.Entry(cal_page, textvariable=year).pack()

tk.Button(cal_page, text="Обновить календарь", command=draw_calendar).pack()

# ---------------- SIDEBAR ----------------
def show(page):
    for p in pages:
        p.pack_forget()
    page.pack(fill="both", expand=True)

tk.Button(sidebar, text="👤 Сотрудники", command=lambda: show(emp_page)).pack(fill="x")
tk.Button(sidebar, text="🏖 Отпуска", command=lambda: show(vac_page)).pack(fill="x")
tk.Button(sidebar, text="📅 Календарь", command=lambda: show(cal_page)).pack(fill="x")
tk.Button(sidebar, text="🌙 Тема", command=lambda: toggle_theme()).pack(fill="x")

def toggle_theme():
    theme["dark"] = not theme["dark"]
    apply_theme()

# INIT
show(emp_page)
refresh_all()
root.mainloop()
