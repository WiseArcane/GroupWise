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

        assignments = []

        if num_groups > 0:
            #Logic for when groups are specified: Distribute tasks within each group
            if num_groups > len(members):
                messagebox.showwarning("Warning", "Number of groups is greater than the number of members. Some groups will be empty.")

            #step 1. Divide members into groups
            groups = {f"Group {i+1}": [] for i in range(num_groups)}
            for i, member in enumerate(members):
                groups[f"Group {i % num_groups + 1}"].append(member)

            #step 2. For each group, distribute all tasks among its members
            for group_name, group_members in groups.items():
                if not group_members:
                    continue
                
                random.shuffle(tasks)
                member_tasks = {member: [] for member in group_members}

                #Assign all tasks to members within this group
                for i, task in enumerate(tasks):
                    member_in_group = group_members[i % len(group_members)]
                    member_tasks[member_in_group].append(task)

                #Format for final list
                for member, assigned_tasks in member_tasks.items():
                    tasks_str = ", ".join(assigned_tasks) if assigned_tasks else ""
                    assignments.append((group_name, member, tasks_str))
        else:
            #Original logic for when no groups are specified
            random.shuffle(tasks)
            member_tasks = {member: [] for member in members}
            
            #Assign all tasks across all members
            for i, task in enumerate(tasks):
                member = members[i % len(members)]
                member_tasks[member].append(task)

            for member, assigned_tasks in member_tasks.items():
                tasks_str = ", ".join(assigned_tasks) if assigned_tasks else ""
                assignments.append(("-", member, tasks_str))

        result_page.populate_table(assignments)
        self.controller.show_frame("ResultPage")


class ResultPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.assignments = [] #To store assignment data for saving

        #Central frame to hold all widgets
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True)

        customtkinter.CTkLabel(main_frame, text="Task Assignments", font=("Arial", 26, "bold")).pack(pady=25)

        self.result_frame = customtkinter.CTkScrollableFrame(main_frame, width=800, height=500)
        self.result_frame.pack(pady=10, padx=20, fill="both", expand=True)

        #Bottom Buttons
        bottom_buttons = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        bottom_buttons.pack(pady=20)
        
        customtkinter.CTkButton(bottom_buttons, text="Back", command=lambda: controller.show_frame("InputPage"), fg_color="#d3d3d3", text_color="black", hover_color="#c0c0c0", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=0, padx=10)
        customtkinter.CTkButton(bottom_buttons, text="Save", command=self.save_results, fg_color="#28a745", hover_color="#218838", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=1, padx=10)
        customtkinter.CTkButton(bottom_buttons, text="Re-randomize", command=lambda: controller.frames["InputPage"].assign_tasks(), fg_color="#ffc107", text_color="black", hover_color="#e0a800", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=2, padx=10)
        customtkinter.CTkButton(bottom_buttons, text="Exit", command=controller.quit, fg_color="#d9534f", hover_color="#c82333", font=("Arial", 18, "bold"), width=150, height=40).grid(row=0, column=3, padx=10)

    def clear_table(self):
        #Destroy all widgets inside the scrollable frame
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def populate_table(self, assignments):
        self.clear_table()
        self.assignments = assignments #Store for saving

        #Group members by group name
        grouped_results = {}
        for group, member, task in assignments:
            if group not in grouped_results:
                grouped_results[group] = []
            grouped_results[group].append((member, task))

        #Sort groups (e.g., "Group 1", "Group 2", ...)
        sorted_groups = sorted(grouped_results.keys(), key=lambda g: (g.split()[0], int(g.split()[1]) if g.startswith("Group") and g.split()[1].isdigit() else g))

        for group_name in sorted_groups:
            #Add group header
            group_label = customtkinter.CTkLabel(self.result_frame, text=f"{group_name}:", font=("Arial", 20, "bold"))
            group_label.pack(anchor="w", padx=10, pady=(15, 5))

            for member, task in grouped_results[group_name]:
                task_display = task if task else "No task assigned"
                member_label = customtkinter.CTkLabel(self.result_frame, text=f"  - {member} → {task_display}", font=("Arial", 16))
                member_label.pack(anchor="w", padx=20)
        
    def save_results(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Save Assignments"
        )
        if not file_path:
            return

        assignments_data = []
        for group, member, task in self.assignments:
            assignment = {"Group": group, "Member": member, "Task": task}
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

