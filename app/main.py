import tkinter as tk
from .ui.app import TimelineTkApp

def main():
    root = tk.Tk()
    root.title("timeline (Tkinter)")
    root.geometry("980x640")
    app = TimelineTkApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
