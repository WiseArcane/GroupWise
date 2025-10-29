import tkinter as tk
import random
from tkinter import ttk, filedialog
from tkinter import messagebox

#main window
root = tk.Tk()
root.title("GroupWise!")
root.geometry("1000x800")
root.configure(bg="white")
root.resizable(True, True)
#Grid Configuration
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
# switch page funtion
def show_frame(frame):
    frame.tkraise()
#frames
welcome_page = tk.Frame(root, bg="white")
input_page = tk.Frame(root, bg="white")
result_page = tk.Frame(root, bg="white")
for frame in (welcome_page, input_page, result_page):
    frame.grid(row=0, column=0, sticky="nsew")
#Welcome page
tk.Label(
    welcome_page,
    text="Welcome to GroupWise!",
    font=("Arial", 20, "bold"),
    bg="white",
    fg="gray",
).pack(pady=(150,10))

tk.Label(
    welcome_page,
    text="Group work just got smarter!",
    font=("Arial", 12),
    bg="white"
).pack(pady=(0,20))

tk.Button(
    welcome_page,
    text="GET STARTED",
    font=("Arial", 11, "bold"),
    bg="black",
    fg="white",
    padx=25, pady=6,
    command=lambda: show_frame(input_page)
).pack()
# input page
tk.Label(
    input_page,
    text="Enter Member and Tasks",
    font=("Arial", 20, "bold"),
    bg="white",
).pack(pady=(30,0))

tk.Label(
    input_page,
    text="Enter each name or task on a new line.",
    font=("Arial", 10),
    bg="white",
    fg="gray"
).pack(pady=(0,15))
#Input container
input_frame = tk.Frame(input_page, bg="white")
input_frame.pack()
#Member Box
member_frame = tk.Frame(input_frame, bg="white")
tk.Label(member_frame, text="Members", font=("Arial", 12, "bold"), bg="white").pack()
member_text = tk.Text(member_frame, width=35, height=12, bg="#f9f9f9", relief="solid", bd=1)
member_text.pack(padx=10, pady=5)
member_frame.grid(row=0, column=0, padx=25)
#Tasks Box
task_frame = tk.Frame(input_frame, bg="white")
tk.Label(task_frame, text="Tasks", font=("Arial", 12, "bold"), bg="white").pack()
task_text = tk.Text(task_frame, width=35, height=12, bg="#f9f9f9", relief="solid", bd=1)
task_text.pack(padx=10, pady=(5,10))
task_frame.grid(row=0, column=1, padx=25)

# Group Box
group_frame = tk.Frame(input_frame, bg="white")
tk.Label(group_frame, text="Number of Groups (Optional)", font=("Arial", 12, "bold"), bg="white").pack()
group_entry = tk.Entry(group_frame, width=15, bg="#f9f9f9", relief="solid", bd=1, font=("Arial", 11))
group_entry.pack(padx=10, pady=(5,10))
group_frame.grid(row=1, column=0, columnspan=2, pady=10)

# Randomize function
def assign_tasks():
    members_input = member_text.get("1.0", "end").strip().split("\n")
    tasks_input = task_text.get("1.0", "end").strip().split("\n")
    groups_input = group_entry.get().strip()

    members = [m.strip() for m in members_input if m.strip() != ""]
    tasks = [t.strip() for t in tasks_input if t.strip() != ""]
    num_groups = 0
# error handling
    if groups_input:
        if not groups_input.isdigit() or int(groups_input) <= 0:
            messagebox.showerror("Error", "Number of groups must be a positive number.")
            return
        num_groups = int(groups_input)
    if not members:
        messagebox.showerror("Error", "Please enter at least one member name.")
        return
    if not tasks:
        messagebox.showerror("Error", "Please enter at least one task.")
        return
    random.shuffle(members)
    random.shuffle(tasks)

    assignments = [] # Will store (group, member, task)

    if num_groups > 0:
        if num_groups > len(members):
            messagebox.showwarning("Warning", "Number of groups is greater than the number of members. Some groups will be empty.")

        groups = [[] for _ in range(num_groups)]
        for i, member in enumerate(members):
            groups[i % num_groups].append(member)

        for i, group in enumerate(groups):
            if not group: continue # Skip empty groups

            shuffled_tasks = tasks[:]
            random.shuffle(shuffled_tasks)
            for j, member in enumerate(group):
                task = shuffled_tasks[j % len(shuffled_tasks)] # reuse tasks if fewer tasks than members in group
                assignments.append((f"Group {i+1}", member, task))
    else:
        # Original behavior: no groups
        if len(tasks) > len(members):
            for i, task in enumerate(tasks):
                member = members[i % len(members)]  # reuse members
                assignments.append(("-", member, task))
        else:
            for i, member in enumerate(members):
                task = tasks[i % len(tasks)]  # reuse tasks if fewer
                assignments.append(("-", member, task))

# Display the results
    for widget in result_table.get_children():
        result_table.delete(widget)
    for group, member, task in assignments:
        result_table.insert("", "end", values=(group, member, task))

    show_frame(result_page)
#button for the input page
button_frame = tk.Frame(input_page, bg="white")
button_frame.pack(pady=25)

tk.Button(
    button_frame,
    text="BACK",
    bg="#d3d3d3",
    fg="black",
    width=12,
    command=lambda: show_frame(welcome_page)
).grid(row=0, column=0, padx=15)

tk.Button(
    button_frame,
    text="ASSIGN TASKS",
    bg="#4C7FFF",
    fg="white",
    width=15,
    command=assign_tasks
).grid(row=0, column=1, padx=15)
#result page
tk.Label(
    result_page,
    text="Task Assignments",
    font=("Arial", 20, "bold"),
    bg="white"
).pack(pady=25)
#result table
table_frame = tk.Frame(result_page, bg="white")
table_frame.pack(pady=10)

columns = ("Group", "Member", "Task")
result_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
result_table.heading("Group", text="Group")
result_table.heading("Member", text="Member")
result_table.heading("Task", text="Assigned Task")
result_table.column("Group", width=100, anchor="center")
result_table.column("Member", width=250)
result_table.column("Task", width=350)
result_table.pack()

# Save results function
def save_results():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        title="Save Assignments"
    )
    if not file_path:
        return

    try:
        with open(file_path, "w") as f:
            f.write("Group,Member,Task\n")
            for item in result_table.get_children():
                values = result_table.item(item, 'values')
                f.write(f"{values[0]},{values[1]},{values[2]}\n")
        messagebox.showinfo("Success", "Assignments saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

#buttons
bottom_buttons = tk.Frame(result_page, bg="white")
bottom_buttons.pack(pady=20)

tk.Button(
    bottom_buttons,
    text="Back",
    bg="#d3d3d3",
    fg="black",
    width=15,
    command=lambda: show_frame(input_page)
).grid(row=0, column=0, padx=10)

tk.Button(
    bottom_buttons,
    text="Save",
    bg="#28a745", # Green 
    fg="white",
    width=15,
    command=save_results
).grid(row=0, column=1, padx=10)

tk.Button(
    bottom_buttons,
    text="Re-randomize",
    bg="#ffc107", # Yellow
    fg="black",
    width=15,
    command=assign_tasks
).grid(row=0, column=2, padx=10)

tk.Button(
    bottom_buttons,
    text="Exit",
    bg="#d9534f", # Red color for exit
    fg="white",
    width=15,
    command=root.quit
).grid(row=0, column=3, padx=10)

show_frame(welcome_page)
root.mainloop()