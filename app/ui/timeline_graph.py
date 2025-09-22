from __future__ import annotations
from typing import Callable, List, Optional, Tuple
from datetime import datetime, date as Date
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QTransform
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsTextItem, QHBoxLayout,
    QLabel, QComboBox, QPushButton
)
from ..models import Event


def _parse_date(d: str) -> Optional[Date]:
    d = (d or "").strip()
    if not d:
        return None
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return None


def _min_max_dates(events: List[Event]) -> Tuple[Optional[Date], Optional[Date]]:
    ds = [dt for dt in (_parse_date(e.date) for e in events) if dt is not None]
    if not ds:
        return None, None
    return min(ds), max(ds)


def _days_between(a: Date, b: Date) -> int:
    return max(0, (b - a).days)


def _color_for_key(key: str) -> QColor:
    h = (abs(hash(key)) % 360)
    return QColor.fromHsv(h, 180, 200)


class _ZoomableView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        dy = 0
        try:
            dy = event.angleDelta().y()
        except Exception:
            pass
        if dy == 0:
            return super().wheelEvent(event)
        factor = 1.2 if dy > 0 else (1 / 1.2)
        old_pos = self.mapToScene(event.position().toPoint())
        self.scale(factor, 1.0)
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())


class TimelineGraphTab(QWidget):
    def __init__(self,
                 get_events_fn: Callable[[], List[Event]],
                 get_characters_fn: Callable[[], List[str]],
                 get_places_fn: Callable[[], List[str]]):
        super().__init__()
        self.get_events_fn = get_events_fn
        self.get_characters_fn = get_characters_fn
        self.get_places_fn = get_places_fn

        self._rendering = False

        self.char_filter = QComboBox()
        self.place_filter = QComboBox()
        self.color_mode = QComboBox()
        self.color_mode.addItems(["Color by Place", "Color by Character"])

        self._refresh_filters(connect_signals=False)
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

        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.view)

        self.render_scene()


    def _refresh_filters(self, connect_signals: bool = True):
        cur_c = self.char_filter.currentText() if self.char_filter.count() else ""
        cur_p = self.place_filter.currentText() if self.place_filter.count() else ""

        self.char_filter.blockSignals(True)
        self.place_filter.blockSignals(True)

        self.char_filter.clear()
        self.char_filter.addItem("(All)")
        for c in self.get_characters_fn():
            self.char_filter.addItem(c)
        if cur_c:
            idx = self.char_filter.findText(cur_c)
            if idx >= 0:
                self.char_filter.setCurrentIndex(idx)
            else:
                self.char_filter.setCurrentIndex(0)

        self.place_filter.clear()
        self.place_filter.addItem("(All)")
        for p in self.get_places_fn():
            self.place_filter.addItem(p)
        if cur_p:
            idx = self.place_filter.findText(cur_p)
            if idx >= 0:
                self.place_filter.setCurrentIndex(idx)
            else:
                self.place_filter.setCurrentIndex(0)

        self.char_filter.blockSignals(False)
        self.place_filter.blockSignals(False)

        if connect_signals:
            pass


    def render_scene(self):
        if self._rendering:
            return
        self._rendering = True
        try:
            self._refresh_filters(connect_signals=False)
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
                self._fit_scene_safe()
                return

            if not mind or not maxd:
                hint = QGraphicsTextItem("Some events lack dates. Add dates to see them on the timeline.")
                self.scene.addItem(hint)
                self._fit_scene_safe()
                return

            left_pad, right_pad, top_pad = 60.0, 40.0, 40.0
            height, width = 260.0, 1000.0
            axis_y = top_pad + height / 2

            total_days = max(1, _days_between(mind, maxd))

            def x_for(d: Date) -> float:
                frac = (_days_between(mind, d) / total_days) if total_days else 0.0
                return left_pad + (width - left_pad - right_pad) * frac

            self.scene.addLine(left_pad, axis_y, width - right_pad, axis_y, QPen(QColor(120, 120, 120)))

            tick_pen = QPen(QColor(150, 150, 150))
            cur = Date(mind.year, mind.month, 1)

            def add_month(dt: Date) -> Date:
                y, m = dt.year, dt.month
                return Date(y + 1, 1, 1) if m == 12 else Date(y, m + 1, 1)

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
                x, y = x_for(d), axis_y

                key = (ev.place or "") if color_by_place else ((ev.characters[0] if ev.characters else "") or "")
                col = _color_for_key(key) if key else QColor(30, 144, 255)

                dot = QGraphicsEllipseItem(x - 6, y - 6, 12, 12)
                dot.setBrush(QBrush(col))
                dot.setPen(QPen(col.darker(150)))
                dot.setToolTip(self._tooltip_for_event(ev))
                self.scene.addItem(dot)

                label = QGraphicsTextItem(ev.title)
                label.setDefaultTextColor(QColor(30, 30, 30))
                label.setPos(x + 8, y - 24)
                label.setToolTip(self._tooltip_for_event(ev))
                self.scene.addItem(label)

            rect = QRectF(0, 0, max(1.0, width), max(1.0, top_pad + height + 80))
            self.scene.setSceneRect(rect)
            self._fit_scene_safe()
        finally:
            self._rendering = False

    def _fit_scene_safe(self):
        rect = self.scene.sceneRect()
        if rect.width() <= 0 or rect.height() <= 0:
            rect = QRectF(0, 0, 100, 100)
            self.scene.setSceneRect(rect)
        self.view.setTransform(QTransform())
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    @staticmethod
    def _tooltip_for_event(ev: Event) -> str:
        chars = ", ".join(ev.characters or [])
        return "\n".join([
            f"Title: {ev.title}",
            f"Date: {ev.date or '(none)'}",
            f"Place: {ev.place or '(none)'}",
            f"Characters: {chars or '(none)'}",
            f"Description: {ev.description or ''}",
        ])
