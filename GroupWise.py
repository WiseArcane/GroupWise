import tkinter as tk
import customtkinter
import random
import os
import json
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from tkinter import messagebox

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class GroupWiseApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Main Window Configuration
        self.title("GroupWise!")
        self.geometry("1200x900")
        self.resizable(True, True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        #Page Container
        container = customtkinter.CTkFrame(self, corner_radius=0)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.current_frame_name = None
        self.animation_in_progress = False

        self.frames = {}
        for F in (WelcomePage, InputPage, ResultPage):
            page_name = F.__name__
            color = "white"
            #Use default color for other pages
            if F is not WelcomePage:
                color = self.cget("fg_color")
            frame = F(parent=container, controller=self, fg_color=color)
            self.frames[page_name] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        if self.animation_in_progress or page_name == self.current_frame_name:
            return

        new_frame = self.frames[page_name]
        
        if self.current_frame_name is None:
            self.current_frame_name = page_name
            new_frame.tkraise()
            return

        self.animation_in_progress = True

        current_frame = self.frames[self.current_frame_name]
        
        #slide direction
        page_order = ["WelcomePage", "InputPage", "ResultPage"]
        current_index = page_order.index(self.current_frame_name)
        new_index = page_order.index(page_name)
        
        direction = 1 if new_index > current_index else -1

        new_frame.place(relx=direction, rely=0, relwidth=1, relheight=1)
        new_frame.tkraise()

        self._animate_slide(current_frame, new_frame, direction, 0.0)
        self.current_frame_name = page_name

    def _animate_slide(self, current_frame, new_frame, direction, progress):
        progress += 0.03  #Animation speed
        if progress >= 1.0:
            current_frame.place_forget()
            new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation_in_progress = False
            return

        current_frame.place(relx=-direction * progress, rely=0, relwidth=1, relheight=1)
        new_frame.place(relx=direction * (1 - progress), rely=0, relwidth=1, relheight=1)
        self.after(10, lambda: self._animate_slide(current_frame, new_frame, direction, progress))


class WelcomePage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        
        # entral frame to hold all widgets
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.place(relx=0.5, rely=0.45, anchor="center")
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "logo", "WelcomePageLogo.jpg")
            img = Image.open(image_path)
            self.logo_image = customtkinter.CTkImage(light_image=img, dark_image=img, size=(270, 360))
            logo_label = customtkinter.CTkLabel(main_frame, image=self.logo_image, text="")
            logo_label.pack(pady=(50, 10))
        except (FileNotFoundError, Exception) as e:
            print(f"Error loading logo: {e}")
            customtkinter.CTkLabel(main_frame, text="[Logo Not Found]", font=("Arial", 20)).pack(pady=(50,10))

        customtkinter.CTkLabel(main_frame, text="Welcome to GroupWise!", font=("Arial", 36, "bold"), text_color="#333333").pack(pady=(10,10))
        customtkinter.CTkLabel(main_frame, text="Group work just got smarter!", font=("Arial", 22), text_color="#444444").pack(pady=(0,20))
        customtkinter.CTkButton(main_frame, text="GET STARTED", font=("Arial", 18, "bold"), command=lambda: controller.show_frame("InputPage"), width=220, height=60).pack()


class InputPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller

        #Central frame to hold all widgets
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True)

        customtkinter.CTkLabel(main_frame, text="Enter Member and Tasks", font=("Arial", 26, "bold")).pack(pady=(30,0))
        customtkinter.CTkLabel(main_frame, text="Enter each name or task on a new line.", font=("Arial", 14)).pack(pady=(0,15))

        input_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(pady=10)

        #Member Box
        member_frame = customtkinter.CTkFrame(input_frame, fg_color="transparent")
        customtkinter.CTkLabel(member_frame, text="Members", font=("Arial", 16, "bold")).pack()
        self.member_text = customtkinter.CTkTextbox(member_frame, width=300, height=300, font=("Arial", 14))
        self.member_text.bind("<Button-3>", self.show_context_menu)
        self.member_text.pack(padx=10, pady=5)
        member_frame.grid(row=0, column=0, padx=25)

        #Tasks Box
        task_frame = customtkinter.CTkFrame(input_frame, fg_color="transparent")
        customtkinter.CTkLabel(task_frame, text="Tasks", font=("Arial", 16, "bold")).pack()
        self.task_text = customtkinter.CTkTextbox(task_frame, width=300, height=300, font=("Arial", 14))
        self.task_text.bind("<Button-3>", self.show_context_menu)
        self.task_text.pack(padx=10, pady=(5,10))
        task_frame.grid(row=0, column=1, padx=25)

        #Group Box
        group_frame = customtkinter.CTkFrame(input_frame, fg_color="transparent")
        customtkinter.CTkLabel(group_frame, text="Number of Groups (Optional)", font=("Arial", 16, "bold")).pack()
        self.group_entry = customtkinter.CTkEntry(group_frame, width=180, font=("Arial", 14))
        self.group_entry.pack(padx=10, pady=(5,10))
        group_frame.grid(row=1, column=0, columnspan=2, pady=10)

        #Button Frame
        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=30)
        customtkinter.CTkButton(button_frame, text="BACK", command=lambda: controller.show_frame("WelcomePage"), fg_color="#d3d3d3", text_color="black", hover_color="#c0c0c0", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=0, padx=15)
        customtkinter.CTkButton(button_frame, text="ASSIGN TASKS", command=self.assign_tasks, font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=1, padx=15)

    def show_context_menu(self, event):
        widget = event.widget
        context_menu = tk.Menu(widget, tearoff=0)
        
        has_selection = False
        try:
            if widget.tag_ranges("sel"):
                has_selection = True
        except tk.TclError: #Nothing selected
            pass 

        context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"), state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        
        context_menu.tk_popup(event.x_root, event.y_root)


    def assign_tasks(self):
        result_page = self.controller.frames["ResultPage"]
        result_page.clear_table()

        members_input = self.member_text.get("1.0", "end").strip().split("\n")
        tasks_input = self.task_text.get("1.0", "end").strip().split("\n")
        groups_input = self.group_entry.get().strip()

        members = [line.strip() for line in members_input if line.strip()]
        tasks = [line.strip() for line in tasks_input if line.strip()]
        num_groups = 0

        #Check for duplicate members
        if len(members) != len(set(members)):
            messagebox.showerror("Error", "Duplicate member names are not allowed.")
            return
        if len(tasks) != len(set(tasks)):
            messagebox.showerror("Error", "Duplicate tasks are not allowed.")
            return

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

        assignments = []

        if num_groups > 0:
            if num_groups > len(members):
                messagebox.showwarning("Warning", "Number of groups is greater than the number of members. Some groups will be empty.")
            groups = [[] for _ in range(num_groups)]
            for i, member in enumerate(members):
                groups[i % num_groups].append(member)

            #Create a shared task pool for all groups.
            num_total_members = len(members)
            extended_tasks = []
            if num_total_members > len(tasks):
                num_repeats = num_total_members // len(tasks)
                remainder = num_total_members % len(tasks)
                extended_tasks.extend(tasks * num_repeats)
                extended_tasks.extend(tasks[:remainder])
            else:
                extended_tasks = tasks[:num_total_members]
            random.shuffle(extended_tasks)

            task_idx = 0
            for i, group in enumerate(groups):
                if not group: continue
                for member in group:
                    task = extended_tasks[task_idx]
                    task_idx += 1
                    assignments.append((f"Group {i+1}", member, task))
        else:
            for i, member in enumerate(members):
                task = tasks[i % len(tasks)]
                assignments.append(("-", member, task))

        result_page.populate_table(assignments)
        self.controller.show_frame("ResultPage")


class ResultPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller

        #Central frame to hold all widgets
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True)

        customtkinter.CTkLabel(main_frame, text="Task Assignments", font=("Arial", 26, "bold")).pack(pady=25)

        table_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        table_frame.pack(pady=10, padx=20, expand=True)

        columns = ("Group", "Member", "Task")
        self.result_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        self.result_table.heading("Group", text="Group")
        self.result_table.heading("Member", text="Member")
        self.result_table.heading("Task", text="Assigned Task")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#f0f0f0", foreground="black", rowheight=30, fieldbackground="#f0f0f0", font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        style.map('Treeview', background=[('selected', '#347083')])
        self.result_table.tag_configure('oddrow', background='#E8E8E8')
        self.result_table.tag_configure('evenrow', background='#DFDFDF')

        self.result_table.column("Group", width=100, anchor="center")
        self.result_table.column("Member", width=300)
        self.result_table.column("Task", width=400)

        result_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.result_table.yview)
        self.result_table.configure(yscrollcommand=result_scrollbar.set)
        result_scrollbar.pack(side="right", fill="y")
        self.result_table.pack(side="left")

        #Bottom Buttons
        bottom_buttons = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        bottom_buttons.pack(pady=20)
        
        customtkinter.CTkButton(bottom_buttons, text="Back", command=lambda: controller.show_frame("InputPage"), fg_color="#d3d3d3", text_color="black", hover_color="#c0c0c0", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=0, padx=10)
        customtkinter.CTkButton(bottom_buttons, text="Save", command=self.save_results, fg_color="#28a745", hover_color="#218838", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=1, padx=10)
        customtkinter.CTkButton(bottom_buttons, text="Re-randomize", command=lambda: controller.frames["InputPage"].assign_tasks(), fg_color="#ffc107", text_color="black", hover_color="#e0a800", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=2, padx=10)
        customtkinter.CTkButton(bottom_buttons, text="Exit", command=controller.quit, fg_color="#d9534f", hover_color="#c82333", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=3, padx=10)

    def clear_table(self):
        for widget in self.result_table.get_children():
            self.result_table.delete(widget)

    def populate_table(self, assignments):
        for i, (group, member, task) in enumerate(assignments):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.result_table.insert("", "end", values=(group, member, task), tags=(tag,))

    def save_results(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Assignments"
        )
        if not file_path:
            return

        assignments_data = []
        for item in self.result_table.get_children():
            values = self.result_table.item(item, 'values')
            assignment = {"Group": values[0], "Member": values[1], "Task": values[2]}
            assignments_data.append(assignment)

        try:
            with open(file_path, "w") as f:
                json.dump(assignments_data, f, indent=4)
            messagebox.showinfo("Success", "Assignments saved successfully as a JSON file!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {e}")


if __name__ == "__main__":
    app = GroupWiseApp()
    app.mainloop()
