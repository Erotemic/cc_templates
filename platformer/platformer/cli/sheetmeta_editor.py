import json
import os
import sys
from typing import Optional, Dict, List

from PyQt5 import QtCore, QtGui, QtWidgets
import logging


# -----------------------------
# Data Structures & Utilities
# -----------------------------


def rect_to_dict(x: float, y: float, w: float, h: float) -> Dict:
    return {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}


def dict_to_rect(d: Dict) -> QtCore.QRectF:
    return QtCore.QRectF(d["x"], d["y"], d["w"], d["h"])


# -----------------------------
# Graphics Items with composition-based signals (no multiple inheritance)
# -----------------------------
class RectItemSignals(QtCore.QObject):
    geometry_changed = QtCore.pyqtSignal(int)  # box_id


class RectItem(QtWidgets.QGraphicsRectItem):
    """QGraphicsRectItem that keeps (x,y) in item.pos() and (w,h) in rect(0,0,w,h).
    Emits geometry_changed via a composed QObject (RectItemSignals)."""

    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        box_id: int,
        meta: Optional[Dict] = None,
    ):
        super().__init__(QtCore.QRectF(0, 0, w, h))
        self.setPos(x, y)
        self.box_id = box_id
        self.meta = meta or {
            "entity_name": "",
            "animation_name": "",
            "animation_frame_number": 0,
        }
        self.signals = RectItemSignals()

        self.setFlags(
            QtWidgets.QGraphicsItem.ItemIsSelectable
            | QtWidgets.QGraphicsItem.ItemIsMovable
            | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self._normal_pen = QtGui.QPen(QtGui.QColor(0, 170, 255), 2)
        self._hover_pen = QtGui.QPen(QtGui.QColor(255, 170, 0), 2, QtCore.Qt.DashLine)
        self._selected_pen = QtGui.QPen(QtGui.QColor(0, 255, 0), 2)
        self._brush = QtGui.QBrush(QtGui.QColor(0, 170, 255, 40))
        self.setPen(self._normal_pen)
        self.setBrush(self._brush)

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        self.setPen(self._hover_pen)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent):
        self.setPen(self._selected_pen if self.isSelected() else self._normal_pen)
        super().hoverLeaveEvent(event)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget=None,
    ):
        self.setPen(self._selected_pen if self.isSelected() else self._normal_pen)
        super().paint(painter, option, widget)

    def itemChange(self, change, value):
        if change in (
            QtWidgets.QGraphicsItem.ItemSelectedHasChanged,
            QtWidgets.QGraphicsItem.ItemPositionHasChanged,
            QtWidgets.QGraphicsItem.ItemTransformHasChanged,
        ):
            # Emit using the composed QObject
            self.signals.geometry_changed.emit(self.box_id)
        return super().itemChange(change, value)

    def scene_rect(self) -> QtCore.QRectF:
        p = self.pos()
        r = self.rect()
        return QtCore.QRectF(p.x(), p.y(), r.width(), r.height())


# -----------------------------
# Graphics View for Image & Drawing
# -----------------------------
class SpriteView(QtWidgets.QGraphicsView):
    image_changed = QtCore.pyqtSignal()
    box_created = QtCore.pyqtSignal(RectItem)
    selection_changed = QtCore.pyqtSignal()
    path_dropped = QtCore.pyqtSignal(str)  # emits any dropped file path (.png or .json)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.setAcceptDrops(True)
        # Important: the QGraphicsView uses an internal viewport widget that actually receives the DnD events
        self.viewport().setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item: Optional[QtWidgets.QGraphicsPixmapItem] = None
        self._drawing = False
        self._start_pos = QtCore.QPointF()
        self._rubber_item: Optional[QtWidgets.QGraphicsRectItem] = None

        # Zoom support
        self._zoom = 1.0
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        self._scene.selectionChanged.connect(self.selection_changed)

    # ------------- Drag & Drop -------------
    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                low = url.toLocalFile().lower()
                if low.endswith('.png') or low.endswith('.json'):
                    logging.info('[SpriteView] dragEnterEvent accept: %s', low)
                    event.acceptProposedAction()
                    return
        logging.info('[SpriteView] dragEnterEvent ignore')
        event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                low = url.toLocalFile().lower()
                if low.endswith('.png') or low.endswith('.json'):
                    # keep accepting while dragging over the view
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            logging.info('[SpriteView] dropEvent path: %s', local)
            try:
                self.path_dropped.emit(local)
                event.acceptProposedAction()
            except Exception as ex:
                logging.exception('[SpriteView] path_dropped emit failed: %s', ex)
            break

    # ------------- Image Handling -------------
    def load_image(self, path: str):
        logging.info('[SpriteView] load_image: %s', path)
        pix = QtGui.QPixmap(path)
        if pix.isNull():
            logging.error('[SpriteView] load_image failed: %s', path)
            QtWidgets.QMessageBox.warning(self, 'Load Error', 'Failed to load image: ' + path)
            return
        self._scene.clear()
        self._pixmap_item = self._scene.addPixmap(pix)
        self._pixmap_item.setZValue(-100)
        # Fix: use numbers to avoid type issues
        self._scene.setSceneRect(*pix.rect().getRect())
        self.resetTransform()
        self._zoom = 1.0
        self.image_changed.emit()
        logging.info('[SpriteView] image loaded: %dx%d', pix.width(), pix.height())

    def image_loaded(self) -> bool:
        return self._pixmap_item is not None

    # ------------- Mouse for Drawing -------------
    def start_draw_mode(self):
        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(), "Hold Shift, then drag on the image to draw a box."
        )

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if (
            self.image_loaded()
            and event.button() == QtCore.Qt.LeftButton
            and (event.modifiers() & QtCore.Qt.ShiftModifier)
        ):
            self._drawing = True
            self._start_pos = self.mapToScene(event.pos())
            self._rubber_item = self._scene.addRect(
                QtCore.QRectF(self._start_pos, self._start_pos),
                QtGui.QPen(QtGui.QColor(255, 0, 0), 1, QtCore.Qt.DashLine),
            )
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if self._drawing and self._rubber_item is not None:
            curr = self.mapToScene(event.pos())
            rect = QtCore.QRectF(self._start_pos, curr).normalized()
            self._rubber_item.setRect(rect)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        if self._drawing and event.button() == QtCore.Qt.LeftButton:
            self._drawing = False
            rect = self._rubber_item.rect() if self._rubber_item else QtCore.QRectF()
            if self._rubber_item:
                self._scene.removeItem(self._rubber_item)
                self._rubber_item = None

            if rect.width() >= 1 and rect.height() >= 1:
                img_rect = QtCore.QRectF(self._pixmap_item.pixmap().rect())
                rect = rect.intersected(img_rect)
                item = RectItem(
                    rect.x(), rect.y(), rect.width(), rect.height(), box_id=-1
                )
                self.box_created.emit(item)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    # ------------- Zoom -------------
    def wheelEvent(self, event: QtGui.QWheelEvent):
        if not self.image_loaded():
            return super().wheelEvent(event)
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 1 / 1.15
        self._zoom *= factor
        self.scale(factor, factor)

    # ------------- Add/Remove Boxes -------------
    def add_box_item(self, item: RectItem):
        self._scene.addItem(item)
        item.setZValue(10)

    def remove_selected(self) -> List[int]:
        removed_ids = []
        for it in list(self._scene.selectedItems()):
            if isinstance(it, RectItem):
                removed_ids.append(it.box_id)
                self._scene.removeItem(it)
        return removed_ids

    def all_rect_items(self) -> List[RectItem]:
        return [it for it in self._scene.items() if isinstance(it, RectItem)]


# -----------------------------
# Metadata Panel (Dock)
# -----------------------------
class MetadataPanel(QtWidgets.QWidget):
    fields_changed = QtCore.pyqtSignal(dict)  # emits full metadata + rect dict

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_box_id: Optional[int] = None

        # Metadata widgets
        self.entity_edit = QtWidgets.QLineEdit()
        self.anim_edit = QtWidgets.QLineEdit()
        self.frame_spin = QtWidgets.QSpinBox()
        self.frame_spin.setRange(0, 10000)

        # Rect widgets
        self.x_spin = QtWidgets.QSpinBox()
        self.x_spin.setRange(0, 1_000_000)
        self.y_spin = QtWidgets.QSpinBox()
        self.y_spin.setRange(0, 1_000_000)
        self.w_spin = QtWidgets.QSpinBox()
        self.w_spin.setRange(1, 1_000_000)
        self.h_spin = QtWidgets.QSpinBox()
        self.h_spin.setRange(1, 1_000_000)

        form = QtWidgets.QFormLayout()
        form.addRow("Entity Name", self.entity_edit)
        form.addRow("Animation Name", self.anim_edit)
        form.addRow("Animation Frame #", self.frame_spin)
        form.addRow(QtWidgets.QLabel(""))
        form.addRow("X", self.x_spin)
        form.addRow("Y", self.y_spin)
        form.addRow("Width", self.w_spin)
        form.addRow("Height", self.h_spin)

        wrap = QtWidgets.QWidget()
        wrap.setLayout(form)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(wrap)
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(scroll)

        for w in [self.entity_edit, self.anim_edit]:
            w.textEdited.connect(self._emit)
        for w in [self.frame_spin, self.x_spin, self.y_spin, self.w_spin, self.h_spin]:
            w.valueChanged.connect(self._emit)

    def set_box(
        self, box_id: Optional[int], rect: Optional[QtCore.QRectF], meta: Optional[Dict]
    ):
        self._current_box_id = box_id
        widgets = [
            self.entity_edit,
            self.anim_edit,
            self.frame_spin,
            self.x_spin,
            self.y_spin,
            self.w_spin,
            self.h_spin,
        ]
        for w in widgets:
            w.blockSignals(True)

        if rect and meta is not None and box_id is not None:
            self.entity_edit.setText(meta.get("entity_name", ""))
            self.anim_edit.setText(meta.get("animation_name", ""))
            self.frame_spin.setValue(int(meta.get("animation_frame_number", 0)))
            self.x_spin.setValue(int(rect.x()))
            self.y_spin.setValue(int(rect.y()))
            self.w_spin.setValue(int(rect.width()))
            self.h_spin.setValue(int(rect.height()))
        else:
            self.entity_edit.clear()
            self.anim_edit.clear()
            self.frame_spin.setValue(0)
            self.x_spin.setValue(0)
            self.y_spin.setValue(0)
            self.w_spin.setValue(1)
            self.h_spin.setValue(1)

        for w in widgets:
            w.blockSignals(False)

    def _emit(self):
        if self._current_box_id is None:
            return
        data = {
            "id": self._current_box_id,
            "entity_name": self.entity_edit.text().strip(),
            "animation_name": self.anim_edit.text().strip(),
            "animation_frame_number": int(self.frame_spin.value()),
            "rect": {
                "x": int(self.x_spin.value()),
                "y": int(self.y_spin.value()),
                "w": int(self.w_spin.value()),
                "h": int(self.h_spin.value()),
            },
        }
        self.fields_changed.emit(data)


# -----------------------------
# Main Window
# -----------------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sprite Sheet Metadata Editor")
        self.resize(1320, 840)
        self.setAcceptDrops(True)

        self.view = SpriteView()
        self.view.image_changed.connect(self.on_image_changed)
        self.view.box_created.connect(self.on_box_created)
        self.view.selection_changed.connect(self.sync_selection_from_scene)
        self.view.path_dropped.connect(self.on_path_dropped)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.currentRowChanged.connect(self.on_list_selection_changed)
        self.list_widget.itemDoubleClicked.connect(self.focus_selected_box)

        self.add_btn = QtWidgets.QPushButton("+ New Box")
        self.add_btn.setToolTip("Add a new 64x64 box at (0,0)")
        self.add_btn.clicked.connect(self.add_new_box)
        self.del_btn = QtWidgets.QPushButton("Delete Selected")
        self.del_btn.clicked.connect(self.delete_selected_box)
        self.save_btn = QtWidgets.QPushButton("Save")
        self.save_btn.setToolTip("Save metadata (Ctrl+S)")
        self.save_btn.clicked.connect(self.save_metadata)

        side = QtWidgets.QWidget()
        side_lay = QtWidgets.QVBoxLayout(side)
        side_lay.addWidget(QtWidgets.QLabel("Boxes"))
        side_lay.addWidget(self.list_widget, 1)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.del_btn)
        side_lay.addLayout(btn_row)
        side_lay.addWidget(self.save_btn)

        splitter = QtWidgets.QSplitter()
        splitter.addWidget(self.view)
        splitter.addWidget(side)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([1100, 400])
        self.setCentralWidget(splitter)

        self.meta_panel = MetadataPanel()
        self.meta_panel.fields_changed.connect(self.on_meta_fields_changed)
        self.meta_dock = QtWidgets.QDockWidget("Metadata", self)
        self.meta_dock.setWidget(self.meta_panel)
        self.meta_dock.setAllowedAreas(
            QtCore.Qt.RightDockWidgetArea | QtCore.Qt.LeftDockWidgetArea
        )
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.meta_dock)

        self.statusBar().showMessage("Drag & drop a PNG or JSON anywhere. Shift+Drag to draw a rectangle, or click '+ New Box'.")

        self.image_path: Optional[str] = None
        self.box_counter = 0
        self.box_index: Dict[int, RectItem] = {}

        self._build_menus()
        QtWidgets.QShortcut(
            QtGui.QKeySequence.Delete, self, activated=self.delete_selected_box
        )
        QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+O"), self, activated=self.open_image
        )
        QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+S"), self, activated=self.save_metadata
        )
        QtWidgets.QShortcut(
            QtGui.QKeySequence("Ctrl+L"), self, activated=self.load_metadata
        )
        QtWidgets.QShortcut(QtGui.QKeySequence("N"), self, activated=self.add_new_box)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".png"):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent):
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local.lower().endswith(".png"):
                self.view.load_image(local)
                self.image_path = local
                break

    def _build_menus(self):
        m = self.menuBar()
        file_menu = m.addMenu("File")
        a_open_img = file_menu.addAction("Open Image…")
        a_open_img.triggered.connect(self.open_image)
        a_load_json = file_menu.addAction("Load Metadata JSON…")
        a_load_json.triggered.connect(self.load_metadata)
        a_save_json = file_menu.addAction("Save Metadata JSON…")
        a_save_json.triggered.connect(self.save_metadata)
        file_menu.addSeparator()
        a_quit = file_menu.addAction("Quit")
        a_quit.triggered.connect(self.close)

        help_menu = m.addMenu("Help")
        a_about = help_menu.addAction("About")
        a_about.triggered.connect(self.show_about)

        toolbar = self.addToolBar("Main")
        act_new_box = QtWidgets.QAction("New Box", self)
        act_new_box.triggered.connect(self.add_new_box)
        toolbar.addAction(act_new_box)
        act_draw_hint = QtWidgets.QAction("Draw (Shift+Drag)", self)
        act_draw_hint.triggered.connect(self.view.start_draw_mode)
        toolbar.addAction(act_draw_hint)
        act_save = QtWidgets.QAction("Save", self)
        act_save.setShortcut(QtGui.QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_metadata)
        toolbar.addAction(act_save)

    def show_about(self):
        msg = (
            "Sprite Sheet Metadata Editor "
            "• Drag & drop a PNG onto the window or use File → Open Image.  "
            "• Hold Shift and drag with left mouse to draw a rectangle (or click '+ New Box').  "
            "• Select a box to edit its metadata and coordinates in the Metadata dock.  "
            "• Press Delete to remove selected.  "
            "• Load/Save JSON via File menu."
        )
        QtWidgets.QMessageBox.information(self, "About", msg)

    def on_image_changed(self):
        for it in self.view.all_rect_items():
            self.view.scene().removeItem(it)
        self.list_widget.clear()
        self.box_index.clear()
        self.box_counter = 0

    def open_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open PNG", "", "PNG Images (*.png)"
        )
        if path:
            self.open_image_path(path)

    def open_image_path(self, path: str):
        if not path:
            return
        logging.info('[MainWindow] open_image_path: %s', path)
        self.view.load_image(path)
        self.image_path = path

    def add_new_box(self):
        if not self.view.image_loaded():
            QtWidgets.QMessageBox.information(
                self, "No Image", "Load or drop a PNG first."
            )
            return
        item = RectItem(0, 0, 64, 64, box_id=self.box_counter)
        self.box_counter += 1
        self.view.add_box_item(item)
        self.box_index[item.box_id] = item
        self._add_list_item(item)
        self.select_box_in_list(item.box_id)
        self.meta_panel.set_box(item.box_id, item.scene_rect(), item.meta)
        item.signals.geometry_changed.connect(self._on_rect_geom_changed)

    def _on_rect_geom_changed(self, box_id: int):
        ri = self.box_index.get(box_id)
        if not ri:
            return
        self.meta_panel.set_box(ri.box_id, ri.scene_rect(), ri.meta)
        self._refresh_list_item(ri.box_id)

    def on_box_created(self, item: RectItem):
        item.box_id = self.box_counter
        self.box_counter += 1
        self.view.add_box_item(item)
        self.box_index[item.box_id] = item
        self._add_list_item(item)
        self.select_box_in_list(item.box_id)
        self.meta_panel.set_box(item.box_id, item.scene_rect(), item.meta)
        item.signals.geometry_changed.connect(self._on_rect_geom_changed)

    def _add_list_item(self, rect_item: RectItem):
        lw_item = QtWidgets.QListWidgetItem(self._list_label(rect_item))
        lw_item.setData(QtCore.Qt.UserRole, rect_item.box_id)
        self.list_widget.addItem(lw_item)

    def _refresh_list_item(self, box_id: int):
        for i in range(self.list_widget.count()):
            it = self.list_widget.item(i)
            if it.data(QtCore.Qt.UserRole) == box_id:
                it.setText(self._list_label(self.box_index[box_id]))
                break

    def _list_label(self, rect_item: RectItem) -> str:
        r = rect_item.scene_rect().toRect()
        meta = rect_item.meta
        return (
            f"#{rect_item.box_id}: {meta.get('entity_name', '')} / {meta.get('animation_name', '')} "
            f"[frame {meta.get('animation_frame_number', 0)}] -> ({r.x()},{r.y()},{r.width()}x{r.height()})"
        )

    def select_box_in_list(self, box_id: int):
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(QtCore.Qt.UserRole) == box_id:
                self.list_widget.setCurrentRow(i)
                break

    def get_selected_rect_item(self) -> Optional[RectItem]:
        idx = self.list_widget.currentRow()
        if idx < 0:
            return None
        item = self.list_widget.item(idx)
        box_id = item.data(QtCore.Qt.UserRole)
        return self.box_index.get(box_id)

    def sync_selection_from_scene(self):
        selected_ids = [
            it.box_id
            for it in self.view._scene.selectedItems()
            if isinstance(it, RectItem)
        ]
        if not selected_ids:
            self.list_widget.clearSelection()
            self.meta_panel.set_box(None, None, None)
            return
        target = selected_ids[0]
        self.select_box_in_list(target)
        self.meta_panel.set_box(
            target, self.box_index[target].scene_rect(), self.box_index[target].meta
        )

    def on_list_selection_changed(self, idx: int):
        if idx < 0:
            self.meta_panel.set_box(None, None, None)
            return
        item = self.list_widget.item(idx)
        box_id = item.data(QtCore.Qt.UserRole)
        for rect_item in self.view.all_rect_items():
            rect_item.setSelected(rect_item.box_id == box_id)
        if box_id in self.box_index:
            ri = self.box_index[box_id]
            self.view.centerOn(ri)
            self.meta_panel.set_box(ri.box_id, ri.scene_rect(), ri.meta)

    def focus_selected_box(self):
        ri = self.get_selected_rect_item()
        if ri:
            self.view.centerOn(ri)
            self.meta_panel.set_box(ri.box_id, ri.scene_rect(), ri.meta)
            self.meta_dock.raise_()

    def on_meta_fields_changed(self, data: Dict):
        box_id = data.get("id")
        if box_id not in self.box_index:
            return
        ri = self.box_index[box_id]
        ri.meta.update(
            {
                "entity_name": data["entity_name"],
                "animation_name": data["animation_name"],
                "animation_frame_number": int(data["animation_frame_number"]),
            }
        )
        ri.setRect(0, 0, data["rect"]["w"], data["rect"]["h"])
        ri.setPos(data["rect"]["x"], data["rect"]["y"])
        self._refresh_list_item(box_id)

    def delete_selected_box(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        item = self.list_widget.item(idx)
        box_id = item.data(QtCore.Qt.UserRole)
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Box",
            f"Delete box #{box_id}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return
        rect_item = self.box_index.pop(box_id, None)
        if rect_item:
            self.view._scene.removeItem(rect_item)
        self.list_widget.takeItem(idx)
        self.meta_panel.set_box(None, None, None)

    def save_metadata(self):
        if not self.view.image_loaded():
            QtWidgets.QMessageBox.information(
                self, "Nothing to Save", "Load an image and create boxes first."
            )
            return
        default_name = "metadata.json"
        if self.image_path:
            base = os.path.splitext(os.path.basename(self.image_path))[0]
            default_name = f"{base}_metadata.json"
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Metadata JSON", default_name, "JSON (*.json)"
        )
        if not path:
            return

        pix = self.view._pixmap_item.pixmap()
        data = {
            "image_path": self.image_path or "",
            "image_size": {"w": pix.width(), "h": pix.height()},
            "boxes": [],
        }
        for it in sorted(self.view.all_rect_items(), key=lambda it: it.box_id):
            r = it.scene_rect()
            data["boxes"].append(
                {
                    "id": it.box_id,
                    "rect": rect_to_dict(r.x(), r.y(), r.width(), r.height()),
                    **it.meta,
                }
            )
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as ex:
            QtWidgets.QMessageBox.warning(
                self, "Save Error", "Failed to save JSON: " + str(ex)
            )
            return
        self.statusBar().showMessage("Saved metadata -> " + path, 5000)

    def load_metadata(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load Metadata JSON", "", "JSON (*.json)"
        )
        if not path:
            return
        self.load_metadata_path(path)

    def load_metadata_path(self, path: str):
        if not path:
            return
        logging.info('[MainWindow] load_metadata_path: %s', path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as ex:
            logging.exception('[MainWindow] load_metadata_path failed')
            QtWidgets.QMessageBox.warning(self, 'Load Error', 'Failed to read JSON: ' + str(ex))
            return

        img_path = data.get('image_path') or ''
        if img_path and os.path.exists(img_path):
            self.view.load_image(img_path)
            self.image_path = img_path
        elif not self.view.image_loaded():
            QtWidgets.QMessageBox.information(
                self,
                'Image Required',
                'The metadata file does not reference a valid image path. Please open the PNG first, then load the metadata again.',
            )
            return

        for it in self.view.all_rect_items():
            self.view._scene.removeItem(it)
        self.list_widget.clear()
        self.box_index.clear()
        self.box_counter = 0

        for b in data.get('boxes', []):
            r = b.get('rect', {'x': 0, 'y': 0, 'w': 1, 'h': 1})
            meta = {
                'entity_name': b.get('entity_name', ''),
                'animation_name': b.get('animation_name', ''),
                'animation_frame_number': int(b.get('animation_frame_number', 0)),
            }
            box_id = int(b.get('id', self.box_counter))
            self.box_counter = max(self.box_counter, box_id + 1)
            item = RectItem(r['x'], r['y'], r['w'], r['h'], box_id=box_id, meta=meta)
            self.view.add_box_item(item)
            self.box_index[item.box_id] = item
            self._add_list_item(item)
            item.signals.geometry_changed.connect(self._on_rect_geom_changed)

        self.statusBar().showMessage('Loaded metadata from ' + path, 5000)
        logging.info('[MainWindow] loaded %d boxes', len(self.box_index))
        return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as ex:
            QtWidgets.QMessageBox.warning(
                self, "Load Error", "Failed to read JSON: " + str(ex)
            )
            return

        img_path = data.get("image_path") or ""
        if img_path and os.path.exists(img_path):
            self.view.load_image(img_path)
            self.image_path = img_path
        elif not self.view.image_loaded():
            QtWidgets.QMessageBox.information(
                self,
                "Image Required",
                "The metadata file does not reference a valid image path. Please open the PNG first, then load the metadata again.",
            )
            return

        for it in self.view.all_rect_items():
            self.view._scene.removeItem(it)
        self.list_widget.clear()
        self.box_index.clear()
        self.box_counter = 0

        for b in data.get("boxes", []):
            r = b.get("rect", {"x": 0, "y": 0, "w": 1, "h": 1})
            meta = {
                "entity_name": b.get("entity_name", ""),
                "animation_name": b.get("animation_name", ""),
                "animation_frame_number": int(b.get("animation_frame_number", 0)),
            }
            box_id = int(b.get("id", self.box_counter))
            self.box_counter = max(self.box_counter, box_id + 1)
            item = RectItem(r["x"], r["y"], r["w"], r["h"], box_id=box_id, meta=meta)
            self.view.add_box_item(item)
            self.box_index[item.box_id] = item
            self._add_list_item(item)
            item.signals.geometry_changed.connect(self._on_rect_geom_changed)

        self.statusBar().showMessage("Loaded metadata from " + path, 5000)

    def on_path_dropped(self, path: str):
        logging.info('[MainWindow] on_path_dropped: %s', path)
        low = path.lower()
        if low.endswith('.json'):
            self.load_metadata_path(path)
        elif low.endswith('.png'):
            self.open_image_path(path)
        else:
            QtWidgets.QMessageBox.information(self, "Unsupported File", "Drop a .png or .json file.")


def main():
    # Basic logging setup; use LOGLEVEL env to override, e.g., LOGLEVEL=DEBUG
    level_name = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, level_name, logging.INFO),
        format='[%(levelname)s] %(message)s'
    )
    logging.info('Starting Sprite Sheet Metadata Editor')

    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SpriteTools')
    app.setApplicationName('Sprite Sheet Metadata Editor')
    w = MainWindow()

    # --- CLI support ---
    args = [a for a in sys.argv[1:] if os.path.exists(a)]
    logging.info('CLI args (existing paths): %s', args)
    if len(args) == 1:
        p0 = args[0].lower()
        if p0.endswith('.json'):
            w.load_metadata_path(args[0])
        elif p0.endswith('.png'):
            w.open_image_path(args[0])
    elif len(args) >= 2:
        img = next((a for a in args if a.lower().endswith('.png')), None)
        jsn = next((a for a in args if a.lower().endswith('.json')), None)
        if img:
            w.open_image_path(img)
        if jsn:
            w.load_metadata_path(jsn)

    w.resize(1500, 950)
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

