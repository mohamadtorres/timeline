import tkinter as tk
from tkinter import ttk, messagebox
from app.models import Project, Event

class EventsFrame(ttk.Frame):
    def __init__(self, master, project: Project | None):
        super().__init__(master, padding=12)
        self.project = project
        self._build()

    def _build(self):
        ttk.Label(self, text="Events", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 8))

        self.list = tk.Listbox(self, height=10)
        self.list.pack(fill="both", expand=True)

        form = ttk.Frame(self)
        form.pack(fill="x", pady=8)

        ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_var).grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(form, text="Date (YYYY-MM-DD)").grid(row=0, column=2, sticky="w")
        self.date_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.date_var, width=14).grid(row=0, column=3, sticky="w", padx=6)

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="nw", pady=(6,0))
        self.desc = tk.Text(form, height=4, wrap="word")
        self.desc.grid(row=1, column=1, columnspan=3, sticky="ew", padx=6, pady=(6,0))

        form.columnconfigure(1, weight=1)

        btns = ttk.Frame(self)
        btns.pack(fill="x")
        ttk.Button(btns, text="Add / Update", command=self.add_or_update).pack(side="left")
        ttk.Button(btns, text="Delete selected", command=self.delete_selected).pack(side="left", padx=6)
        ttk.Button(btns, text="Clear", command=self._clear).pack(side="left")

        self.list.bind("<<ListboxSelect>>", self._on_select)
        self.reload()

    def _on_select(self, _evt=None):
        i = self._selected_index()
        if i is None: return
        ev = self.project.events[i]
        self.title_var.set(ev.title)
        self.date_var.set(ev.date)
        self.desc.delete("1.0", "end")
        self.desc.insert("1.0", ev.description)

    def _selected_index(self):
        sel = self.list.curselection()
        return sel[0] if sel else None

    def reload(self):
        if not self.project: return
        self.list.delete(0, tk.END)
        for e in self.project.events:
            left = f"{e.date} | " if e.date else ""
            self.list.insert(tk.END, f"{left}{e.title}")

    def add_or_update(self):
        if not self.project: return
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Events", "Title is required.")
            return
        date = self.date_var.get().strip()
        desc = self.desc.get("1.0", "end").strip()
        i = self._selected_index()
        if i is None:
            self.project.events.append(Event(title=title, description=desc, date=date))
        else:
            e = self.project.events[i]
            e.title, e.description, e.date = title, desc, date
        self.reload()
        self._clear()

    def delete_selected(self):
        if not self.project: return
        i = self._selected_index()
        if i is None: return
        self.project.events.pop(i)
        self.reload()
        self._clear()

    def _clear(self):
        self.title_var.set("")
        self.date_var.set("")
        self.desc.delete("1.0", "end")
        self.list.selection_clear(0, tk.END)

    def sync_to_model(self):
        pass
