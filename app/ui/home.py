import tkinter as tk
from tkinter import ttk

class HomeFrame(ttk.Frame):
    def __init__(self, master, list_projects_cb, open_cb, create_cb):
        super().__init__(master, padding=16)
        self.list_projects_cb = list_projects_cb
        self.open_cb = open_cb
        self.create_cb = create_cb

        title = ttk.Label(self, text="timeline – choose project", font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w", pady=(0, 12))

        self.projects = tk.Listbox(self, height=10)
        self.projects.pack(fill="x", pady=(0, 8))
        self.refresh_list()

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=(0, 16))
        ttk.Button(btns, text="Open selected", command=self._open_selected).pack(side="left")
        ttk.Button(btns, text="Refresh", command=self.refresh_list).pack(side="left", padx=8)

        sep = ttk.Separator(self)
        sep.pack(fill="x", pady=12)

        new_lbl = ttk.Label(self, text="Create new project:")
        new_lbl.pack(anchor="w")
        row = ttk.Frame(self)
        row.pack(fill="x", pady=(4, 0))
        self.name_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.name_var).pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Create", command=self._create).pack(side="left", padx=8)

    def refresh_list(self):
        self.projects.delete(0, tk.END)
        for name in self.list_projects_cb():
            self.projects.insert(tk.END, name)

    def _open_selected(self):
        try:
            idx = self.projects.curselection()[0]
        except IndexError:
            return
        name = self.projects.get(idx)
        self.open_cb(name)

    def _create(self):
        name = self.name_var.get().strip()
        if not name:
            return
        self.create_cb(name)
