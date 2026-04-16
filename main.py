import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QSystemTrayIcon, QMenu,
                             QSlider, QComboBox, QCheckBox, QFrame, QGraphicsDropShadowEffect,
                             QToolTip)
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, Property, QPoint, QRectF, QSize
from PySide6.QtGui import QIcon, QAction, QColor, QPainter, QPixmap, QPen, QBrush, QMovie, QPainterPath, QFont, QConicalGradient
import pyautogui

from settings_manager import SettingsManager

# --- CONTENEDOR CIRCULAR CON EFECTO DE PARPADEO ---
class CircularWidget(QWidget):
    def __init__(self, parent=None, manager=None):
        super().__init__(parent)
        self.manager = manager
        self.progress = 0.0
        self.is_flashing = False
        self.flash_state = True
        self.setFixedSize(220, 220)
        
        self.movie = QMovie("cat.gif")
        self.movie.frameChanged.connect(self.update)
        self.movie.start()

        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.flash_count = 0

    def set_progress(self, value):
        self.progress = value
        self.update()

    def start_flash(self):
        self.is_flashing = True
        self.flash_count = 0
        self.flash_timer.start(150)

    def toggle_flash(self):
        self.flash_state = not self.flash_state
        self.flash_count += 1
        self.update()
        if self.flash_count >= 6:
            self.flash_timer.stop()
            self.is_flashing = False
            self.progress = 0.0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        thickness = 12
        rect = QRectF(thickness/2, thickness/2, self.width() - thickness, self.height() - thickness)
        
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)

        if self.movie.isValid():
            path = QPainterPath()
            path.addEllipse(thickness, thickness, self.width() - thickness*2, self.height() - thickness*2)
            painter.save()
            painter.setClipPath(path)
            current_frame = self.movie.currentPixmap()
            scaled_frame = current_frame.scaled(200, 200, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(10, 10, scaled_frame)
            painter.restore()
        
        painter.setPen(QPen(QColor("#f8f9fa"), thickness))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(rect)

        if self.progress > 0 or self.is_flashing:
            color_setting = self.manager.get("loader_color")
            alpha = 255 if not (self.is_flashing and not self.flash_state) else 0

            if color_setting == "rainbow":
                gradient = QConicalGradient(rect.center(), 90)
                gradient.setColorAt(0.0, QColor(255, 0, 0, alpha))
                gradient.setColorAt(0.14, QColor(255, 127, 0, alpha))
                gradient.setColorAt(0.28, QColor(255, 255, 0, alpha))
                gradient.setColorAt(0.42, QColor(0, 255, 0, alpha))
                gradient.setColorAt(0.57, QColor(0, 0, 255, alpha))
                gradient.setColorAt(0.71, QColor(75, 0, 130, alpha))
                gradient.setColorAt(0.85, QColor(148, 0, 211, alpha))
                gradient.setColorAt(1.0, QColor(255, 0, 0, alpha))
                pen = QPen(QBrush(gradient), thickness, Qt.SolidLine, Qt.RoundCap)
            else:
                c = QColor(color_setting)
                c.setAlpha(alpha)
                pen = QPen(c, thickness, Qt.SolidLine, Qt.RoundCap)
            
            painter.setPen(pen)
            start_angle = 90 * 16
            span_angle = -int((1.0 if self.is_flashing else self.progress) * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

# --- PANEL DE AJUSTES (OVERLAY) ---
class SettingsPanel(QFrame):
    def __init__(self, parent=None, manager=None, circle_widget=None, close_callback=None):
        super().__init__(parent)
        self.manager = manager
        self.circle_widget = circle_widget
        self.setObjectName("SettingsPanel")
        self.setFixedSize(240, 320)
        
        self.setStyleSheet("""
            #SettingsPanel {
                background-color: white;
                border-radius: 25px;
                border: 3px solid #ff7eb9;
            }
            QLabel { 
                color: #2d3436; 
                font-family: 'Segoe UI Semibold'; 
                font-size: 13px; 
                background: transparent;
            }
            QLabel#Title { 
                color: #ff7eb9; 
                font-size: 18px; 
                font-weight: bold; 
            }
            QComboBox { 
                background: #f1f2f6; 
                border: 2px solid #dfe4ea; 
                border-radius: 10px; 
                padding: 5px; 
                color: #2d3436; 
                font-size: 12px;
            }
            QComboBox QAbstractItemView { 
                background: white; 
                color: #2d3436;
                selection-background-color: #ff7eb9; 
            }
            QSlider::groove:horizontal { height: 10px; background: #dfe4ea; border-radius: 5px; }
            QSlider::handle:horizontal { 
                background: #ff7eb9; 
                width: 20px; height: 20px; 
                margin: -5px 0; border-radius: 10px; 
            }
            QCheckBox { 
                color: #2d3436; 
                font-size: 13px; 
                font-weight: bold; 
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 6px;
                border: 2px solid #dfe4ea;
                background-color: #f1f2f6;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #ff7eb9;
            }
            QCheckBox::indicator:checked {
                background-color: #22c55e;
                border: 2px solid #22c55e;
                image: url(check_mark.png); /* Fallback si no hay imagen: se verá el color verde */
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)
        
        # Header con Botón de Cerrar
        header = QHBoxLayout()
        title = QLabel("Ajustes ⚙️")
        title.setObjectName("Title")
        header.addWidget(title)
        
        self.btn_close_settings = QPushButton("✕")
        self.btn_close_settings.setFixedSize(24, 24)
        self.btn_close_settings.setStyleSheet("""
            QPushButton { 
                background: #ff7e7e; color: white; border-radius: 12px; font-weight: bold; font-size: 10px; border: none;
            }
            QPushButton:hover { background: #ef4444; }
        """)
        self.btn_close_settings.clicked.connect(close_callback)
        header.addWidget(self.btn_close_settings)
        layout.addLayout(header)

        # Color
        layout.addWidget(QLabel("Color Favorito"))
        self.color_combo = QComboBox()
        self.colors = {"Arcoiris 🌈": "rainbow", "Rosa Pastel 🌸": "#ff7eb9", "Azul Mágico 💎": "#7eb6ff", "Verde Lima 🍏": "#72ec8a", "Naranja Dulce 🍊": "#ffb37e", "Morado Sueño 🔮": "#c37eff"}
        self.color_combo.addItems(list(self.colors.keys()))
        curr = self.manager.get("loader_color")
        for i, (k, v) in enumerate(self.colors.items()):
            if v == curr: self.color_combo.setCurrentIndex(i)
        self.color_combo.currentIndexChanged.connect(self.update_color)
        layout.addWidget(self.color_combo)

        # Acción
        layout.addWidget(QLabel("Actividad"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["🐾 Mover Patita", "🖱️ Hacer Clic", "⌨️ Tecla F15"])
        mode_map = {"move": 0, "click": 1, "key": 2}
        self.action_combo.setCurrentIndex(mode_map.get(self.manager.get("action_type"), 0))
        self.action_combo.currentIndexChanged.connect(self.save_action)
        layout.addWidget(self.action_combo)

        # Intervalo
        self.lbl_time = QLabel(f"Cada {self.manager.get('interval_s')} segundos")
        layout.addWidget(self.lbl_time)
        self.sld_time = QSlider(Qt.Horizontal)
        self.sld_time.setRange(5, 120); self.sld_time.setValue(self.manager.get("interval_s"))
        self.sld_time.valueChanged.connect(self.update_time)
        layout.addWidget(self.sld_time)

        self.chk_min = QCheckBox("Esconder al cerrar")
        self.chk_min.setChecked(self.manager.get("minimize_on_close"))
        self.chk_min.stateChanged.connect(lambda v: self.manager.set("minimize_on_close", v == 2))
        layout.addWidget(self.chk_min)
        layout.addStretch()

    def update_color(self, idx):
        c = self.colors[self.color_combo.currentText()]
        self.manager.set("loader_color", c); self.circle_widget.update()

    def update_time(self, v):
        self.manager.set("interval_s", v); self.lbl_time.setText(f"Cada {v} segundos")

    def save_action(self, idx):
        modes = ["move", "click", "key"]; self.manager.set("action_type", modes[idx])

class MouseJigglerWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = SettingsManager()
        self.elapsed_ms = 0
        self.is_active = False
        self.panel_visible = False
        self.timer = QTimer(); self.timer.timeout.connect(self.update_tick)
        self.init_ui(); self.setup_tray()

    def init_ui(self):
        self.setFixedSize(280, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.central_container = QWidget(self)
        self.central_container.setStyleSheet("background: transparent; border: none;")
        
        # El layout principal ya no es horizontal, sino que usaremos el contenedor para posicionar el overlay
        self.main_area = QWidget(self.central_container)
        self.main_area.setGeometry(0, 0, 280, 400)
        v_layout = QVBoxLayout(self.main_area)
        v_layout.setAlignment(Qt.AlignCenter)

        # SECCIÓN GATO
        circle_side = QWidget()
        circle_side.setFixedWidth(260)
        circle_v = QVBoxLayout(circle_side)
        circle_v.setAlignment(Qt.AlignCenter)
        
        self.circle = CircularWidget(manager=self.manager)
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(30); shadow.setColor(QColor(0,0,0,50)); shadow.setOffset(0, 10)
        self.circle.setGraphicsEffect(shadow)
        circle_v.addWidget(self.circle)
        v_layout.addWidget(circle_side)

        v_layout.addSpacing(20)
        
        # BOTONES
        controls = QHBoxLayout(); controls.setSpacing(15)
        self.btn_set = self.create_toy_button("⚙️", "#f1f5f9", "#475569", "Ajustes del Gatito")
        self.btn_play = self.create_toy_button("▶", "#22c55e", "white", "¡Empieza el juego!")
        self.btn_off = self.create_toy_button("✕", "#ef4444", "white", "Cerrar Aplicación")
        
        self.btn_set.clicked.connect(self.toggle_settings)
        self.btn_play.clicked.connect(self.toggle_service)
        self.btn_off.clicked.connect(self.handle_close)

        controls.addWidget(self.btn_set); controls.addWidget(self.btn_play); controls.addWidget(self.btn_off)
        v_layout.addLayout(controls)

        # EL OVERLAY DE AJUSTES (Se pone por encima de todo)
        self.side_panel = SettingsPanel(self.central_container, self.manager, self.circle, self.toggle_settings)
        self.side_panel.move(20, 20) # Posicionado sobre el gato
        self.side_panel.hide()

        self.setCentralWidget(self.central_container)

    def create_toy_button(self, text, bg, color, tip):
        btn = QPushButton(text); btn.setFixedSize(55, 55); btn.setToolTip(tip)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {bg}; color: {color}; font-size: 22px; font-weight: bold; border-radius: 27px; border: none; }}
            QPushButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 0.2), stop:1 {bg}); border: none; }}
            QPushButton:pressed {{ background-color: {bg}; }}
        """)
        eff = QGraphicsDropShadowEffect(); eff.setBlurRadius(12); eff.setOffset(0, 5); eff.setColor(QColor(0,0,0,50))
        btn.setGraphicsEffect(eff)
        return btn

    def toggle_settings(self):
        self.panel_visible = not self.panel_visible
        if self.panel_visible:
            self.side_panel.show()
            self.side_panel.raise_() # Asegurar que esté al frente
        else:
            self.side_panel.hide()

    def toggle_service(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.timer.start(100); self.btn_play.setText("■")
            self.btn_play.setStyleSheet(self.btn_play.styleSheet().replace("#22c55e", "#f97316"))
            self.tray.setToolTip("Move Mouse Pro - ¡Activo! 🐾")
        else:
            self.timer.stop(); self.btn_play.setText("▶")
            self.btn_play.setStyleSheet(self.btn_play.styleSheet().replace("#f97316", "#22c55e"))
            self.circle.set_progress(0); self.elapsed_ms = 0
            self.tray.setToolTip("Move Mouse Pro - En espera 💤")

    def update_tick(self):
        if self.circle.is_flashing: return
        self.elapsed_ms += 100
        interval = self.manager.get("interval_s") * 1000
        self.circle.set_progress(self.elapsed_ms / interval)
        if self.elapsed_ms >= interval:
            mode = self.manager.get("action_type")
            if mode == "move": pyautogui.moveRel(2, 0, duration=0.1); pyautogui.moveRel(-2, 0, duration=0.1)
            elif mode == "click": pyautogui.click()
            elif mode == "key": pyautogui.press('f15')
            self.circle.start_flash(); self.elapsed_ms = 0

    def handle_close(self):
        if self.manager.get("minimize_on_close"): self.hide()
        else: QApplication.quit()

    def setup_tray(self):
        self.tray = QSystemTrayIcon(self)
        pix = QPixmap(64,64); pix.fill(Qt.transparent)
        p = QPainter(pix); p.setBrush(QColor("#ff7eb9")); p.drawEllipse(8,8,48,48); p.end()
        self.tray.setIcon(QIcon(pix))
        self.tray.setToolTip("Move Mouse Pro - En espera 💤")
        menu = QMenu(); menu.addAction("Mostrar", self.showNormal); menu.addAction("Salir", QApplication.quit)
        self.tray.setContextMenu(menu); self.tray.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_pos = event.globalPosition().toPoint()
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    QToolTip.setFont(QFont('Segoe UI', 10))
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = MouseJigglerWidget()
    window.show()
    sys.exit(app.exec())
