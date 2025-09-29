from __future__ import annotations
from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from ..models import Event

def _date_key(s: str) -> str:
    return s if s else "9999-99-99"

class TimelineTab(QWidget):
    def __init__(self, get_events_fn):
        """
        get_events_fn: callable som returnerar List[Event] (hämtas från EventsTab.values)
        """
        super().__init__()
        self.get_events_fn = get_events_fn

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date(s)", "Title", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)

        top = QHBoxLayout()
        top.addStretch(1)
        top.addWidget(self.refresh_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        events: List[Event] = self.get_events_fn()
        # Sort by start_date
        events = sorted(events, key=lambda e: _date_key(getattr(e, "start_date", "")))
        self.table.setRowCount(len(events))
        for row, ev in enumerate(events):
            # Format date(s)
            start = getattr(ev, "start_date", "")
            end = getattr(ev, "end_date", "")
            if start and end and end != start:
                date_str = f"{start} – {end}"
            elif start:
                date_str = start
            else:
                date_str = ""
            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(ev.title))
            self.table.setItem(row, 2, QTableWidgetItem(ev.description))