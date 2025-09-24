import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from app.models import Project, Character

class CharactersFrame(ttk.Frame):
    def __init__(self, master, project: Project | None):
        super().__init__(master, padding=12)
        self.project = project
        self._build()

    def _build(self):
        title = ttk.Label(self, text="Characters", font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", pady=(0, 8))

        self.list = tk.Listbox(self, height=10)
        self.list.pack(fill="both", expand=True)

        form = ttk.Frame(self)
        form.pack(fill="x", pady=8)
        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(form, text="Color").grid(row=0, column=2, sticky="w")
        self.color_var = tk.StringVar(value="#4e79a7")
        self.color_btn = ttk.Button(form, text="Pick…", command=self._pick_color)
        self.color_btn.grid(row=0, column=3, padx=6)

        form.columnconfigure(1, weight=1)

        btns = ttk.Frame(self)
        btns.pack(fill="x")
        ttk.Button(btns, text="Add / Update", command=self.add_or_update).pack(side="left")
        ttk.Button(btns, text="Delete selected", command=self.delete_selected).pack(side="left", padx=6)
        ttk.Button(btns, text="Clear", command=self._clear).pack(side="left")

        self.list.bind("<<ListboxSelect>>", self._on_select)

        self.reload()

    def _pick_color(self):
        c = colorchooser.askcolor(color=self.color_var.get())
        if c and c[1]:
            self.color_var.set(c[1])

    def _on_select(self, _evt=None):
        i = self._selected_index()
        if i is None:
            return
        ch = self.project.characters[i]
        self.name_var.set(ch.name)
        self.color_var.set(ch.color)

    def _selected_index(self):
        sel = self.list.curselection()
        return sel[0] if sel else None

    def reload(self):
        if not self.project: return
        self.list.delete(0, tk.END)
        for ch in self.project.characters:
            self.list.insert(tk.END, f"{ch.name}  [{ch.color}]")

    def add_or_update(self):
        if not self.project: return
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Characters", "Name is required.")
            return
        color = self.color_var.get().strip() or "#4e79a7"
        i = self._selected_index()
        if i is None:
            if any(c.name.lower() == name.lower() for c in self.project.characters):
                messagebox.showinfo("Characters", "Character already exists.")
                return
            self.project.characters.append(Character(name=name, color=color))
        else:
            self.project.characters[i].name = name
            self.project.characters[i].color = color
        self.reload()
        self._clear()

    def delete_selected(self):
        if not self.project: return
        i = self._selected_index()
        if i is None: return
        self.project.characters.pop(i)
        self.reload()
        self._clear()

    def _clear(self):
        self.name_var.set("")
        self.color_var.set("#4e79a7")
        self.list.selection_clear(0, tk.END)

    def sync_to_model(self):
        pass
