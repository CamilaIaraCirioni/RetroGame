from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QRect, QEasingCurve, QPropertyAnimation, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont
from ranking.name_prompt import prompt_player_name
import random


class PongGame(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setFocusPolicy(Qt.StrongFocus)
        self.setStyleSheet("background-color: black;")

        # Estados
        self.mode = 1  # 1 jugador por defecto
        self.game_running = False
        self.showing_message = False

        self.init_ui()
        self.init_game()

        #  Interfaz y botones
    def init_ui(self):
        self.title = QLabel("🏓 PONG")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Courier New", 36, QFont.Bold))
        self.title.setStyleSheet("""
            QLabel {
                color: #FF69B4;
                text-shadow: 0px 0px 15px #FFB6C1;
                margin-bottom: 10px;
            }
        """)

        # Botones de control
        self.btn_start = self.create_button("▶ COMENZAR", self.start_game)
        self.btn_restart = self.create_button("🔁 REINICIAR", self.reset_game)
        self.btn_menu = self.create_button("⬅ MENÚ", lambda: self.stacked_widget.setCurrentIndex(0))

        # Botones de modo
        self.btn_1p = self.create_button("👤 1 JUGADOR", lambda: self.set_mode(1))
        self.btn_2p = self.create_button("👥 2 JUGADORES", lambda: self.set_mode(2))

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.btn_start)
        controls_layout.addWidget(self.btn_restart)
        controls_layout.addStretch()
        controls_layout.addWidget(self.btn_menu)

        mode_layout = QHBoxLayout()
        mode_layout.addStretch()
        mode_layout.addWidget(self.btn_1p)
        mode_layout.addWidget(self.btn_2p)
        mode_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title, alignment=Qt.AlignCenter)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(mode_layout)
        main_layout.addStretch()
        main_layout.setContentsMargins(40, 20, 40, 20)
        self.setLayout(main_layout)

        # Mensaje temporal (GOAL, WIN, etc.)
        self.message_label = QLabel("", self)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("""
            QLabel {
                color: #FFB6C1;
                font-size: 40px;
                font-family: 'Courier New';
                text-shadow: 0 0 10px #FF69B4;
            }
        """)
        self.message_label.hide()

    def create_button(self, text, func):
        btn = QPushButton(text)
        btn.setFixedSize(180, 45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(func)
        btn.setStyleSheet("""
    QPushButton {
        background-color: rgba(40, 0, 30, 180);
        color: #FF69B4;
        border: 2px solid #FF69B4;
        border-radius: 10px;
        font-family: 'Courier New';
        font-weight: bold;
        letter-spacing: 1px;
    }
    QPushButton:hover {
        background-color: #FF69B4;
        color: #000;
    }
    QPushButton:pressed {
        background-color: #FFB6C1;
        color: #000;
    }
""")
        return btn

    #Lógica del juego
    def init_game(self):
        w, h = self.width() or 800, self.height() or 600
        self.ball = QRect(w // 2 - 10, h // 2 - 10, 20, 20)
        self.ball_dx = random.choice([-6, 6])
        self.ball_dy = random.choice([-5, 5])

        self.paddle_left = QRect(30, h // 2 - 60, 12, 120)
        self.paddle_right = QRect(w - 42, h // 2 - 60, 12, 120)

        self.score_left = 0
        self.score_right = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)

    def start_game(self):
        self.reset_game()
        self.game_running = True
        if not self.timer.isActive():
            self.timer.start(25)
        self.setFocus()
        self.show_center_message("🏁 ¡EMPIEZA!", 800)

    def set_mode(self, mode):
        self.mode = mode
        self.reset_game()
        self.setFocus()
        self.show_center_message("👤 MODO " + ("1 JUGADOR" if mode == 1 else "2 JUGADORES"), 900)

    def reset_game(self):
        self.init_game()
        self.update()

   
    #  Lógica principal
    
    def update_game(self):
        if not self.game_running:
            return

        self.ball.moveTo(
    int(self.ball.x() + self.ball_dx),
    int(self.ball.y() + self.ball_dy)
)


        # Rebote vertical
        if self.ball.top() <= 0 or self.ball.bottom() >= self.height():
            self.ball_dy *= -1

        # Movimiento IA
        if self.mode == 1:
            if self.ball.center().y() > self.paddle_right.center().y():
                self.paddle_right.moveTop(self.paddle_right.top() + 5)
            elif self.ball.center().y() < self.paddle_right.center().y():
                self.paddle_right.moveTop(self.paddle_right.top() - 5)

        # Colisiones con paletas
        if self.ball.intersects(self.paddle_left) or self.ball.intersects(self.paddle_right):
            self.ball_dx *= -1.1
            self.ball_dy *= random.choice([-1, 1])

        # Puntos
        if self.ball.left() <= 0:
            self.score_right += 1
            self.reset_ball()
            self.show_center_message("🏆 PUNTO!", 800)
        elif self.ball.right() >= self.width():
            self.score_left += 1
            self.reset_ball()
            self.show_center_message("🔥 GOL!", 800)

        # Victoria
        if self.score_left >= 5 or self.score_right >= 5:
            self.game_running = False
            winner = "🏅 JUGADOR IZQ" if self.score_left > self.score_right else "🏅 JUGADOR DER"
            score = abs(self.score_left - self.score_right) * 100  # base simple
            prompt_player_name("pong", score)
            self.show_center_message(f"{winner}\n🎉 GANÓ EL JUEGO 🎉", 2500)
            self.timer.stop()

        self.update()

    def reset_ball(self):
        self.ball.moveCenter(self.rect().center())
        self.ball_dx *= -1
        self.ball_dy = random.choice([-5, 5])

    #  Controles
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_W and self.paddle_left.top() > 0:
            self.paddle_left.moveTop(self.paddle_left.top() - 20)
        elif key == Qt.Key_S and self.paddle_left.bottom() < self.height():
            self.paddle_left.moveTop(self.paddle_left.top() + 20)

        if self.mode == 2:
            if key == Qt.Key_Up and self.paddle_right.top() > 0:
                self.paddle_right.moveTop(self.paddle_right.top() - 20)
            elif key == Qt.Key_Down and self.paddle_right.bottom() < self.height():
                self.paddle_right.moveTop(self.paddle_right.top() + 20)

        #  Redimensionamiento
    def resizeEvent(self, event):
        w, h = self.width(), self.height()
        if hasattr(self, "paddle_left") and hasattr(self, "paddle_right"):
            self.paddle_left.moveTop(h // 2 - 60)
            self.paddle_right.moveLeft(w - 40)
            self.paddle_right.moveTop(h // 2 - 60)

        super().resizeEvent(event)


        #  Renderizado
    def paintEvent(self, event):
        painter = QPainter(self)

        # Fondo retro animado
        painter.fillRect(self.rect(), QColor(15, 15, 0))
        painter.setPen(QColor(60, 0, 40))
        for i in range(0, self.width(), 40):
            painter.drawLine(i, 0, i, self.height())

        # Centro
        painter.setPen(QColor("#FF69B4"))
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())

        # Paletas
        painter.setBrush(QColor("#FF69B4"))
        painter.drawRect(self.paddle_left)
        painter.setBrush(QColor("#FF69B4"))
        painter.drawRect(self.paddle_right)

        # Pelota
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(self.ball)

        # Puntaje
        painter.setPen(QColor("#FF69B4"))
        painter.setFont(QFont("Courier New", 30, QFont.Bold))
        painter.drawText(self.width() // 2 - 80, 100, f"{self.score_left} : {self.score_right}")

        # Letrero modo
        painter.setFont(QFont("Courier New", 16))
        painter.drawText(40, 50, "👤 1P" if self.mode == 1 else "👥 2P")
    
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self.setFocus)

    #  Mensajes visuales
    def show_center_message(self, text, duration=1000):
        self.message_label.setText(text)
        self.message_label.setGeometry(0, 0, self.width(), self.height())
        self.message_label.show()
        self.showing_message = True

        # Animación de aparición
        anim = QPropertyAnimation(self.message_label, b"pos")
        anim.setDuration(300)
        anim.setStartValue(QPoint(0, -50))
        anim.setEndValue(QPoint(0, 0))
        anim.setEasingCurve(QEasingCurve.OutBounce)
        anim.start()
        self.anim = anim

        QTimer.singleShot(duration, self.message_label.hide)
