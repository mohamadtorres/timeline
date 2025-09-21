from __future__ import annotations
from typing import List, Optional
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

        add_btn.clicked.connect(self.add_item)
        del_btn.clicked.connect(self.delete_selected)

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
    """
    Events med stöd för:
    - Add
    - Delete selected
    - Dubbelklick på item => ladda in i formuläret (edit mode)
    - Save Changes (uppdaterar valt item)
    - Clear (avbryt redigering / töm formulär)
    """
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
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.add_btn = QPushButton("Add Event")
        self.clear_btn = QPushButton("Clear")
        self.del_btn = QPushButton("Delete selected")

        self.add_btn.clicked.connect(self.add_or_save)
        self.clear_btn.clicked.connect(self.clear_form)
        self.del_btn.clicked.connect(self.delete_selected)

        self.list.itemDoubleClicked.connect(self.load_for_edit)

        form = QVBoxLayout()
        form.addWidget(QLabel("Title"))
        form.addWidget(self.title_input)
        form.addWidget(QLabel("Description"))
        form.addWidget(self.desc_input)
        form.addWidget(QLabel("Date"))
        form.addWidget(self.date_input)

        buttons = QHBoxLayout()
        buttons.addWidget(self.add_btn)
        buttons.addWidget(self.clear_btn)
        buttons.addStretch(1)
        buttons.addWidget(self.del_btn)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.list)
        layout.addLayout(buttons)

        self._edit_row: Optional[int] = None


    @staticmethod
    def _compose_label(date: str, title: str, desc: str) -> str:
        """Format we render to the list: 'YYYY-MM-DD | Title – Preview' (date can be empty)."""
        left = date.strip()
        preview = _shorten(desc.strip())
        if left:
            return f"{left} | {title.strip()} – {preview}"
        return f"{title.strip()} – {preview}"

    @staticmethod
    def _split_label(label: str) -> tuple[str, str, str]:
        """
        Motsatsen till _compose_label. Returnerar (date, title, descPreview).
        (descPreview är förkortad version, originaltexten har vi inte kvar i listan.)
        """
        date = ""
        rest = label
        if " | " in label:
            date, rest = label.split(" | ", 1)
        title = rest
        desc = ""
        if " – " in rest:
            title, desc = rest.split(" – ", 1)
        return date.strip(), title.strip(), desc.strip()

    def clear_form(self):
        self.title_input.clear()
        self.desc_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self._edit_row = None
        self.add_btn.setText("Add Event")


    def load_for_edit(self, item: QListWidgetItem):
        """Dubbelklick på list-item laddar formuläret för redigering."""
        row = self.list.row(item)
        date, title, desc_preview = self._split_label(item.text())
        self.title_input.setText(title)
        self.desc_input.setPlainText(desc_preview)
        if date:
            try:
                y, m, d = [int(p) for p in date.split("-")]
                self.date_input.setDate(QDate(y, m, d))
            except Exception:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
        self._edit_row = row
        self.add_btn.setText("Save Changes")

    def add_or_save(self):
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        if not title:
            QMessageBox.warning(self, "Missing title", "Please enter a title for the event.")
            return

        label = self._compose_label(date, title, desc)

        if self._edit_row is None:
            self.list.addItem(QListWidgetItem(label))
        else:
            item = self.list.item(self._edit_row)
            if item is not None:
                item.setText(label)

        self.clear_form()

    def delete_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))
        self.clear_form()

    def values(self) -> List[Event]:
        """
        Transformera rad-text tillbaka till Event-objekt.
        Obs: beskrivningen som sparas är previewn vi har i listan (MVP).
        """
        result: List[Event] = []
        for i in range(self.list.count()):
            t = self.list.item(i).text()
            date, title, desc = self._split_label(t)
            result.append(Event(title=title, description=desc, date=date))
        return result
