from __future__ import annotations
from typing import Callable, List, Optional, Tuple
from datetime import datetime, date
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QTransform
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsTextItem, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from ..models import Event


def _parse_date(d: str) -> Optional[date]:
    d = (d or "").strip()
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def _min_max_dates(events: List[Event]) -> Tuple[Optional[date], Optional[date]]:
    ds = [dt for dt in (_parse_date(e.date) for e in events) if dt is not None]
    if not ds:
        return None, None
    return min(ds), max(ds)


def _days_between(a: date, b: date) -> int:
    return (b - a).days


def _color_for_key(key: str) -> QColor:
    h = (abs(hash(key)) % 360)
    return QColor.fromHsv(h, 180, 200)


class _ZoomableView(QGraphicsView):
    """QGraphicsView med mushjuls-zoom och pan (drag)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRenderHints(self.renderHints())
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        factor = 1.2 if zoom_in else 1 / 1.2
        old_pos = self.mapToScene(event.position().toPoint())
        self.scale(factor, 1.0)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())


class TimelineGraphTab(QWidget):
    """
    Grafisk tidslinje:
    - Horisontell axel över min..max datum
    - Punkter för events (placeras efter datum)
    - Färgkodning (Place eller Character)
    - Filter: Character / Place (som i tabellen)
    - Zoom med mushjul, pan med drag
    """
    def __init__(self,
                 get_events_fn: Callable[[], List[Event]],
                 get_characters_fn: Callable[[], List[str]],
                 get_places_fn: Callable[[], List[str]]):
        super().__init__()
        self.get_events_fn = get_events_fn
        self.get_characters_fn = get_characters_fn
        self.get_places_fn = get_places_fn

        self.char_filter = QComboBox()
        self.place_filter = QComboBox()
        self.color_mode = QComboBox()
        self.color_mode.addItems(["Color by Place", "Color by Character"])

        self._refresh_filters()

        self.char_filter.currentIndexChanged.connect(self.render_scene)
        self.place_filter.currentIndexChanged.connect(self.render_scene)
        self.color_mode.currentIndexChanged.connect(self.render_scene)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.render_scene)

        top = QHBoxLayout()
        top.addWidget(QLabel("Filter Character:"))
        top.addWidget(self.char_filter)
        top.addSpacing(12)
        top.addWidget(QLabel("Filter Place:"))
        top.addWidget(self.place_filter)
        top.addSpacing(12)
        top.addWidget(QLabel("Color mode:"))
        top.addWidget(self.color_mode)
        top.addStretch(1)
        top.addWidget(self.refresh_btn)

        self.scene = QGraphicsScene(self)
        self.view = _ZoomableView(self.scene, self)
        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setRenderHints(self.view.renderHints())

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.view)

        self.render_scene()


    def _refresh_filters(self):
        cur_c = self.char_filter.currentText() if self.char_filter.count() else ""
        cur_p = self.place_filter.currentText() if self.place_filter.count() else ""

        self.char_filter.clear()
        self.char_filter.addItem("(All)")
        for c in self.get_characters_fn():
            self.char_filter.addItem(c)
        if cur_c:
            idx = self.char_filter.findText(cur_c)
            if idx >= 0:
                self.char_filter.setCurrentIndex(idx)

        self.place_filter.clear()
        self.place_filter.addItem("(All)")
        for p in self.get_places_fn():
            self.place_filter.addItem(p)
        if cur_p:
            idx = self.place_filter.findText(cur_p)
            if idx >= 0:
                self.place_filter.setCurrentIndex(idx)


    def render_scene(self):
        self._refresh_filters()
        self.scene.clear()

        events = self.get_events_fn()
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

        events = [e for e in events if visible(e)]
        mind, maxd = _min_max_dates(events)

        if not events:
            hint = QGraphicsTextItem("No events match the current filters.")
            self.scene.addItem(hint)
            return
        if not mind or not maxd:
            hint = QGraphicsTextItem("Some events lack dates. Add dates to see them on the timeline.")
            self.scene.addItem(hint)
            return

        left_pad = 60.0
        right_pad = 40.0
        top_pad = 40.0
        height = 240.0
        width = 1000.0

        total_days = max(1, _days_between(mind, maxd))
        def x_for(d: date) -> float:
            return left_pad + (width - left_pad - right_pad) * (_days_between(mind, d) / total_days)

        axis_y = top_pad + height / 2
        axis_pen = QPen(QColor(120, 120, 120))
        self.scene.addLine(left_pad, axis_y, width - right_pad, axis_y, axis_pen)

        tick_pen = QPen(QColor(150, 150, 150))
        label_brush = QBrush(QColor(60, 60, 60))
        cur = date(mind.year, mind.month, 1)
        def add_month(dt: date) -> date:
            y, m = dt.year, dt.month
            if m == 12:
                return date(y + 1, 1, 1)
            return date(y, m + 1, 1)

        while cur <= maxd:
            x = x_for(cur)
            self.scene.addLine(x, axis_y - 6, x, axis_y + 6, tick_pen)
            txt = QGraphicsTextItem(cur.strftime("%Y-%m"))
            txt.setDefaultTextColor(QColor(80, 80, 80))
            txt.setPos(x - 20, axis_y + 8)
            self.scene.addItem(txt)
            cur = add_month(cur)

        color_by_place = (self.color_mode.currentText() == "Color by Place")

        for ev in events:
            d = _parse_date(ev.date)
            if not d:
                continue
            x = x_for(d)
            y = axis_y

            key = ev.place if color_by_place else (ev.characters[0] if ev.characters else "")
            col = _color_for_key(key) if key else QColor(30, 144, 255)
            pen = QPen(col.darker(150))
            brush = QBrush(col)

            r = 6.0
            dot = QGraphicsEllipseItem(x - r, y - r, 2 * r, 2 * r)
            dot.setBrush(brush)
            dot.setPen(pen)
            dot.setToolTip(self._tooltip_for_event(ev))
            self.scene.addItem(dot)

            label = QGraphicsTextItem(ev.title)
            label.setDefaultTextColor(QColor(30, 30, 30))
            label.setPos(x + 8, y - 24)
            label.setToolTip(self._tooltip_for_event(ev))
            self.scene.addItem(label)

        rect = QRectF(0, 0, width, top_pad + height + 80)
        self.scene.setSceneRect(rect)
        self.view.setTransform(QTransform())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    @staticmethod
    def _tooltip_for_event(ev: Event) -> str:
        chars = ", ".join(ev.characters or [])
        parts = [
            f"Title: {ev.title}",
            f"Date: {ev.date or '(none)'}",
            f"Place: {ev.place or '(none)'}",
            f"Characters: {chars or '(none)'}",
            f"Description: {ev.description or ''}",
        ]
        return "\n".join(parts)
