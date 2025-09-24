import tkinter as tk
from tkinter import ttk, messagebox
from app.models import Project
from app.storage import list_projects, load_project, create_project, save_project
from app.ui.home import HomeFrame
from app.ui.characters import CharactersFrame
from app.ui.places import PlacesFrame
from app.ui.events import EventsFrame

class TimelineTkApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.project: Project | None = None

        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save", command=self.save_current)
        filemenu.add_command(label="Switch project", command=self.show_home)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        self.container = ttk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        self.home = HomeFrame(self.container,
                              list_projects_cb=list_projects,
                              open_cb=self.open_project,
                              create_cb=self.create_project)
        self.home.pack(fill="both", expand=True)

        self.notebook: ttk.Notebook | None = None

    def show_home(self):
        if self.project:
            self.save_current()
        for w in self.container.winfo_children():
            w.destroy()
        self.home = HomeFrame(self.container,
                              list_projects_cb=list_projects,
                              open_cb=self.open_project,
                              create_cb=self.create_project)
        self.home.pack(fill="both", expand=True)
        self.notebook = None
        self.project = None
        self.root.title("timeline (Tkinter)")

    def show_notebook(self):
        for w in self.container.winfo_children():
            w.destroy()
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True)

        self.characters_tab = CharactersFrame(self.notebook, self.project)
        self.places_tab = PlacesFrame(self.notebook, self.project)
        self.events_tab = EventsFrame(self.notebook, self.project)

        self.notebook.add(self.characters_tab, text="Characters")
        self.notebook.add(self.places_tab, text="Places")
        self.notebook.add(self.events_tab, text="Events")

    def open_project(self, name: str):
        proj = load_project(name)
        if not proj:
            messagebox.showerror("Open project", f"Could not open project '{name}'.")
            return
        self.project = proj
        self.root.title(f"timeline – {proj.name}")
        self.show_notebook()

    def create_project(self, name: str):
        if not name.strip():
            messagebox.showwarning("Create project", "Please enter a project name.")
            return
        self.project = create_project(name.strip())
        self.root.title(f"timeline – {self.project.name}")
        self.show_notebook()

    def save_current(self):
        if self.project:
            if self.notebook:
                self.characters_tab.sync_to_model()
                self.places_tab.sync_to_model()
                self.events_tab.sync_to_model()
            save_project(self.project)

    def on_close(self):
        if self.project:
            self.save_current()
        self.root.destroy()
