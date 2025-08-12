import tkinter as tk
from tkinter import messagebox, ttk

def on_submit():
    name = name_entry.get()
    gender = gender_var.get()
    language = lang_var.get()
    comments = comments_text.get("1.0", tk.END).strip()
    
    tree.insert('', tk.END, values=(name, gender, language))
    messagebox.showinfo("Submitted", f"Thank you, {name}!\nYour comment: {comments}")

def exit_app():
    root.destroy()

root = tk.Tk()
root.title("Python GUI Demo")
root.geometry("500x500")

# Name
tk.Label(root, text="Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

# Gender (Radio)
tk.Label(root, text="Gender:").pack()
gender_var = tk.StringVar(value="Male")
tk.Radiobutton(root, text="Male", variable=gender_var, value="Male").pack()
tk.Radiobutton(root, text="Female", variable=gender_var, value="Female").pack()

# Language (Dropdown)
tk.Label(root, text="Language:").pack()
lang_var = tk.StringVar(value="Python")
langs = ["Python", "Java", "C#", "JavaScript"]
tk.OptionMenu(root, lang_var, *langs).pack()

# Comments (Text area)
tk.Label(root, text="Comments:").pack()
comments_text = tk.Text(root, height=4, width=40)
comments_text.pack()

# Submit Button
tk.Button(root, text="Submit", command=on_submit).pack(pady=10)

# Treeview (Grid)
tree = ttk.Treeview(root, columns=("Name", "Gender", "Language"), show="headings")
tree.heading("Name", text="Name")
tree.heading("Gender", text="Gender")
tree.heading("Language", text="Language")
tree.pack(pady=10)

# Exit
tk.Button(root, text="Exit", command=exit_app).pack(pady=5)

root.mainloop()
