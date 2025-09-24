import tkinter as tk
from tkinter import ttk, messagebox
from app.models import Project, Place

class PlacesFrame(ttk.Frame):
    def __init__(self, master, project: Project | None):
        super().__init__(master, padding=12)
        self.project = project
        self._build()

    def _build(self):
        ttk.Label(self, text="Places", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))

        self.list = tk.Listbox(self, height=10)
        self.list.pack(fill="both", expand=True)

        row = ttk.Frame(self)
        row.pack(fill="x", pady=8)
        self.name_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.name_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Add / Update", command=self.add_or_update).pack(side="left", padx=6)
        ttk.Button(row, text="Delete selected", command=self.delete_selected).pack(side="left")
        self.list.bind("<<ListboxSelect>>", self._on_select)

        self.reload()

    def _on_select(self, _evt=None):
        i = self._selected_index()
        if i is None: return
        self.name_var.set(self.project.places[i].name)

    def _selected_index(self):
        sel = self.list.curselection()
        return sel[0] if sel else None

    def reload(self):
        if not self.project: return
        self.list.delete(0, tk.END)
        for p in self.project.places:
            self.list.insert(tk.END, p.name)

    def add_or_update(self):
        if not self.project: return
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Places", "Name is required.")
            return
        i = self._selected_index()
        if i is None:
            if any(p.name.lower() == name.lower() for p in self.project.places):
                messagebox.showinfo("Places", "Place already exists.")
                return
            self.project.places.append(Place(name=name))
        else:
            self.project.places[i].name = name
        self.reload()
        self.name_var.set("")
        self.list.selection_clear(0, tk.END)

    def delete_selected(self):
        if not self.project: return
        i = self._selected_index()
        if i is None: return
        self.project.places.pop(i)
        self.reload()
        self.name_var.set("")
        self.list.selection_clear(0, tk.END)

    def sync_to_model(self):
        pass
