import tkinter as tk
from tkinter import filedialog, messagebox
import os
import tkinter.font as tkFont
from spellchecker import SpellChecker



# Initialize main window
root = tk.Tk()
root.title("Ullas Text Editor")
root.geometry("1000x800")


# Default font settings
current_font_family = tk.StringVar()
current_font_size = tk.IntVar()

current_font_family.set("Arial")
current_font_size.set(15)

toolbar = tk.Frame(root)
toolbar.pack(side=tk.TOP, fill=tk.X)


# Font Family Dropdown
font_families = tkFont.families()
font_dropdown = tk.OptionMenu(toolbar, current_font_family, *font_families, command=lambda _: update_font())
font_dropdown.config(width=15)
font_dropdown.pack(side=tk.LEFT, padx=5)

# Font Size Spinbox
size_spinbox = tk.Spinbox(toolbar, from_=8, to=72, textvariable=current_font_size, command=lambda: update_font(), width=7)
size_spinbox.pack(side=tk.LEFT, padx=5)

spell_button = tk.Button(toolbar, text="Check Spelling", command=lambda:check_spelling())
spell_button.pack(side=tk.LEFT, padx=5)


# Create a Frame to hold text + scrollbar
text_frame = tk.Frame(root)
text_frame.pack(fill=tk.BOTH, expand=True)


# Status Bar
status_bar = tk.Label(root, text="Words: 0  |  Characters: 0", anchor='w')
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Scrollbar
scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Text widget (without hardcoded font)
text_area = tk.Text(text_frame, yscrollcommand=scrollbar.set, undo=True)
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Configure scrollbar to scroll text area
scrollbar.config(command=text_area.yview)

# ✅ Set font using the current dropdown/spinbox selection
text_area.config(font=(current_font_family.get(), current_font_size.get()))

text_area.tag_config("misspelled", underline=True, foreground="red")



# Track the current file path
file_path = None

dark_mode = False


# ---- FILE FUNCTIONS ---- #

def new_file():
    global file_path
    file_path = None
    text_area.delete(1.0, tk.END)
    root.title("Untitled - Ullas Text Editor")

def open_file():
    global file_path
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if path:
        file_path = path
        with open(path, "r") as file:
            content = file.read()
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, content)
        root.title(os.path.basename(path) + " - Ullas Text Editor")

def save_file():
    global file_path
    if file_path:
        with open(file_path, "w") as file:
            file.write(text_area.get(1.0, tk.END))
    else:
        save_as_file()

def save_as_file():
    global file_path
    path = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if path:
        file_path = path
        with open(path, "w") as file:
            file.write(text_area.get(1.0, tk.END))
        root.title(os.path.basename(path) + " - Ullas Text Editor")

read_only = tk.BooleanVar()
read_only.set(False)

def toggle_read_only():
    if read_only.get():
        text_area.config(state="disabled")
    else:
        text_area.config(state="normal")


def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    if dark_mode:
        text_area.config(bg="#1e1e1e", fg="#dcdcdc", insertbackground="white")
    else:
        text_area.config(bg="white", fg="black", insertbackground="black")


def update_status(event=None):
    text = text_area.get(1.0, tk.END)
    words = len(text.split())
    characters = len(text) - 1  # -1 to remove the extra newline at the end
    status_bar.config(text=f"Words: {words}  |  Characters: {characters}")

def find_and_replace():
    def replace():
        find_text = find_entry.get()
        replace_text = replace_entry.get()
        content = text_area.get(1.0, tk.END)
        new_content = content.replace(find_text, replace_text)
        text_area.delete(1.0, tk.END)
        text_area.insert(1.0, new_content)
        popup.destroy()

    popup = tk.Toplevel(root)
    popup.title("Find and Replace")
    popup.geometry("300x200")
    popup.transient(root)
    popup.grab_set()

    # Use a Frame for better layout
    frame = tk.Frame(popup, padx=10, pady=10)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Find:").grid(row=0, column=0, sticky="w")
    find_entry = tk.Entry(frame, width=30)
    find_entry.grid(row=1, column=0, padx=5, pady=(0, 10))

    tk.Label(frame, text="Replace with:").grid(row=2, column=0, sticky="w")
    replace_entry = tk.Entry(frame, width=30)
    replace_entry.grid(row=3, column=0, padx=5, pady=(0, 10))

    replace_button = tk.Button(frame, text="Replace All", command=replace)
    replace_button.grid(row=4, column=0, pady=(10, 0), ipadx=10)

def update_font():
    new_font = (current_font_family.get(), current_font_size.get())
    text_area.config(font=new_font)

def auto_save():
    if file_path:  # Only save if the file has already been saved once
        try:
            with open(file_path, "w") as file:
                file.write(text_area.get(1.0, tk.END))
            print("Auto-saved.")
        except Exception as e:
            print("Auto-save failed:", e)
    
    # Schedule the next auto-save after 30,000ms (30 seconds)
    root.after(30000, auto_save)

def check_spelling():
    spell = SpellChecker()
    text = text_area.get("1.0", tk.END)
    words = text.split()

    text_area.tag_remove("misspelled", "1.0", tk.END)  # Clear previous highlights

    for word in words:
        if word.strip().isalpha() and word not in spell:
            start_index = "1.0"
            while True:
                start_index = text_area.search(rf"\y{word}\y", start_index, stopindex=tk.END, regexp=True)
                if not start_index:
                    break
                end_index = f"{start_index}+{len(word)}c"
                text_area.tag_add("misspelled", start_index, end_index)
                start_index = end_index


# ---- MENU BAR ---- #

menu_bar = tk.Menu(root)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_command(label="Save As", command=save_as_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

view_menu = tk.Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)
view_menu.add_checkbutton(label="Read-Only Mode", onvalue=True, offvalue=False,
                          variable=read_only, command=toggle_read_only)
menu_bar.add_cascade(label="View", menu=view_menu)

edit_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo", command=text_area.edit_undo, accelerator="Ctrl+Z")
edit_menu.add_command(label="Redo", command=text_area.edit_redo, accelerator="Ctrl+Y")
edit_menu.add_separator()

edit_menu.add_command(label="Find and Replace", command=find_and_replace)
menu_bar.add_cascade(label="Edit", menu=edit_menu)





# Attach menu bar to window
root.config(menu=menu_bar)




root.bind("<Control-n>", lambda event: new_file())
root.bind("<Control-o>", lambda event: open_file())
root.bind("<Control-s>", lambda event: save_file())
root.bind("<Control-S>", lambda event: save_as_file())  # Shift+Ctrl+S for Save As
text_area.bind("<KeyRelease>", update_status)
root.bind("<Control-z>", lambda event: text_area.edit_undo())
root.bind("<Control-y>", lambda event: text_area.edit_redo())


update_status()
auto_save()


root.mainloop()
