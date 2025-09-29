from __future__ import annotations
from typing import List, Dict, Tuple
from PySide6.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter
from PySide6.QtCore import Qt, QRectF
from ..models import Event, Character

def _date_key(s: str) -> str:
    return s if s else "9999-99-99"

class TimelineGraphWidget(QGraphicsView):
    """
    Shows a graphical timeline with one swimlane per character, colored by character color.
    Events are shown as rectangles at their date, per involved character.
    """
    ROW_HEIGHT = 50  # px per character lane
    LEFT_MARGIN = 120  # px space for character names
    TOP_MARGIN = 50
    LANE_PADDING = 10  # px vertical padding per lane
    EVENT_WIDTH = 20   # px width for event marker on timeline
    EVENT_HEIGHT = 24  # px height for event marker

    def __init__(self, get_events_fn, get_characters_fn, parent=None):
        super().__init__(parent)
        self.get_events_fn = get_events_fn
        self.get_characters_fn = get_characters_fn
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(350)
        self.setMinimumWidth(800)
        self._font = QFont()
        self._font.setPointSize(10)

    def refresh(self):
        # Gather data
        events: List[Event] = self.get_events_fn()
        characters: List[Character] = self.get_characters_fn()
        char_by_name: Dict[str, Character] = {c.name: c for c in characters}

        # Get all event dates for sorting X axis
        event_dates = []
        for ev in events:
            if getattr(ev, "start_date", ""):
                event_dates.append(ev.start_date)
        event_dates = sorted(set(event_dates))
        if not event_dates:
            self.scene().clear()
            return

        # Map: date -> x position
        n_dates = len(event_dates)
        timeline_width = max(600, n_dates * 90)
        date_x: Dict[str, float] = {
            date: self.LEFT_MARGIN + i * (timeline_width // max(1, n_dates-1))
            for i, date in enumerate(event_dates)
        }

        # Paint
        self.scene().clear()
        # Draw date labels
        for date, x in date_x.items():
            self.scene().addLine(x, self.TOP_MARGIN-12, x, self.TOP_MARGIN-6, QPen(Qt.gray, 1))
            txt = self.scene().addText(date, self._font)
            txt.setPos(x-22, self.TOP_MARGIN-30)

        # Draw character lanes
        for row, c in enumerate(characters):
            y = self.TOP_MARGIN + row * self.ROW_HEIGHT
            # Lane line
            col = QColor(c.color)
            pen = QPen(col, 3)
            self.scene().addLine(self.LEFT_MARGIN, y, timeline_width+self.LEFT_MARGIN-30, y, pen)
            # Character label
            label = self.scene().addText(c.name, self._font)
            label.setDefaultTextColor(col)
            label.setPos(10, y - self.EVENT_HEIGHT // 2)
        # Draw events
        for ev in events:
            if not getattr(ev, "start_date", ""):
                continue
            x = date_x.get(ev.start_date)
            if x is None:
                continue
            for cn in getattr(ev, "characters", []):
                crow = [i for i, c in enumerate(characters) if c.name == cn]
                if not crow:
                    continue
                row = crow[0]
                y = self.TOP_MARGIN + row * self.ROW_HEIGHT
                col = QColor(char_by_name[cn].color if cn in char_by_name else "#999")
                rect = QRectF(x - self.EVENT_WIDTH/2, y - self.EVENT_HEIGHT/2, self.EVENT_WIDTH, self.EVENT_HEIGHT)
                self.scene().addRect(rect, QPen(Qt.black, 1), QBrush(col.lighter(120)))
                # Event title (only for first character per event, to avoid repetition)
                if cn == ev.characters[0]:
                    txt = self.scene().addText(ev.title, self._font)
                    txt.setDefaultTextColor(Qt.black)
                    txt.setPos(x + 4, y - self.EVENT_HEIGHT)
        # Adjust scene size
        self.setSceneRect(0, 0, timeline_width+self.LEFT_MARGIN, self.TOP_MARGIN + len(characters)*self.ROW_HEIGHT + 40)

class TimelineTab(QWidget):
    """
    Tab containing the graphical timeline and a refresh button.
    """
    def __init__(self, get_events_fn, get_characters_fn):
        super().__init__()
        self.graph = TimelineGraphWidget(get_events_fn, get_characters_fn)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.graph.refresh)

        top = QHBoxLayout()
        top.addStretch(1)
        top.addWidget(self.refresh_btn)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.graph)
        # Initial draw
        self.graph.refresh()
    def refresh(self):
        self.graph.refresh()