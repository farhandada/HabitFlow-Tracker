import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json

class HabitTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit Tracker")
        self.habits = {}
        self.load_data()
        self.create_widgets()
        self.check_reset()

    def create_widgets(self):
        title_frame = tk.Frame(self.root)
        title_frame.grid(row=0, column=0, columnspan=2, pady=10)
        
        title_label = tk.Label(title_frame, text="Habit Tracker", font=("Helvetica", 20, "bold"))
        title_label.pack()

        self.input_frame = tk.Frame(self.root, padx=10, pady=10)
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.input_frame.grid_remove()  # Hide the input frame initially

        habit_label = tk.Label(self.input_frame, text="Habit (e.g., Exercise):")
        habit_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.habit_entry = tk.Entry(self.input_frame)
        self.habit_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        target_label = tk.Label(self.input_frame, text="Target (e.g., 30):")
        target_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.target_entry = tk.Entry(self.input_frame)
        self.target_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        measurement_label = tk.Label(self.input_frame, text="Measurement (optional, e.g., Minutes):")
        measurement_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.measurement_entry = tk.Entry(self.input_frame)
        self.measurement_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.add_habit_button = tk.Button(self.input_frame, text="Add Habit", command=self.add_habit)
        self.add_habit_button.grid(row=3, column=0, pady=10)

        self.cancel_button = tk.Button(self.input_frame, text="Cancel", command=self.hide_input_form)
        self.cancel_button.grid(row=3, column=1, pady=10)

        self.input_frame.columnconfigure(1, weight=1)

        self.show_input_button = tk.Button(self.root, text="Add Habit", command=self.show_input_form)
        self.show_input_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.habits_frame = tk.Frame(self.root, padx=10, pady=10)
        self.habits_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.display_habits()

    def show_input_form(self):
        self.show_input_button.grid_remove()  # Hide the "Add Habit" button
        self.input_frame.grid()  # Show the input form
        self.show_suggestions()  # Show habit suggestions

    def hide_input_form(self):
        self.input_frame.grid_remove()  # Hide the input form
        self.show_input_button.grid()  # Show the "Add Habit" button again
        self.hide_suggestions()  # Hide habit suggestions

    def add_habit(self):
        habit = self.habit_entry.get()
        target = self.target_entry.get()
        measurement = self.measurement_entry.get()
        if habit:
            if not target.isdigit():
                target = 1
            else:
                target = int(target)
            self.habits[habit] = {"target": target, "count": 0, "measurement": measurement, "congratulated": False}
            self.habit_entry.delete(0, tk.END)
            self.target_entry.delete(0, tk.END)
            self.measurement_entry.delete(0, tk.END)
            self.hide_input_form()
            self.display_habits()
            self.save_data()
        else:
            messagebox.showwarning("Input Error", "Please enter a valid habit.")

    def display_habits(self):
        for widget in self.habits_frame.winfo_children():
            widget.destroy()

        for habit, data in self.habits.items():
            habit_frame = tk.Frame(self.habits_frame, pady=5)
            habit_frame.pack(fill='x')

            # Handle missing 'measurement' key
            measurement = data.get('measurement', '')

            habit_label = tk.Label(habit_frame, text=f"{habit} ({data['target']} {measurement})", width=30, anchor='w')
            habit_label.pack(side='left')

            progress = tk.DoubleVar()
            progress_bar = ttk.Progressbar(habit_frame, variable=progress, maximum=data['target'], length=200)
            progress_bar.pack(side='left', fill='x', expand=True, padx=10)
            progress.set(data['count'] if data['count'] <= data['target'] else data['target'])

            percentage_label = tk.Label(habit_frame, text=f"{(data['count']/data['target']) * 100:.1f}% ({data['count']}/{data['target']})")
            percentage_label.pack(side='left')

            increment_button = tk.Button(habit_frame, text="+", command=lambda h=habit: self.increment_progress(h))
            increment_button.pack(side='left')

            edit_count_button = tk.Button(habit_frame, text="Edit Count", command=lambda h=habit: self.override_progress(h))
            edit_count_button.pack(side='left')

            reset_button = tk.Button(habit_frame, text="Reset", command=lambda h=habit: self.reset_habit(h))
            reset_button.pack(side='left')

            delete_button = tk.Button(habit_frame, text="Delete", command=lambda h=habit: self.delete_habit(h))
            delete_button.pack(side='left')

            if data['count'] >= data['target']:
                habit_label.config(fg="green")

    def increment_progress(self, habit):
        self.habits[habit]['count'] += 1
        if self.habits[habit]['count'] >= self.habits[habit]['target'] and not self.habits[habit]['congratulated']:
            self.habits[habit]['congratulated'] = True
            self.congratulate_user()
        self.save_data()
        self.display_habits()

    def override_progress(self, habit):
        def set_progress():
            try:
                new_count = int(override_entry.get())
                if new_count >= 0:
                    self.habits[habit]['count'] = new_count
                    self.habits[habit]['congratulated'] = new_count >= self.habits[habit]['target']
                    self.save_data()
                    self.display_habits()
                    override_window.destroy()
                    if self.habits[habit]['count'] >= self.habits[habit]['target'] and not self.habits[habit]['congratulated']:
                        self.habits[habit]['congratulated'] = True
                        self.congratulate_user()
                else:
                    messagebox.showwarning("Input Error", "Please enter a non-negative number.")
            except ValueError:
                messagebox.showwarning("Input Error", "Please enter a valid number.")

        override_window = tk.Toplevel(self.root)
        override_window.title("Edit Count")
        override_label = tk.Label(override_window, text=f"Set progress for '{habit}':")
        override_label.pack(pady=10)
        override_entry = tk.Entry(override_window)
        override_entry.pack(pady=5)
        set_button = tk.Button(override_window, text="Set", command=set_progress)
        set_button.pack(pady=10)

    def reset_habit(self, habit):
        self.habits[habit]['count'] = 0
        self.habits[habit]['congratulated'] = False
        self.save_data()
        self.display_habits()

    def delete_habit(self, habit):
        if messagebox.askyesno("Delete Habit", f"Are you sure you want to delete the habit '{habit}'?"):
            del self.habits[habit]
            self.display_habits()
            self.save_data()

    def save_data(self):
        with open("habits.json", "w") as file:
            json.dump(self.habits, file)

    def load_data(self):
        try:
            with open("habits.json", "r") as file:
                self.habits = json.load(file)
        except FileNotFoundError:
            self.habits = {}

    def check_reset(self):
        # Reset the habits daily
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        try:
            with open("last_reset.txt", "r") as file:
                last_reset = file.read()
        except FileNotFoundError:
            last_reset = ""

        if last_reset != today:
            for habit in self.habits:
                self.habits[habit]['count'] = 0
                self.habits[habit]['congratulated'] = False
            self.save_data()
            with open("last_reset.txt", "w") as file:
                file.write(today)
            self.display_habits()

    def show_suggestions(self):
        self.suggestions_frame = tk.Frame(self.root, padx=10, pady=10)
        self.suggestions_frame.grid(row=3, column=0, columnspan=2, sticky="ew")

        suggestions_label = tk.Label(self.suggestions_frame, text="Habit Suggestions:", font=("Helvetica", 14))
        suggestions_label.pack(anchor='w')

        suggestions = [
            "Drink 8 glasses of water",
            "Exercise for 30 minutes",
            "Read for 20 minutes",
            "Meditate for 10 minutes",
            "Walk 10,000 steps",
            "Write a journal entry"
        ]

        for suggestion in suggestions:
            suggestion_label = tk.Label(self.suggestions_frame, text=f"- {suggestion}", anchor='w')
            suggestion_label.pack(anchor='w')

    def hide_suggestions(self):
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        self.suggestions_frame.grid_remove()

    def congratulate_user(self):
        congrats_window = tk.Toplevel(self.root)
        congrats_window.title("Congratulations!")
        congrats_label = tk.Label(congrats_window, text="Good job! You completed your task!", font=("Helvetica", 14))
        congrats_label.pack(pady=20)
        ok_button = tk.Button(congrats_window, text="OK", command=congrats_window.destroy)
        ok_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerApp(root)
    root.mainloop()
