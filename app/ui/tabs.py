from __future__ import annotations
from typing import List
from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox, QDateEdit
)
from ..models import Event

def _shorten(text: str, max_len: int = 60) -> str:
    text = (text or "").replace("\n", " ")
    return text if len(text) <= max_len else text[: max_len - 1] + "…"

class ListTab(QWidget):
    """Generic list tab for Characters and Places."""
    def __init__(self, label_singular: str, initial_items: List[str]):
        super().__init__()
        self.label_singular = label_singular

        self.list = QListWidget()
        for name in initial_items:
            self.list.addItem(QListWidgetItem(name))

        self.input = QLineEdit()
        self.input.setPlaceholderText(f"Add {label_singular.lower()}…")

        add_btn = QPushButton(f"Add {label_singular}")
        del_btn = QPushButton("Delete selected")

        add_btn.clicked.connect(self.add_item)        # type: ignore
        del_btn.clicked.connect(self.delete_selected) # type: ignore

        top = QHBoxLayout()
        top.addWidget(self.input)
        top.addWidget(add_btn)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        bottom.addWidget(del_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.list)
        layout.addLayout(bottom)

    def add_item(self):
        text = self.input.text().strip()
        if not text:
            return
        existing = [self.list.item(i).text().lower() for i in range(self.list.count())]
        if text.lower() in existing:
            QMessageBox.information(self, "Already exists", f"{self.label_singular} '{text}' already exists.")
            return
        self.list.addItem(QListWidgetItem(text))
        self.input.clear()

    def delete_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def values(self) -> List[str]:
        return [self.list.item(i).text() for i in range(self.list.count())]

class EventsTab(QWidget):
    def __init__(self, initial_events: List[Event]):
        super().__init__()

        self.list = QListWidget()
        for ev in initial_events:
            label = f"{(ev.date or '').strip()} | {ev.title} – {_shorten(ev.description)}".strip(" |")
            self.list.addItem(QListWidgetItem(label))

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Event title…")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Short description…")
        self.desc_input.setFixedHeight(90)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())  # default: idag
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        add_btn = QPushButton("Add Event")
        del_btn = QPushButton("Delete selected")

        add_btn.clicked.connect(self.add_event)        # type: ignore
        del_btn.clicked.connect(self.delete_selected)  # type: ignore

        form = QVBoxLayout()
        form.addWidget(QLabel("Title"))
        form.addWidget(self.title_input)
        form.addWidget(QLabel("Description"))
        form.addWidget(self.desc_input)
        form.addWidget(QLabel("Date"))
        form.addWidget(self.date_input)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(add_btn)
        buttons.addWidget(del_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.list)
        layout.addLayout(buttons)

    def add_event(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        if not title:
            QMessageBox.warning(self, "Missing title", "Please enter a title for the event.")
            return
        label = f"{date} | {title} – {_shorten(desc)}"
        self.list.addItem(QListWidgetItem(label))
        self.title_input.clear()
        self.desc_input.clear()
        self.date_input.setDate(QDate.currentDate())

    def delete_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))

    def values(self) -> List[Event]:
        result: List[Event] = []
        for i in range(self.list.count()):
            t = self.list.item(i).text()
            # Format: "YYYY-MM-DD | Title – Desc" (date kan saknas)
            date = ""
            title_desc = t
            if " | " in t:
                date, title_desc = t.split(" | ", 1)
            title = title_desc
            desc = ""
            if " – " in title_desc:
                title, desc = title_desc.split(" – ", 1)
            result.append(Event(title=title, description=desc, date=date))
        return result
