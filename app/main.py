import sys
from dataclasses import asdict
from PySide6.QtWidgets import QApplication, QWidget, QTabWidget, QVBoxLayout, QMessageBox

from .models import Character, Place, Event
from .storage import load_state, save_state
from .ui.tabs import ListTab, EventsTab
from .ui.timeline import TimelineTab
from .ui.timeline_graph import TimelineGraphTab

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("timeline – MVP with Graph Timeline")
        self.resize(1100, 720)

        state = load_state()
        char_names = [c["name"] for c in state.get("characters", [])]
        place_names = [p["name"] for p in state.get("places", [])]
        events = [Event(**e) for e in state.get("events", [])]

        self.tabs = QTabWidget()
        self.chars_tab = ListTab("Character", char_names)
        self.places_tab = ListTab("Place", place_names)

        get_chars = self.chars_tab.values
        get_places = self.places_tab.values

        self.events_tab = EventsTab(events, get_characters_fn=get_chars, get_places_fn=get_places)
        self.timeline_tab = TimelineTab(self.events_tab.values, get_characters_fn=get_chars, get_places_fn=get_places)
        self.timeline_graph_tab = TimelineGraphTab(self.events_tab.values, get_characters_fn=get_chars, get_places_fn=get_places)

        self.tabs.addTab(self.chars_tab, "Characters")
        self.tabs.addTab(self.places_tab, "Places")
        self.tabs.addTab(self.events_tab, "Events")
        self.tabs.addTab(self.timeline_tab, "Timeline")
        self.tabs.addTab(self.timeline_graph_tab, "Timeline (Graph)")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    def closeEvent(self, event):
        state = {
            "characters": [asdict(Character(name=n)) for n in self.chars_tab.values()],
            "places": [asdict(Place(name=n)) for n in self.places_tab.values()],
            "events": [asdict(e) for e in self.events_tab.values()],
        }
        try:
            save_state(state)
        except Exception as e:
            QMessageBox.critical(self, "Save failed", f"Could not save data: {e}")
        event.accept()

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
