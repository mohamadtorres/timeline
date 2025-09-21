from __future__ import annotations
from typing import List, Optional, Callable
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox, QDateEdit, QComboBox
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
    Events med:
    - Add / Delete
    - Dubbelklick => redigering (form fylls)
    - Save Changes / Clear
    - Välj flera Characters (multi-select) och en Place (dropdown)
    """
    def __init__(self, initial_events: List[Event],
                 get_characters_fn: Callable[[], List[str]],
                 get_places_fn: Callable[[], List[str]]):
        super().__init__()

        self.get_characters_fn = get_characters_fn
        self.get_places_fn = get_places_fn

        self.list = QListWidget()
        for ev in initial_events:
            item = QListWidgetItem(self._compose_label(ev))
            item.setData(Qt.UserRole, {
                "title": ev.title, "description": ev.description, "date": ev.date,
                "characters": list(ev.characters or []), "place": ev.place or ""
            })
            self.list.addItem(item)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Event title…")

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Short description…")
        self.desc_input.setFixedHeight(90)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("yyyy-MM-dd")

        self.char_list = QListWidget()
        self.char_list.setSelectionMode(QListWidget.MultiSelection)

        self.place_combo = QComboBox()
        self._refresh_char_place_choices()

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

        form.addWidget(QLabel("Characters (select multiple):"))
        form.addWidget(self.char_list)
        form.addWidget(QLabel("Place:"))
        form.addWidget(self.place_combo)

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


    def _refresh_char_place_choices(self):
        self.char_list.clear()
        for name in self.get_characters_fn():
            self.char_list.addItem(QListWidgetItem(name))
        self.place_combo.clear()
        self.place_combo.addItem("")
        for p in self.get_places_fn():
            self.place_combo.addItem(p)

    @staticmethod
    def _short_characters(chars: List[str]) -> str:
        return ", ".join(chars) if chars else ""

    def _compose_label(self, ev: Event) -> str:
        left = ev.date.strip() if ev.date else ""
        base = f"{ev.title.strip()} – {_shorten(ev.description)}"
        meta = []
        if ev.place:
            meta.append(ev.place)
        if ev.characters:
            meta.append(self._short_characters(ev.characters))
        meta_str = (" (" + " • ".join(meta) + ")") if meta else ""
        return f"{left + ' | ' if left else ''}{base}{meta_str}"

    def _collect_form(self) -> Event:
        title = self.title_input.text().strip()
        desc = self.desc_input.toPlainText().strip()
        date = self.date_input.date().toString("yyyy-MM-dd")
        chars = [i.text() for i in self.char_list.selectedItems()]
        place = self.place_combo.currentText().strip()
        return Event(title=title, description=desc, date=date, characters=chars, place=place)

    def _fill_form(self, ev: Event):
        self.title_input.setText(ev.title)
        self.desc_input.setPlainText(ev.description)
        if ev.date:
            try:
                y, m, d = [int(p) for p in ev.date.split("-")]
                self.date_input.setDate(QDate(y, m, d))
            except Exception:
                self.date_input.setDate(QDate.currentDate())
        else:
            self.date_input.setDate(QDate.currentDate())
        self._refresh_char_place_choices()
        want = set(ev.characters or [])
        for i in range(self.char_list.count()):
            item = self.char_list.item(i)
            item.setSelected(item.text() in want)
        idx = max(0, self.place_combo.findText(ev.place or ""))
        self.place_combo.setCurrentIndex(idx)

    def clear_form(self):
        self.title_input.clear()
        self.desc_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self._refresh_char_place_choices()
        for i in range(self.char_list.count()):
            self.char_list.item(i).setSelected(False)
        self.place_combo.setCurrentIndex(0)
        self._edit_row = None
        self.add_btn.setText("Add Event")


    def load_for_edit(self, item: QListWidgetItem):
        row = self.list.row(item)
        payload = item.data(Qt.UserRole)
        if isinstance(payload, dict):
            ev = Event(
                title=payload.get("title", ""),
                description=payload.get("description", ""),
                date=payload.get("date", ""),
                characters=list(payload.get("characters", []) or []),
                place=payload.get("place", "") or "",
            )
        else:
            ev = self._parse_from_label(item.text())
        self._edit_row = row
        self.add_btn.setText("Save Changes")
        self._fill_form(ev)

    def add_or_save(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Missing title", "Please enter a title for the event.")
            return

        ev = self._collect_form()
        label = self._compose_label(ev)
        payload = {
            "title": ev.title, "description": ev.description, "date": ev.date,
            "characters": ev.characters, "place": ev.place
        }

        if self._edit_row is None:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, payload)
            self.list.addItem(item)
        else:
            item = self.list.item(self._edit_row)
            if item is not None:
                item.setText(label)
                item.setData(Qt.UserRole, payload)

        self.clear_form()

    def delete_selected(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.row(item))
        self.clear_form()

    def _parse_from_label(self, label: str) -> Event:
        date = ""
        rest = label
        if " | " in label:
            date, rest = label.split(" | ", 1)
        title = rest
        desc = ""
        if " – " in rest:
            title, desc = rest.split(" – ", 1)
        return Event(title=title.strip(), description=desc.strip(), date=date.strip(), characters=[], place="")

    def values(self) -> List[Event]:
        """
        Läs tillbaka full payload per rad (om finns),
        annars fallback till parsing av label.
        """
        result: List[Event] = []
        for i in range(self.list.count()):
            item = self.list.item(i)
            payload = item.data(Qt.UserRole)
            if isinstance(payload, dict):
                result.append(Event(
                    title=payload.get("title", ""),
                    description=payload.get("description", ""),
                    date=payload.get("date", ""),
                    characters=list(payload.get("characters", []) or []),
                    place=payload.get("place", "") or "",
                ))
            else:
                result.append(self._parse_from_label(item.text()))
        return result
