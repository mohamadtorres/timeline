from __future__ import annotations
from typing import List
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from ..models import Event

def _date_key(s: str) -> str:
    # Tomma datum hamnar sist
    return s if s else "9999-99-99"

class TimelineTab(QWidget):
    def __init__(self, get_events_fn):
        """
        get_events_fn: callable som returnerar List[Event] (hämtas från EventsTab.values)
        """
        super().__init__()
        self.get_events_fn = get_events_fn

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Date", "Title", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)  # type: ignore

        top = QHBoxLayout()
        top.addStretch(1)
        top.addWidget(self.refresh_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        events: List[Event] = self.get_events_fn()
        events = sorted(events, key=lambda e: _date_key(e.date))
        self.table.setRowCount(len(events))
        for row, ev in enumerate(events):
            self.table.setItem(row, 0, QTableWidgetItem(ev.date))
            self.table.setItem(row, 1, QTableWidgetItem(ev.title))
            self.table.setItem(row, 2, QTableWidgetItem(ev.description))
