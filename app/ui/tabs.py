from __future__ import annotations
from typing import List
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QPushButton, QLabel, QMessageBox, QColorDialog,
    QFileDialog, QListView, QListWidget, QListWidgetItem, QInputDialog, QDialog, QDialogButtonBox, QGridLayout
)
from ..models import Character, Event

def _shorten(text: str, max_len: int = 60) -> str:
    text = (text or "").replace("\n", " ")
    return text if len(text) <= max_len else text[: max_len - 1] + "…"

class CharactersTab(QWidget):
    """
    A full-featured characters tab: select a character and edit all fields.
    """
    def __init__(self, initial_chars: List[Character]):
        super().__init__()
        self.chars: List[Character] = [Character(**asdict(c)) if not isinstance(c, Character) else c for c in initial_chars]
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SingleSelection)
        for c in self.chars:
            self.list.addItem(QListWidgetItem(c.name))
        self.list.currentRowChanged.connect(self._on_select)

        add_btn = QPushButton("Add Character")
        del_btn = QPushButton("Delete selected")
        add_btn.clicked.connect(self._add_char)
        del_btn.clicked.connect(self._delete_selected)

        # Detail
        self.name_edit = QLineEdit()
        self.desc_edit = QTextEdit()
        self.color_btn = QPushButton()
        self.color_btn.clicked.connect(self._pick_color)
        self.texts_list = QListWidget()
        self.add_text_btn = QPushButton("Add Note")
        self.del_text_btn = QPushButton("Delete Note")
        self.add_text_btn.clicked.connect(self._add_text)
        self.del_text_btn.clicked.connect(self._del_text)
        self.images_list = QListWidget()
        self.add_img_btn = QPushButton("Add Image")
        self.del_img_btn = QPushButton("Delete Image")
        self.add_img_btn.clicked.connect(self._add_img)
        self.del_img_btn.clicked.connect(self._del_img)

        # Save btn
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self._save_current)

        form = QGridLayout()
        form.addWidget(QLabel("Name"), 0, 0)
        form.addWidget(self.name_edit, 0, 1)
        form.addWidget(QLabel("Description"), 1, 0)
        form.addWidget(self.desc_edit, 1, 1)
        form.addWidget(QLabel("Color"), 2, 0)
        form.addWidget(self.color_btn, 2, 1)
        form.addWidget(QLabel("Texts/Notes"), 3, 0)
        form.addWidget(self.texts_list, 3, 1)
        form.addWidget(self.add_text_btn, 4, 1)
        form.addWidget(self.del_text_btn, 5, 1)
        form.addWidget(QLabel("Images"), 6, 0)
        form.addWidget(self.images_list, 6, 1)
        form.addWidget(self.add_img_btn, 7, 1)
        form.addWidget(self.del_img_btn, 8, 1)
        form.addWidget(self.save_btn, 9, 0, 1, 2)

        left = QVBoxLayout()
        left.addWidget(self.list)
        left.addWidget(add_btn)
        left.addWidget(del_btn)

        main = QHBoxLayout(self)
        main.addLayout(left, 1)
        main.addLayout(form, 2)

        self.list.setCurrentRow(0)

    def _on_select(self, row):
        if row < 0 or row >= len(self.chars):
            self._clear_details()
            return
        c = self.chars[row]
        self.name_edit.setText(c.name)
        self.desc_edit.setPlainText(c.description)
        self.color_btn.setStyleSheet(f"background:{c.color}")
        self.color_btn.setText(c.color)
        self.texts_list.clear()
        for t in c.texts:
            self.texts_list.addItem(QListWidgetItem(t))
        self.images_list.clear()
        for img in c.images:
            item = QListWidgetItem(img)
            self.images_list.addItem(item)

    def _save_current(self):
        row = self.list.currentRow()
        if row < 0 or row >= len(self.chars):
            return
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing name", "Name cannot be empty.")
            return
        # Check for duplicate names
        for i, cc in enumerate(self.chars):
            if i != row and cc.name.lower() == name.lower():
                QMessageBox.warning(self, "Duplicate", "Another character has this name.")
                return
        c = self.chars[row]
        c.name = name
        c.description = self.desc_edit.toPlainText()
        c.color = self.color_btn.text()
        c.texts = [self.texts_list.item(i).text() for i in range(self.texts_list.count())]
        c.images = [self.images_list.item(i).text() for i in range(self.images_list.count())]
        self.list.item(row).setText(c.name)

    def _clear_details(self):
        self.name_edit.clear()
        self.desc_edit.clear()
        self.color_btn.setStyleSheet("")
        self.color_btn.setText("")
        self.texts_list.clear()
        self.images_list.clear()

    def _add_char(self):
        name, ok = QInputDialog.getText(self, "Add Character", "Character name?")
        if not ok or not name.strip():
            return
        if any(c.name.lower() == name.strip().lower() for c in self.chars):
            QMessageBox.warning(self, "Duplicate", "Character already exists.")
            return
        c = Character(name=name.strip())
        self.chars.append(c)
        self.list.addItem(QListWidgetItem(c.name))
        self.list.setCurrentRow(self.list.count() - 1)

    def _delete_selected(self):
        row = self.list.currentRow()
        if row < 0 or row >= len(self.chars):
            return
        self.chars.pop(row)
        self.list.takeItem(row)
        self.list.setCurrentRow(0 if self.chars else -1)

    def _pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background:{color.name()}")
            self.color_btn.setText(color.name())

    def _add_text(self):
        text, ok = QInputDialog.getMultiLineText(self, "Add Note", "Text:")
        if ok and text.strip():
            self.texts_list.addItem(QListWidgetItem(text.strip()))

    def _del_text(self):
        for item in self.texts_list.selectedItems():
            self.texts_list.takeItem(self.texts_list.row(item))

    def _add_img(self):
        folder = os.path.join(os.getcwd(), "pictures")
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        file, _ = QFileDialog.getOpenFileName(self, "Select Image", folder, "Images (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)")
        if file:
            rel = os.path.relpath(file, os.getcwd())
            if not rel.startswith("pictures/") and not rel.startswith("pictures\\"):
                QMessageBox.warning(self, "Not in pictures/", "Please only add images from the 'pictures/' folder.")
                return
            self.images_list.addItem(QListWidgetItem(rel))

    def _del_img(self):
        for item in self.images_list.selectedItems():
            self.images_list.takeItem(self.images_list.row(item))

    def values(self) -> List[Character]:
        # Save current edit if any
        self._save_current()
        return self.chars

# ListTab and EventsTab remain the same as before, unchanged.
from PySide6.QtCore import QDate
from ..models import Event

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
    def __init__(self, initial_events: List[Event]):
        super().__init__()

        self.list = QListWidget()
        for ev in initial_events:
            label = f"{getattr(ev, 'date', '')} | {ev.title} – {_shorten(ev.description)}".strip(" |")
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

        add_btn = QPushButton("Add Event")
        del_btn = QPushButton("Delete selected")

        add_btn.clicked.connect(self.add_event)
        del_btn.clicked.connect(self.delete_selected)

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