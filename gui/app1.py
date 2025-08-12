import tkinter as tk
from tkinter import ttk
import random

# Sample data for countries and capitals
sample_data = [
    ("India", "New Delhi"), ("USA", "Washington, D.C."), ("UK", "London"),
    ("France", "Paris"), ("Germany", "Berlin"), ("Canada", "Ottawa"),
    ("Australia", "Canberra"), ("Japan", "Tokyo"), ("Russia", "Moscow"),
    ("Brazil", "Brasília"), ("Italy", "Rome"), ("Spain", "Madrid")
]

class CommandApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Grid Generator")

        # Multiline input field
        self.text_input = tk.Text(root, height=5, width=50)
        self.text_input.pack(pady=10)

        # Submit and Exit buttons
        button_frame = tk.Frame(root)
        button_frame.pack()

        submit_btn = tk.Button(button_frame, text="Submit", command=self.process_command)
        submit_btn.pack(side=tk.LEFT, padx=10)

        exit_btn = tk.Button(button_frame, text="Exit", command=root.quit)
        exit_btn.pack(side=tk.LEFT, padx=10)

        # Treeview (grid) to display output
        self.tree = ttk.Treeview(root, columns=("Country", "Capital"), show='headings')
        self.tree.heading("Country", text="Country")
        self.tree.heading("Capital", text="Capital")
        self.tree.pack(pady=20)

    def process_command(self):
        command = self.text_input.get("1.0", tk.END).strip().lower()

        # Clear previous rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        if "generate" in command and "country" in command and "capital" in command:
            # Try to extract number from command
            import re
            match = re.search(r'generate\s+(\d+)', command)
            if match:
                count = int(match.group(1))
                random.shuffle(sample_data)
                for country, capital in sample_data[:count]:
                    self.tree.insert('', tk.END, values=(country, capital))
            else:
                self.tree.insert('', tk.END, values=("Invalid", "Command format"))
        else:
            self.tree.insert('', tk.END, values=("Unknown", "Command"))

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = CommandApp(root)
    root.mainloop()
