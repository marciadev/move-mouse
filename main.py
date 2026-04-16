import sys
import os
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QSystemTrayIcon, QMenu,
                             QSlider, QComboBox, QCheckBox, QFrame, QGraphicsDropShadowEffect,
                             QToolTip, QGraphicsOpacityEffect)
from PySide6.QtCore import QTimer, Qt, QPropertyAnimation, QEasingCurve, Property, QPoint, QRectF, QSize, QUrl
from PySide6.QtGui import (QIcon, QAction, QColor, QPainter, QPixmap, QPen, QBrush, 
                          QPainterPath, QFont, QConicalGradient, QImage)
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QAudioOutput
from PySide6.QtSvg import QSvgRenderer
import pyautogui

from settings_manager import SettingsManager

# --- CONTENEDOR CIRCULAR CON SOPORTE DE VIDEO ---
class CircularWidget(QWidget):
    def __init__(self, parent=None, manager=None):
        super().__init__(parent)
        self.manager = manager
        self.progress = 0.0
        self.is_flashing = False
        self.flash_state = True
        self.setFixedSize(220, 220)
        
        self.player = QMediaPlayer()
        self.video_sink = QVideoSink()
        self.player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self.update)
        
        self.audio_output = QAudioOutput()
        self.audio_output.setMuted(True)
        self.player.setAudioOutput(self.audio_output)

        self.video_list = ["saludo.mp4", "jugando.mp4", "cazando.mp4", "durmiendo.mp4"]
        self.current_video_idx = 0

        self.cycle_timer = QTimer()
        self.cycle_timer.timeout.connect(self.play_next_video)
        self.start_sequence()

        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.toggle_flash)
        self.flash_count = 0

    def start_sequence(self):
        self.current_video_idx = 0
        self.play_video(self.video_list[self.current_video_idx])
        self.cycle_timer.start(5000)

    def play_next_video(self):
        self.current_video_idx = (self.current_video_idx + 1) % len(self.video_list)
        self.play_video(self.video_list[self.current_video_idx])

    def play_video(self, filename):
        path = os.path.join(os.getcwd(), filename)
        if os.path.exists(path):
            self.player.setSource(QUrl.fromLocalFile(path))
            self.player.play()

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

        frame = self.video_sink.videoFrame()
        if frame.isValid():
            path = QPainterPath()
            path.addEllipse(thickness, thickness, self.width() - thickness*2, self.height() - thickness*2)
            painter.save()
            painter.setClipPath(path)
            image = frame.toImage()
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                x = (220 - scaled_pixmap.width()) / 2
                y = (220 - scaled_pixmap.height()) / 2
                painter.drawPixmap(x, y, scaled_pixmap)
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
                c = QColor(color_setting); c.setAlpha(alpha)
                pen = QPen(c, thickness, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen)
            start_angle = 90 * 16
            span_angle = -int((1.0 if self.is_flashing else self.progress) * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

# --- PANEL DE AJUSTES ---
class SettingsPanel(QFrame):
    def __init__(self, parent=None, manager=None, circle_widget=None, close_callback=None):
        super().__init__(parent)
        self.manager = manager
        self.circle_widget = circle_widget
        self.close_callback = close_callback
        self.setObjectName("SettingsPanel")
        self.setFixedSize(250, 330)
        
        self.accent_color = self.manager.get("loader_color")
        if self.accent_color == "rainbow": self.accent_color = "#ff7eb9"
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Ajustes 🐾")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2d3436; background: transparent;")
        header.addWidget(title)
        
        self.btn_close_x = QPushButton("✕")
        self.btn_close_x.setFixedSize(28, 28)
        self.btn_close_x.setCursor(Qt.PointingHandCursor)
        self.btn_close_x.clicked.connect(self.close_callback)
        header.addWidget(self.btn_close_x)
        self.layout.addLayout(header)

        self.layout.addWidget(QLabel("Color Favorito 🌸"))
        self.color_combo = QComboBox()
        self.colors = {"Arcoiris 🌈": "rainbow", "Rosa Pastel 🌸": "#ff7eb9", "Azul Mágico 💎": "#7eb6ff", "Verde Lima 🍏": "#72ec8a", "Naranja Dulce 🍊": "#ffb37e", "Morado Sueño 🔮": "#c37eff"}
        self.color_combo.addItems(list(self.colors.keys()))
        curr = self.manager.get("loader_color")
        for i, (k, v) in enumerate(self.colors.items()):
            if v == curr: self.color_combo.setCurrentIndex(i)
        self.color_combo.currentIndexChanged.connect(self.update_color)
        self.layout.addWidget(self.color_combo)

        self.layout.addWidget(QLabel("Actividad 🐾"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Mover Patita", "Hacer Clic", "Tecla F15"])
        mode_map = {"move": 0, "click": 1, "key": 2}
        self.action_combo.setCurrentIndex(mode_map.get(self.manager.get("action_type"), 0))
        self.action_combo.currentIndexChanged.connect(self.save_action)
        self.layout.addWidget(self.action_combo)

        self.lbl_time = QLabel(f"Cada {self.manager.get('interval_s')} segundos ⏱️")
        self.layout.addWidget(self.lbl_time)
        self.sld_time = QSlider(Qt.Horizontal)
        self.sld_time.setRange(5, 120); self.sld_time.setValue(self.manager.get("interval_s"))
        self.sld_time.valueChanged.connect(self.update_time)
        self.layout.addWidget(self.sld_time)
        self.layout.addStretch()
        
        self.update_panel_styles()

    def update_panel_styles(self):
        accent = self.accent_color
        bg_soft = QColor(accent); bg_soft.setAlpha(40); bg_soft_hex = bg_soft.name(QColor.HexArgb)
        svg_color = accent.replace("#", "%23")
        
        self.setStyleSheet(f"""
            #SettingsPanel {{ 
                background-color: white; 
                border-radius: 35px; 
                border: 4px solid {accent}; 
            }}
            QLabel {{ color: #2d3436; font-weight: bold; font-size: 12px; background: transparent; }}
            QComboBox {{ 
                background: {bg_soft_hex}; border: 2px solid #edeff2; border-radius: 12px; 
                padding: 6px 10px; color: #2d3436; font-weight: 500;
            }}
            QComboBox:hover {{ border: 2px solid {accent}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox::down-arrow {{ 
                image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='{svg_color}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><path d='M6 9l6 6 6-6'/></svg>");
                width: 12px; height: 12px;
            }}
            QComboBox QAbstractItemView {{ 
                background-color: white; border: 2px solid {accent}; border-radius: 12px; 
                selection-background-color: {bg_soft_hex}; selection-color: #2d3436; color: #2d3436; 
                outline: none; margin: 0px; border: none;
            }}
            QSlider::groove:horizontal {{ height: 10px; background: #f1f2f6; border-radius: 5px; }}
            QSlider::handle:horizontal {{ 
                background: {accent}; border: 3px solid white; width: 20px; height: 20px; 
                margin: -5px 0; border-radius: 10px; 
            }}
        """)
        self.btn_close_x.setStyleSheet(f"background: {accent}; color: white; border-radius: 14px; border: none; font-weight: bold;")
        
        for combo in [self.color_combo, self.action_combo]:
            if combo.view() and combo.view().window():
                combo.view().window().setAttribute(Qt.WA_TranslucentBackground)
                combo.view().window().setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

    def update_color(self, idx):
        c_key = self.color_combo.currentText(); new_c = self.colors[c_key]
        self.manager.set("loader_color", new_c)
        self.accent_color = new_c if new_c != "rainbow" else "#ff7eb9"
        self.update_panel_styles(); self.circle_widget.update()

    def update_time(self, v):
        self.manager.set("interval_s", v); self.lbl_time.setText(f"Cada {v} segundos ⏱️")

    def save_action(self, idx):
        modes = ["move", "click", "key"]; self.manager.set("action_type", modes[idx])

# --- VENTANA PRINCIPAL ---
class MouseJigglerWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = SettingsManager()
        self.elapsed_ms = 0
        self.is_active = False
        self.panel_visible = False
        
        self.timer = QTimer(); self.timer.timeout.connect(self.update_tick)
        self.ui_timer = QTimer(); self.ui_timer.setSingleShot(True); self.ui_timer.timeout.connect(self.fade_out_controls)
        
        self.init_ui()
        self.setup_tray()
        
        self.setMouseTracking(True); self.central_container.setMouseTracking(True)
        self.reset_ui_timer()
        
        if os.path.exists("logo.png"):
            app_icon = QIcon("logo.png")
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)

    def init_ui(self):
        self.setFixedSize(280, 420)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        self.central_container = QWidget(self); self.setCentralWidget(self.central_container)
        self.main_area = QWidget(self.central_container); self.main_area.setGeometry(0, 0, 280, 420)
        v_layout = QVBoxLayout(self.main_area); v_layout.setAlignment(Qt.AlignCenter)

        self.circle = CircularWidget(manager=self.manager)
        shadow = QGraphicsDropShadowEffect(); shadow.setBlurRadius(30); shadow.setColor(QColor(0,0,0,50)); shadow.setOffset(0, 10)
        self.circle.setGraphicsEffect(shadow)
        v_layout.addWidget(self.circle, 0, Qt.AlignCenter); v_layout.addSpacing(20)

        self.controls_widget = QWidget(); self.controls_widget.setFixedHeight(80)
        self.controls_layout = QHBoxLayout(self.controls_widget); self.controls_layout.setSpacing(10)
        
        self.opacity_effect = QGraphicsOpacityEffect(self.controls_widget); self.controls_widget.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity"); self.fade_anim.setDuration(500); self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.btn_set = self.create_toy_button("#f1f5f9", "Ajustes"); self.set_btn_icon(self.btn_set, "settings", "#475569")
        self.btn_play = self.create_toy_button("#22c55e", "Activar"); self.set_btn_icon(self.btn_play, "play", "white")
        self.btn_min = self.create_toy_button("#7eb6ff", "Minimizar"); self.set_btn_icon(self.btn_min, "minimize", "white")
        self.btn_off = self.create_toy_button("#ef4444", "Cerrar"); self.set_btn_icon(self.btn_off, "close", "white")
        
        self.btn_set.clicked.connect(self.toggle_settings)
        self.btn_play.clicked.connect(self.toggle_service)
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_off.clicked.connect(self.handle_close)

        for b in [self.btn_set, self.btn_play, self.btn_min, self.btn_off]: self.controls_layout.addWidget(b)
        v_layout.addWidget(self.controls_widget)

        self.side_panel = SettingsPanel(self.central_container, self.manager, self.circle, self.toggle_settings)
        self.side_panel.move(15, 20); self.side_panel.hide()

    def set_btn_icon(self, btn, icon_type, color):
        c = QColor(color).name()
        icons = {
            "settings": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>""",
            "play": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{c}"><path d="M8 5v14l11-7z"/></svg>""",
            "stop": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="{c}"><rect x="6" y="6" width="12" height="12" rx="3"/></svg>""",
            "minimize": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"><line x1="5" y1="12" x2="19" y2="12"/></svg>""",
            "close": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>"""
        }
        svg_data = icons.get(icon_type, "").encode('utf-8')
        pixmap = QPixmap(QSize(22, 22)); pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap); renderer = QSvgRenderer(svg_data); renderer.render(painter); painter.end()
        btn.setIcon(QIcon(pixmap)); btn.setIconSize(QSize(22, 22))

    def reset_ui_timer(self):
        if self.fade_anim.state() == QPropertyAnimation.Running: self.fade_anim.stop()
        if self.opacity_effect.opacity() < 1.0:
            self.fade_anim.setStartValue(self.opacity_effect.opacity()); self.fade_anim.setEndValue(1.0); self.fade_anim.start()
        self.controls_widget.setEnabled(True)
        if not self.panel_visible: self.ui_timer.start(3000)

    def fade_out_controls(self):
        if self.panel_visible: return 
        self.fade_anim.setStartValue(self.opacity_effect.opacity()); self.fade_anim.setEndValue(0.0); self.fade_anim.start()
        self.controls_widget.setEnabled(False)

    def mouseMoveEvent(self, event):
        self.reset_ui_timer()
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def enterEvent(self, event):
        self.reset_ui_timer(); super().enterEvent(event)

    def create_toy_button(self, bg, tip):
        btn = QPushButton(); btn.setFixedSize(50, 50); btn.setToolTip(tip)
        btn.setStyleSheet(f"QPushButton {{ background-color: {bg}; border-radius: 25px; border: none; outline: none; }} QPushButton:hover {{ opacity: 0.8; }}")
        eff = QGraphicsDropShadowEffect(); eff.setBlurRadius(12); eff.setOffset(0, 5); eff.setColor(QColor(0,0,0,50))
        btn.setGraphicsEffect(eff)
        return btn

    def toggle_settings(self):
        self.panel_visible = not self.panel_visible
        if self.panel_visible:
            self.side_panel.show(); self.side_panel.raise_(); self.ui_timer.stop(); self.reset_ui_timer()
        else:
            self.side_panel.hide(); self.ui_timer.start(1000)

    def toggle_service(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.timer.start(100); self.btn_play.setStyleSheet(self.btn_play.styleSheet().replace("#22c55e", "#f97316"))
            self.set_btn_icon(self.btn_play, "stop", "white")
            self.tray.setToolTip("Fluffy Paw Pro - Activo 🐾")
        else:
            self.timer.stop(); self.btn_play.setStyleSheet(self.btn_play.styleSheet().replace("#f97316", "#22c55e"))
            self.set_btn_icon(self.btn_play, "play", "white")
            self.circle.set_progress(0); self.elapsed_ms = 0
            self.tray.setToolTip("Fluffy Paw Pro - Desactivado 💤")

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
        self.tray.setToolTip("Fluffy Paw Pro - Desactivado 💤")
        if os.path.exists("logo.png"): self.tray.setIcon(QIcon("logo.png"))
        else:
            pix = QPixmap(64,64); pix.fill(Qt.transparent); p = QPainter(pix); p.setBrush(QColor("#ff7eb9")); p.drawEllipse(8,8,48,48); p.end()
            self.tray.setIcon(QIcon(pix))
        menu = QMenu(); menu.addAction("Mostrar", self.showNormal); menu.addAction("Salir", QApplication.quit)
        self.tray.setContextMenu(menu); self.tray.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_pos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet("*{outline: none;}")
    window = MouseJigglerWidget()
    window.show()
    sys.exit(app.exec())
