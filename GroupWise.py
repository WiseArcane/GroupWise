import tkinter as tk
import customtkinter
import random
import os
import sys
import json
import csv
from tkinter import filedialog, messagebox
from datetime import datetime
from PIL import Image
from tkcalendar import Calendar

#Set default color theme
customtkinter.set_default_color_theme("blue")
customtkinter.set_appearance_mode("Dark")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class GroupWiseApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        #Main Window Configuration
        self.title("GroupWise! v2.0")
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
            frame = F(parent=container, controller=self)
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

        #fade animation for Input -> Result page transition to avoid lag
        if self.current_frame_name == "InputPage" and page_name == "ResultPage":
            #Place new frame underneath and start fade
            new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            new_frame.tkraise()
            #Create a temporary overlay on the current frame to fade out
            fade_overlay = customtkinter.CTkFrame(current_frame, fg_color=current_frame.cget("fg_color"))
            fade_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._animate_fade(fade_overlay, new_frame, 1.0)
            self.current_frame_name = page_name #Set current frame name immediately
            return #Return to let the animation run
        
        #Determine slide direction
        page_order = ["WelcomePage", "InputPage", "ResultPage"]
        current_index = page_order.index(self.current_frame_name)
        new_index = page_order.index(page_name)
        
        direction = 1 if new_index > current_index else -1

        new_frame.place(relx=direction, rely=0, relwidth=1, relheight=1)
        new_frame.tkraise()

        self._animate_slide(current_frame, new_frame, direction, 0.0)
        self.current_frame_name = page_name

    def _animate_slide(self, current_frame, new_frame, direction, progress):
        progress += 0.04
        if progress >= 1.0:
            current_frame.place_forget()
            new_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation_in_progress = False
            return

        current_frame.place(relx=-direction * progress, rely=0, relwidth=1, relheight=1)
        new_frame.place(relx=direction * (1 - progress), rely=0, relwidth=1, relheight=1)
        self.after(10, lambda: self._animate_slide(current_frame, new_frame, direction, progress))

    def _animate_fade(self, fade_overlay, new_frame, alpha):
        alpha -= 0.1
        if alpha <= 0.0:
            fade_overlay.destroy()
            self.animation_in_progress = False
            return
        #we just destroy it at the end. The visual effect is a quick.
        self.after(20, lambda: self._animate_fade(fade_overlay, new_frame, alpha))



class CustomScrollableFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, bg=self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]), highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.v_scrollbar = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.h_scrollbar = customtkinter.CTkScrollbar(self, orientation="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.scrollable_frame = customtkinter.CTkFrame(self.canvas, fg_color="transparent")
        self.window_item = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        #Mousewheel binding
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if self.scrollable_frame.winfo_height() > self.canvas.winfo_height():
             self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        canvas_width = event.width
        self.canvas.itemconfig(self.window_item, width=canvas_width)

    def winfo_children(self):
        return self.scrollable_frame.winfo_children()


class WelcomePage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=50, pady=50)
        self.main_frame.grid_rowconfigure((0, 4), weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.logo_image = None
        try:
            image_path = resource_path(os.path.join("logo", "WelcomePageLogo.jpg"))
            if os.path.exists(image_path):
                img = Image.open(image_path)
                original_width, original_height = img.size
                max_height = 400
                aspect_ratio = original_width / original_height
                new_height = min(original_height, max_height)
                new_width = int(new_height * aspect_ratio)

                self.logo_image = customtkinter.CTkImage(light_image=img, dark_image=img, size=(new_width, new_height))
                logo_label = customtkinter.CTkLabel(self.main_frame, image=self.logo_image, text="")
                logo_label.grid(row=1, column=0, pady=(20, 10))
            else:
                customtkinter.CTkLabel(self.main_frame, text="GroupWise!", font=("Courier New", 50, "bold")).grid(row=1, column=0, pady=(20,10))
        except Exception as e:
            customtkinter.CTkLabel(self.main_frame, text="GroupWise!", font=("Courier New", 50, "bold")).grid(row=1, column=0, pady=(20,10))

        self.subtitle_label = customtkinter.CTkLabel(self.main_frame, text="Group work just got smarter!", font=("Courier New", 24, "italic"), text_color="gray")
        self.subtitle_label.grid(row=3, column=0, pady=(0,5))

        description_text = "The intelligent tool to randomly assign members to groups and distribute tasks evenly."
        customtkinter.CTkLabel(self.main_frame, text=description_text, font=("Courier New", 16), text_color="lightgray", wraplength=500, justify="center").grid(row=4, column=0, pady=(10,30))
        
        customtkinter.CTkButton(self.main_frame, 
                                text="GET STARTED", 
                                font=("Courier New", 22, "bold"), 
                                command=lambda: controller.show_frame("InputPage"), 
                                width=250, 
                                height=70,
                                fg_color="#4CAF50",
                                hover_color="#45A049", 
                                text_color="white"
                                ).grid(row=5, column=0, pady=(20, 40))


class InputPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller

        #Main Layout
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        #Header
        customtkinter.CTkLabel(main_frame, text="Configure Groups", font=("Courier New", 28, "bold")).pack(pady=(10,0))
        customtkinter.CTkLabel(main_frame, text="One entry per line.", font=("Courier New", 16, "italic"), text_color="gray").pack(pady=(0,15))

        #Input Container
        input_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(pady=(10, 20), padx=80, fill="both", expand=True)

        #Member Column
        member_col = customtkinter.CTkFrame(input_frame, fg_color="transparent")
        member_col.pack(side="left", expand=True, fill="both", padx=10)
        
        #Member Header with Counter
        self.member_label = customtkinter.CTkLabel(member_col, text="Members (0)", font=("Courier New", 24, "bold"))
        self.member_label.pack()
        
        self.member_text = customtkinter.CTkTextbox(member_col, font=("Courier New", 16))
        self.member_text.pack(expand=True, fill="both", pady=5)
        self.member_text.bind("<Button-3>", self.show_context_menu)
        self.member_text.bind("<KeyRelease>", self.update_counters) # UPGRADE: Real-time counting

        #Task Column
        task_col = customtkinter.CTkFrame(input_frame, fg_color="transparent")
        task_col.pack(side="right", expand=True, fill="both", padx=10)

        #Task Header with Counter
        self.task_label = customtkinter.CTkLabel(task_col, text="Tasks (0)", font=("Courier New", 24, "bold"))
        self.task_label.pack()

        self.task_text = customtkinter.CTkTextbox(task_col, font=("Courier New", 16))
        self.task_text.pack(expand=True, fill="both", pady=5)
        self.task_text.bind("<Button-3>", self.show_context_menu)
        self.task_text.bind("<KeyRelease>", self.update_counters) #UPGRADE: Real-time counting

        #Options Row
        options_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(pady=10)

        #Number of Groups
        customtkinter.CTkLabel(options_frame, text="Number of Groups:", font=("Courier New", 16, "bold")).grid(row=0, column=0, padx=5)
        self.group_entry = customtkinter.CTkEntry(options_frame, width=100, font=("Courier New", 16), placeholder_text="Required")
        self.group_entry.grid(row=0, column=1, padx=5)

        #Subject
        customtkinter.CTkLabel(options_frame, text="Subject:", font=("Courier New", 16, "bold")).grid(row=0, column=2, padx=5)
        self.subject_entry = customtkinter.CTkEntry(options_frame, width=200, font=("Courier New", 16), placeholder_text="Optional")
        self.subject_entry.grid(row=0, column=3, padx=5)

        #Action Buttons
        button_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        btn_style = {"font": ("Courier New", 16, "bold"), "width": 140, "height": 45}

        customtkinter.CTkButton(button_frame, text="< Back", command=lambda: controller.show_frame("WelcomePage"), 
                                fg_color="#6c757d", hover_color="#5a6268", **btn_style).grid(row=0, column=0, padx=10)
        
        customtkinter.CTkButton(button_frame, text="Clear", command=self.clear_inputs, 
                                fg_color="#C0392B", hover_color="#A93226", **btn_style).grid(row=0, column=1, padx=10)

        #Added CSV support
        customtkinter.CTkButton(button_frame, text="Import CSV/JSON", command=self.load_file, 
                                fg_color="#F39C12", hover_color="#E67E22", text_color="black", **btn_style).grid(row=0, column=2, padx=10)
        
        customtkinter.CTkButton(button_frame, text="Assign Tasks >", command=self.assign_tasks, 
                                fg_color="#1f538d", hover_color="#14375e", **btn_style).grid(row=0, column=3, padx=10)

    def update_counters(self, event=None):
        """Updates the labels with the line count of the text boxes"""
        members = [line for line in self.member_text.get("1.0", "end").strip().split("\n") if line.strip()]
        tasks = [line for line in self.task_text.get("1.0", "end").strip().split("\n") if line.strip()]
        
        self.member_label.configure(text=f"Members ({len(members)})")
        self.task_label.configure(text=f"Tasks ({len(tasks)})")

    def clear_inputs(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all fields?"):
            self.member_text.delete("1.0", "end")
            self.task_text.delete("1.0", "end")
            self.group_entry.delete(0, "end")
            self.subject_entry.delete(0, "end")
            self.update_counters()

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a File",
            filetypes=[("Data files", "*.json *.csv *.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return

        if file_path.lower().endswith('.csv') or file_path.lower().endswith('.txt'):
            self.import_csv(file_path)
        else:
            self.populate_from_json(file_path)

    def import_csv(self, file_path):
        """UPGRADE: Reads a CSV file with 'Members' and 'Tasks' columns"""
        members = []
        tasks = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                #Simple logic try to detect columns or just read raw lines
                for row in reader:
                    for item in row:
                        if item.strip():
                            # or try to split if there are 2 columns
                            pass
                
            #Better approach for CSV: Ask user what they are importing? 
            #Just read the file as raw text and let user paste, 
            #OR assume Column 1 = Members, Column 2 = Tasks
            
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None) #Skip header if exists
                
                #Reset file pointer
                f.seek(0)
                
                #If valid csv structure
                for row in reader:
                    if len(row) >= 1 and row[0].strip():
                        if "member" not in row[0].lower(): #Skip header
                            members.append(row[0].strip())
                    if len(row) >= 2 and row[1].strip():
                         if "task" not in row[1].lower(): #Skip header
                            tasks.append(row[1].strip())

            if members:
                current_members = self.member_text.get("1.0", "end").strip()
                if current_members: current_members += "\n"
                self.member_text.insert("end", "\n".join(members) + "\n")
            
            if tasks:
                current_tasks = self.task_text.get("1.0", "end").strip()
                if current_tasks: current_tasks += "\n"
                self.task_text.insert("end", "\n".join(tasks) + "\n")
            
            self.update_counters()
            messagebox.showinfo("Import", "CSV data appended successfully!")

        except Exception as e:
             messagebox.showerror("Error", f"Failed to read CSV: {e}")

    def show_context_menu(self, event):
        widget = event.widget
        context_menu = tk.Menu(widget, tearoff=0)
        has_selection = False
        try:
            if widget.tag_ranges("sel"):
                has_selection = True
        except tk.TclError:
            pass 
        context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"), state=tk.NORMAL if has_selection else tk.DISABLED)
        context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
        context_menu.tk_popup(event.x_root, event.y_root)

    def populate_from_json(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            members = set()
            tasks = set()
            groups = set()

            if "Assignments" in data and isinstance(data["Assignments"], list):
                assignments_list = data["Assignments"]
                subject = data.get("Subject", "")
            else: 
                assignments_list = data
                subject = ""

            for item in assignments_list:
                if item.get("Member"):
                    members.add(item["Member"])
                if item.get("Task"):
                    for task in item["Task"].split(','):
                        task = task.strip()
                        if task:
                            tasks.add(task)
                if item.get("Group") and item["Group"] != "-":
                    groups.add(item["Group"])

            self.member_text.delete("1.0", "end")
            self.task_text.delete("1.0", "end")
            self.group_entry.delete(0, "end")
            self.subject_entry.delete(0, "end")

            self.member_text.insert("1.0", "\n".join(sorted(list(members))))
            self.task_text.insert("1.0", "\n".join(sorted(list(tasks))))
            if groups:
                self.group_entry.insert(0, str(len(groups)))
            if subject:
                self.subject_entry.insert(0, subject)
            
            self.update_counters()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

    def assign_tasks(self):
        result_page = self.controller.frames["ResultPage"]
        result_page.clear_table()

        members = [line.strip() for line in self.member_text.get("1.0", "end").strip().split("\n") if line.strip()]
        tasks = [line.strip() for line in self.task_text.get("1.0", "end").strip().split("\n") if line.strip()]
        groups_input = self.group_entry.get().strip()
        subject_input = self.subject_entry.get().strip()

        #Validation
        if not members:
            messagebox.showerror("Error", "Please enter at least one member name.")
            return

        for member in members:
            if len(member) < 2:
                messagebox.showerror("Input Error", f"Member name '{member}' is too short.\n\nPlease ensure all member names are at least 2 characters long.")
                return

        if not tasks:
            messagebox.showerror("Error", "Please enter at least one task.")
            return
        
        #Determine unique members to warn about duplicates (optional, strictly speaking we can have 2 Johns)
        
        if not groups_input:
            messagebox.showerror("Error", "Please enter the number of groups.")
            return
        
        if not groups_input.isdigit():
            messagebox.showerror("Error", "Letters are not allowed. Please enter numbers only.")
            return
        
        if int(groups_input) <= 0:
            messagebox.showerror("Error", "Number of groups must be a positive number.")
            return
        
        num_groups = int(groups_input)

        if num_groups > len(members):
            messagebox.showerror("Error", "Number of groups cannot exceed the number of members.")
            return

        assignments = []
        
        #Logic
        random.shuffle(members)
        
        groups = {f"Group {i+1}": [] for i in range(num_groups)}
        for i, member in enumerate(members):
            groups[f"Group {i % num_groups + 1}"].append(member)

        for group_name, group_members in groups.items():
            if not group_members: continue
            
            random.shuffle(tasks)
            member_tasks = {member: [] for member in group_members}

            targets = tasks if len(tasks) >= len(group_members) else group_members
            source = group_members if len(tasks) >= len(group_members) else tasks
            
            count = max(len(tasks), len(group_members))
            for i in range(count):
                m = group_members[i % len(group_members)]
                t = tasks[i % len(tasks)]
                member_tasks[m].append(t)

            for member, assigned_tasks in member_tasks.items():
                tasks_str = ", ".join(assigned_tasks)
                assignments.append((group_name, member, tasks_str))

            random.shuffle(tasks)

        result_page.populate_table(assignments, subject_input, len(members), len(tasks))
        self.controller.show_frame("ResultPage")


class ResultPage(customtkinter.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.assignments = []
        self.deadline_value = None
        self.subject_value = None

        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        #Header Area
        header_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))

        customtkinter.CTkLabel(header_frame, text="Results", font=("Courier New", 32, "bold")).pack()
        
        self.subject_label = customtkinter.CTkLabel(header_frame, text="", font=("Courier New", 20, "italic"), text_color="#3498DB")
        self.subject_label.pack(pady=(5, 5))

        #UPGRADE: Stats Bar
        self.stats_label = customtkinter.CTkLabel(header_frame, text="Stats: -", font=("Courier New", 14), text_color="gray")
        self.stats_label.pack(pady=(0,10))

        #Deadline & Tools
        tools_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        tools_frame.pack(pady=(0, 10))

        self.deadline_label = customtkinter.CTkLabel(tools_frame, text="Deadline: Not set", font=("Courier New", 16))
        self.deadline_label.grid(row=0, column=0, padx=15)

        customtkinter.CTkButton(tools_frame, text="Set Deadline", command=self.open_deadline_popup, 
                                font=("Courier New", 14), width=120, height=30, fg_color="#1ABC9C", hover_color="#16A085", text_color="black").grid(row=0, column=1, padx=5)

        #UPGRADE: Copy to Clipboard
        customtkinter.CTkButton(tools_frame, text="Copy to Clipboard", command=self.copy_to_clipboard,
                                font=("Courier New", 14), width=160, height=30, fg_color="#8E44AD", hover_color="#732D91").grid(row=0, column=2, padx=5)

        #Results Area
        self.result_frame = CustomScrollableFrame(main_frame)
        self.result_frame.pack(pady=10, padx=100, fill="both", expand=True)

        #Footer Buttons
        bottom_buttons = customtkinter.CTkFrame(main_frame, fg_color="transparent")
        bottom_buttons.pack(pady=10)

        btn_style = {"font": ("Courier New", 18, "bold"), "width": 160, "height": 50}

        customtkinter.CTkButton(bottom_buttons, text="Edit / Back", command=lambda: controller.show_frame("InputPage"), 
                                fg_color="#6c757d", hover_color="#5a6268", **btn_style).grid(row=0, column=0, padx=10)

        #Save Menu
        self.save_btn = customtkinter.CTkButton(bottom_buttons, text="Save As...", command=self.save_results, 
                                fg_color="#28a745", hover_color="#218838", text_color="black", **btn_style)
        self.save_btn.grid(row=0, column=1, padx=10)

        customtkinter.CTkButton(bottom_buttons, text="Re-Shuffle", command=lambda: controller.frames["InputPage"].assign_tasks(), 
                                fg_color="#ffc107", hover_color="#e0a800", text_color="black", **btn_style).grid(row=0, column=2, padx=10)

    def open_deadline_popup(self):
        popup = customtkinter.CTkToplevel(self)
        popup.title("Set Deadline")
        popup.geometry("400x350")
        popup.grab_set()
        popup.resizable(False, False)

        customtkinter.CTkLabel(popup, text="Select a Deadline", font=("Courier New", 16, "bold")).pack(pady=10)

        cal = Calendar(popup, selectmode='day', date_pattern='mm/dd/y', background="white",
                       foreground='black', headersbackground="white", normalbackground="white", 
                       weekendbackground="white", selectbackground="#1f6aa5", bordercolor="#cccccc")
        cal.pack(pady=10, padx=10, fill="both", expand=True)
        
        def confirm_deadline():
            deadline_date = cal.selection_get()
            if deadline_date < datetime.now().date():
                messagebox.showerror("Error", "Deadline cannot be in the past.", parent=popup)
                return
            self.deadline_value = deadline_date.strftime('%m/%d/%Y')
            self.deadline_label.configure(text=f"Deadline: {self.deadline_value}")
            popup.destroy()

        customtkinter.CTkButton(popup, text="Confirm", command=confirm_deadline, fg_color="#1ABC9C", hover_color="#16A085", text_color="black").pack(pady=15)

    def clear_table(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

    def populate_table(self, assignments, subject=None, total_members=0, total_tasks=0):
        self.clear_table()
        self.assignments = assignments
        self.subject_value = subject
        self.subject_label.configure(text=f"Subject: {subject}" if subject else "")
        self.deadline_value = None
        self.deadline_label.configure(text="Deadline: Not set")

        grouped_results = {}
        for group, member, task in assignments:
            grouped_results.setdefault(group, []).append((member, task))

        sorted_groups = sorted(grouped_results.keys(), key=lambda g: (g.split()[0], int(g.split()[1]) if g.startswith("Group") and g.split()[1].isdigit() else g))

        # Update stats
        self.stats_label.configure(text=f"Total: {total_members} Members | {len(sorted_groups)} Groups")

        for group_name in sorted_groups:
            card = customtkinter.CTkFrame(self.result_frame.scrollable_frame, border_width=1)
            card.pack(fill="x", pady=8, padx=10)
            
            header = customtkinter.CTkFrame(card, height=30, corner_radius=0)
            header.pack(fill="x")
            customtkinter.CTkLabel(header, text=group_name, font=("Courier New", 18, "bold")).pack(pady=2)
            
            content_frame = customtkinter.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=10)

            for member, task in grouped_results[group_name]:
                row = customtkinter.CTkFrame(content_frame, fg_color="transparent")
                row.pack(fill="x", pady=2, anchor="w")
                customtkinter.CTkLabel(row, text=f"• {member}", font=("Courier New", 16, "bold"), anchor="w", width=150).pack(side="left")
                customtkinter.CTkLabel(row, text=f"→ {task}", font=("Courier New", 16), text_color="#ccc", anchor="w").pack(side="left", padx=(5,0))

    def copy_to_clipboard(self):
        """UPGRADE: Copies formatted text to system clipboard"""
        if not self.assignments:
            return
        
        text_output = f"Subject: {self.subject_value}\n" if self.subject_value else ""
        text_output += f"Deadline: {self.deadline_value}\n\n" if self.deadline_value else "\n"
        
        grouped_results = {}
        for group, member, task in self.assignments:
            grouped_results.setdefault(group, []).append((member, task))
            
        sorted_groups = sorted(grouped_results.keys(), key=lambda g: (g.split()[0], int(g.split()[1]) if g.startswith("Group") and g.split()[1].isdigit() else g))

        for group in sorted_groups:
            text_output += f"[{group}]\n"
            for member, task in grouped_results[group]:
                text_output += f"- {member}: {task}\n"
            text_output += "\n"
        
        self.clipboard_clear()
        self.clipboard_append(text_output)
        messagebox.showinfo("Copied", "Assignments copied to clipboard!")

    def save_results(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text File", "*.txt"), ("JSON Files", "*.json")], 
            title="Save Assignments"
        )
        if not file_path: return

        if file_path.endswith(".json"):
            assignments_data = [{"Group": g, "Member": m, "Task": t} for g, m, t in self.assignments]
            output_data = {
                "Subject": self.subject_value or "",
                "Deadline": self.deadline_value or "Not set",
                "Assignments": assignments_data
            }
            try:
                with open(file_path, "w") as f:
                    json.dump(output_data, f, indent=4)
                messagebox.showinfo("Success", "Saved JSON successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
        else:
            #Save as Text
            try:
                with open(file_path, "w") as f:
                    f.write(f"Subject: {self.subject_value or 'N/A'}\n")
                    f.write(f"Deadline: {self.deadline_value or 'N/A'}\n")
                    f.write("-" * 30 + "\n\n")
                    
                    grouped_results = {}
                    for group, member, task in self.assignments:
                        grouped_results.setdefault(group, []).append((member, task))
                    
                    sorted_groups = sorted(grouped_results.keys(), key=lambda g: (g.split()[0], int(g.split()[1]) if g.startswith("Group") and g.split()[1].isdigit() else g))

                    for group in sorted_groups:
                        f.write(f"{group}\n")
                        for member, task in grouped_results[group]:
                            f.write(f"  - {member}: {task}\n")
                        f.write("\n")
                messagebox.showinfo("Success", "Saved Text File successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

if __name__ == "__main__":
    app = GroupWiseApp()
    app.mainloop()
