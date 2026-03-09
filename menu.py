from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel,
    QSpacerItem, QSizePolicy, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPixmap, QMovie
from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, QPoint, Qt, QTimer
)
from transitions import transition_flash
from paths import resource_path
import sys


class GameMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setStyleSheet("background-color: black;")
        self.animations = []
        self.ruta_fondo = resource_path('assets/fondo.gif')
        self._setup_background()
        self._setup_ui()

    #  Fondo dinámico
    def _setup_background(self):
        self.bg_label = QLabel(self)
        self.bg_label.setScaledContents(True)

        self.bg_movie = QMovie(self.ruta_fondo)
        self.bg_label.setMovie(self.bg_movie)
        self.bg_movie.start()

    # Interfaz principal
    def _setup_ui(self):
        # Título
        self.title = QLabel("🎮 RETRO GAME ", self)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.title.setStyleSheet("""
            QLabel {
                color: #FFD700;
                border: 3px solid #FF69B4;
                border-radius: 10px;
                padding: 15px;
                background-color: rgba(0, 0, 0, 100);
                letter-spacing: 4px;
                text-shadow:
                    2px 2px 2px #FF69B4,
                    0 0 10px #FFD700,
                    0 0 20px #FF1493;
            }
        """)

        # Botones de juegos
        self.buttons = []

# Mapeo: índice → color del flash
        flash_colors = {
    1: "#00FF00",  # Snake - verde
    2: "#00FFFF",  # Minesweeper - celeste
    3: "#ff06ff", # Pong - rosa
    4: "#E5FF00"  # Ranking - amarillo
}

        for label, index in [
            ("🐍 SNAKE", 1), 
            ("💣 MINES", 2),
            ("🏓 PONG", 3),
            ("🏆 RANKING", 4)]:
            btn = self._create_button(label)
            btn.clicked.connect(lambda _, i=index: transition_flash(self.stacked_widget, i, flash_colors[i]))
            self.buttons.append(btn)

        # Botón salir
        self.exit_btn = self._create_button("❌", size=50)
        self.exit_btn.clicked.connect(lambda: sys.exit())

        # Layout principal
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(60, 60, 60, 60)
        v_layout.setSpacing(35)
        v_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        v_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        v_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        for btn in self.buttons:
            v_layout.addWidget(btn, alignment=Qt.AlignCenter)
        v_layout.addSpacerItem(QSpacerItem(10, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        v_layout.addWidget(self.exit_btn, alignment=Qt.AlignRight)

        # Contenedor centrado
        self.main_container = QWidget(self)
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addLayout(v_layout)
        h_layout.addStretch()
        self.main_container.setLayout(h_layout)
        self.main_container.setStyleSheet("background-color: transparent;")

    #  Creadores auxiliares
    def _create_button(self, text, size=None):
        btn = QPushButton(text, self)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(20, 0, 40, 200);
                color: #00FFFF;
                border: 3px solid #FF69B4;
                border-radius: 12px;
                font-family: 'Courier New';
                font-weight: bold;
                letter-spacing: 2px;
                text-shadow:
                    0 0 10px #FF69B4,
                    0 0 20px #00FFFF;
            }
            QPushButton:hover {
                background-color: #FF69B4;
                color: #000;
                border-color: #FFD700;
            }
            QPushButton:pressed {
                background-color: #FFD700;
                color: #000;
            }
        """)
        if size:
            btn.setFixedSize(size, size)
        return btn

    #  Animaciones de entrada 
    def showEvent(self, event):
        super().showEvent(event)
        self._animate_entry()

    def _animate_entry(self):
        self.animations.clear()

        # Título bajando desde arriba
        title_anim = QPropertyAnimation(self.title, b"pos")
        title_anim.setDuration(700)
        title_anim.setStartValue(self.title.pos() - QPoint(0, 150))
        title_anim.setEndValue(self.title.pos())
        title_anim.setEasingCurve(QEasingCurve.OutBounce)
        title_anim.start()
        self.animations.append(title_anim)

        # Botones desde la izquierda
        for i, btn in enumerate(self.buttons):
            anim = QPropertyAnimation(btn, b"pos")
            anim.setDuration(700 + i * 120)
            anim.setStartValue(btn.pos() - QPoint(400, 0))
            anim.setEndValue(btn.pos())
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
            self.animations.append(anim)

    #  Redimensionamiento 
    def resizeEvent(self, event):
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        font_size = max(28, self.width() // 25)
        self.title.setFont(QFont("Courier New", font_size, QFont.Bold))

        btn_font = QFont("Courier New", max(16, self.width() // 60))
        btn_height = max(50, self.height() // 12)
        btn_width = max(250, self.width() // 6)
        for btn in self.buttons:
            btn.setFont(btn_font)
            btn.setFixedSize(btn_width, btn_height)

        self.main_container.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
