import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
import os

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image converter")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.cancel_all = False  # Flag to track if the user cancels all conversions
        
        # Frame for controls
        self.frame_controls = ttk.Frame(root)
        self.frame_controls.pack(pady=5, padx=5, fill=tk.X)
        
        self.btn_select = ttk.Button(self.frame_controls, text="Select files", command=self.select_files)
        self.btn_select.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.label_format = ttk.Label(self.frame_controls, text="Target format:")
        self.label_format.pack(side=tk.LEFT, padx=5)
        
        self.format_var = tk.StringVar()
        self.combo_format = ttk.Combobox(self.frame_controls, textvariable=self.format_var, state="readonly")
        self.combo_format['values'] = ("webp", "jpg", "png")
        self.combo_format.current(0)
        self.combo_format.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.frame_buttons = ttk.Frame(root)
        self.frame_buttons.pack(pady=5, fill=tk.X)
        
        self.btn_convert = ttk.Button(self.frame_buttons, text="Convert to selected format", command=self.convert_images, state=tk.DISABLED)
        self.btn_convert.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.btn_clear = ttk.Button(self.frame_buttons, text="Clear list", command=self.clear_list)
        self.btn_clear.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.tree = ttk.Treeview(root, columns=("Filename", "Extension", "Status"), show="headings")
        self.tree.heading("Filename", text="Filename")
        self.tree.heading("Extension", text="Extension")
        self.tree.heading("Status", text="Status")
        self.tree.column("Filename", width=200)
        self.tree.column("Extension", width=80)
        self.tree.column("Status", width=120)
        self.tree.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)
        
        # Context menu for right-click delete
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Remove from list", command=self.remove_selected_file)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Label for conversion status
        self.progress_label = tk.Label(root, text="", anchor="center")
        self.progress_label.pack()
        
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=5)
        
        self.files = []
    
    def select_files(self):
        selected_files = filedialog.askopenfilenames(
            filetypes=[("Images", "*.webp;*.jpg;*.jpeg;*.png;*.svg"), ("All Files", "*.*")]
        )
        
        if selected_files:
            self.files = list(selected_files)
            self.tree.delete(*self.tree.get_children())
            
            for file in self.files:
                filename = os.path.basename(file)
                ext = os.path.splitext(file)[1].replace(".", "")
                self.tree.insert("", tk.END, values=(filename, ext, ""))
        
        self.btn_convert.config(state=tk.NORMAL if self.files else tk.DISABLED)
    
    def convert_images(self):
        if not self.files:
            return

        self.progress_label.config(text="Converting, please wait...")
        self.progress["value"] = 0
        self.cancel_all = False

        target_format = self.format_var.get()
        total_files = len(self.files)

        for i, (item, file) in enumerate(zip(self.tree.get_children(), self.files)):
            if self.cancel_all:
                self.tree.item(item, values=(self.tree.item(item, "values")[0], self.tree.item(item, "values")[1], "Canceled"))
                continue

            current_ext = self.tree.item(item, "values")[1]
            if current_ext.lower() == target_format.lower():
                self.tree.item(item, values=(self.tree.item(item, "values")[0], current_ext, "Already in selected format"))
            else:
                new_file = os.path.splitext(file)[0] + f".{target_format}"

                if os.path.exists(new_file):
                    counter = 1
                    alternate_name = os.path.splitext(file)[0] + f"_{counter}.{target_format}"
                    while os.path.exists(alternate_name):
                        alternate_name = os.path.splitext(file)[0] + f"_{counter}.{target_format}"
                        counter += 1
                    choice = messagebox.askyesnocancel(
                        "File Exists", 
                        f"The file '{os.path.basename(new_file)}' already exists.\n\nYes - Save as '{alternate_name}'\nNo - Skip this file\nCancel - Stop converting remaining files"
                    )
                    if choice is None:
                        self.cancel_all = True
                        self.progress_label.config(text="Conversion canceled")
                        return
                    elif not choice:
                        self.tree.item(item, values=(self.tree.item(item, "values")[0], current_ext, "Skipped"))
                        continue
                    else:
                        new_file = alternate_name

                try:
                    img = Image.open(file)
                    img.save(new_file, format=target_format.upper())
                    self.tree.item(item, values=(self.tree.item(item, "values")[0], current_ext, "Converted"))
                except Exception:
                    self.tree.item(item, values=(self.tree.item(item, "values")[0], current_ext, "Error"))

            self.progress["value"] = ((i + 1) / total_files) * 100
            self.root.update_idletasks()

        if not self.cancel_all:
            self.progress_label.config(text="Conversion completed")
    
    def clear_list(self):
        self.tree.delete(*self.tree.get_children())
        self.progress["value"] = 0
        self.files = []
        self.btn_convert.config(state=tk.DISABLED)
        self.cancel_all = False
        self.progress_label.config(text="")

    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def remove_selected_file(self):
        selected_item = self.tree.selection()
        if selected_item:
            filename = self.tree.item(selected_item, "values")[0]
            self.tree.delete(selected_item)
            self.files = [f for f in self.files if os.path.basename(f) != filename]
            self.btn_convert.config(state=tk.NORMAL if self.files else tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()
