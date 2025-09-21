from __future__ import annotations
from typing import List, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel, QComboBox
)
from ..models import Event

def _date_key(s: str) -> str:
    return s if s else "9999-99-99"

class TimelineTab(QWidget):
    def __init__(self,
                 get_events_fn: Callable[[], List[Event]],
                 get_characters_fn: Callable[[], List[str]],
                 get_places_fn: Callable[[], List[str]]):
        """
        get_events_fn: callable som returnerar List[Event] (hämtas från EventsTab.values)
        get_characters_fn / get_places_fn: för att bygga filter-listor
        """
        super().__init__()
        self.get_events_fn = get_events_fn
        self.get_characters_fn = get_characters_fn
        self.get_places_fn = get_places_fn

        self.char_filter = QComboBox()
        self.place_filter = QComboBox()
        self._refresh_filters()

        self.char_filter.currentIndexChanged.connect(self.refresh)
        self.place_filter.currentIndexChanged.connect(self.refresh)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Date", "Title", "Place", "Characters", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)

        top = QHBoxLayout()
        top.addWidget(QLabel("Filter Character:"))
        top.addWidget(self.char_filter)
        top.addSpacing(12)
        top.addWidget(QLabel("Filter Place:"))
        top.addWidget(self.place_filter)
        top.addStretch(1)
        top.addWidget(self.refresh_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table)

        self.refresh()

    def _refresh_filters(self):
        """Fyll comboboxar utan att trigga currentIndexChanged."""
        current_char = self.char_filter.currentText() if self.char_filter.count() else ""
        self.char_filter.blockSignals(True)
        try:
            self.char_filter.clear()
            self.char_filter.addItem("(All)")
            for c in self.get_characters_fn():
                self.char_filter.addItem(c)
            if current_char:
                idx = self.char_filter.findText(current_char)
                self.char_filter.setCurrentIndex(idx if idx >= 0 else 0)
            else:
                self.char_filter.setCurrentIndex(0)
        finally:
            self.char_filter.blockSignals(False)

        current_place = self.place_filter.currentText() if self.place_filter.count() else ""
        self.place_filter.blockSignals(True)
        try:
            self.place_filter.clear()
            self.place_filter.addItem("(All)")
            for p in self.get_places_fn():
                self.place_filter.addItem(p)
            if current_place:
                idx = self.place_filter.findText(current_place)
                self.place_filter.setCurrentIndex(idx if idx >= 0 else 0)
            else:
                self.place_filter.setCurrentIndex(0)
        finally:
            self.place_filter.blockSignals(False)

    def refresh(self):
        self._refresh_filters()

        events: List[Event] = self.get_events_fn()
        events = sorted(events, key=lambda e: _date_key(e.date))

        c_filter = self.char_filter.currentText()
        p_filter = self.place_filter.currentText()

        def visible(ev: Event) -> bool:
            if c_filter and c_filter != "(All)":
                if c_filter not in (ev.characters or []):
                    return False
            if p_filter and p_filter != "(All)":
                if (ev.place or "") != p_filter:
                    return False
            return True

        filtered = [e for e in events if visible(e)]

        self.table.setRowCount(len(filtered))
        for row, ev in enumerate(filtered):
            chars = ", ".join(ev.characters or [])
            self.table.setItem(row, 0, QTableWidgetItem(ev.date))
            self.table.setItem(row, 1, QTableWidgetItem(ev.title))
            self.table.setItem(row, 2, QTableWidgetItem(ev.place))
            self.table.setItem(row, 3, QTableWidgetItem(chars))
            self.table.setItem(row, 4, QTableWidgetItem(ev.description))
