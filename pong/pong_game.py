from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QRect, QEasingCurve, QPropertyAnimation, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
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
        self.key_up = False
        self.key_down = False
        self.key_w = False
        self.key_s = False
        self.MARGIN = 8
        self.flash_opacity = 0
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self.update_flash)


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
        self.score_label = QLabel("0 : 0")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setFont(QFont("Courier New", 28, QFont.Bold))
        self.score_label.setStyleSheet("color: #FF69B4; margin-top: -10px;")

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
        main_layout.addWidget(self.score_label, alignment=Qt.AlignCenter)
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
        w = self.width() if self.width() > 0 else 1280
        h = self.height() if self.height() > 0 else 720

        self.ball = QRect(0, 0, 20, 20)
        self.ball_dx = random.choice([-6, 6])
        self.ball_dy = random.choice([-5, 5])

        paddle_w = 12
        paddle_h = 120

        self.paddle_left = QRect(0, 0, paddle_w, paddle_h)
        self.paddle_right = QRect(0, 0, paddle_w, paddle_h)

        self.score_left = 0
        self.score_right = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)


    def start_game(self):
        self.reset_game()
        self.resizeEvent(None)
        self.reset_ball()
        self.game_running = True
        if not self.timer.isActive():
            self.timer.start(25)
        self.setFocus()
        self.show_center_message("🏁 ¡EMPIEZA!", 800)

    def set_mode(self, mode):
        self.mode = mode
        self.resizeEvent(None)
        self.reset_game()
        self.setFocus()
        self.show_center_message("👤 MODO " + ("1 JUGADOR" if mode == 1 else "2 JUGADORES"), 900)

    def reset_game(self):
        self.score_left = 0
        self.score_right = 0
        self.score_label.setText("0 : 0")

        self.reset_ball()

        self.resizeEvent(None)
        self.update()

    #  Lógica principal
    
    def update_game(self):
        if not self.game_running:
            return

    #  MOVIMIENTO DE PALETAS
    # Movimiento jugador 1
        if self.key_w:
            self.paddle_left.moveTop(self.paddle_left.top() - 8)
        elif self.key_s:
            self.paddle_left.moveTop(self.paddle_left.top() + 8)

    # Movimiento jugador 2
        if self.mode == 2:
            if self.key_up:
                self.paddle_right.moveTop(self.paddle_right.top() - 8)
            elif self.key_down:
                self.paddle_right.moveTop(self.paddle_right.top() + 8)

    #  LIMITAR PALETAS A LA CAJA
        px, py, pw, ph = self.play_area.x(), self.play_area.y(), self.play_area.width(), self.play_area.height()

    # Izquierda
        if self.paddle_left.top() < py + self.MARGIN:
            self.paddle_left.moveTop(py + self.MARGIN)
        elif self.paddle_left.bottom() > py + ph - self.MARGIN:
            self.paddle_left.moveBottom(py + ph - self.MARGIN)



    # Derecha
        if self.paddle_right.top() < py + self.MARGIN:
            self.paddle_right.moveTop(py + self.MARGIN)
        elif self.paddle_right.bottom() > py + ph - self.MARGIN:
            self.paddle_right.moveBottom(py + ph - self.MARGIN)

    # MOVER PELOTA DENTRO DE LA CAJA
        self.ball.moveTo(int(self.ball.x() + self.ball_dx),
                     int(self.ball.y() + self.ball_dy))

    # Rebote piso/techo
        if self.ball.top() <= py + self.MARGIN or self.ball.bottom() >= py + ph - self.MARGIN:
            self.ball_dy *= -1

    # Rebote con paletas
        if self.ball.intersects(self.paddle_left) or self.ball.intersects(self.paddle_right):
            self.ball_dx *= -1.1
            self.ball_dy *= random.choice([-1, 1])

    #  GOLES (solo bordes izquierdos y derechos de la caja)
        if self.ball.left() <= px + self.MARGIN:
            self.score_right += 1
            self.score_label.setText(f"{self.score_left} : {self.score_right}")
            self.reset_ball()
            self.start_flash()
            return

        if self.ball.right() >= px + pw - self.MARGIN:
            self.score_left += 1
            self.score_label.setText(f"{self.score_left} : {self.score_right}")
            self.reset_ball()
            self.start_flash()
            return

    #  IA (solo 1 jugador)
        if self.mode == 1:
            if self.ball.center().y() > self.paddle_right.center().y():
                self.paddle_right.moveTop(self.paddle_right.top() + 5)
            else:
                self.paddle_right.moveTop(self.paddle_right.top() - 5)

    #  VICTORIA
        if self.score_left >= 5 or self.score_right >= 5:
            self.game_running = False
            winner = "🏅 JUGADOR IZQ" if self.score_left > self.score_right else "🏅 JUGADOR DER"
            score = abs(self.score_left - self.score_right) * 100
            prompt_player_name("pong", score)
            self.show_center_message(f"{winner}\n🎉 GANÓ EL JUEGO 🎉", 2500)
            self.timer.stop()

        self.update()

    def start_flash(self):
        self.flash_opacity = 1.0
        self.flash_timer.start(30)

    def update_flash(self):
        self.flash_opacity -= 0.08
        if self.flash_opacity <= 0:
            self.flash_opacity = 0
            self.flash_timer.stop()
        self.update()


    def reset_ball(self):
    # centra la pelota dentro de la caja
        self.ball.moveCenter(self.play_area.center())
        self.ball_dx = random.choice([-6, 6])
        self.ball_dy = random.choice([-5, 5])


    #  Controles
    def keyPressEvent(self, event):
        key = event.key()

    # Izquierda (Jugador 1)
        if key == Qt.Key_W:
            self.key_w = True
        elif key == Qt.Key_S:
            self.key_s = True

    # Derecha (Jugador 2)
        if self.mode == 2:
            if key == Qt.Key_Up:
                self.key_up = True
            elif key == Qt.Key_Down:
                self.key_down = True

    def keyReleaseEvent(self, event):
        key = event.key()

        if key == Qt.Key_W:
            self.key_w = False
        elif key == Qt.Key_S:
            self.key_s = False
        elif key == Qt.Key_Up:
                self.key_up = False
        elif key == Qt.Key_Down:
            self.key_down = False


        #  Redimensionamiento
    def resizeEvent(self, event):
        super().resizeEvent(event)

        W = self.width()
        H = self.height()

    # Caja de juego proporcional al tamaño de pantalla
        box_width = int(W * 0.75)     # 65% del ancho de pantalla
        box_height = int(H * 0.60)    # 55% del alto de pantalla

        x = (W - box_width) // 2
        y = (H - box_height) // 2 + 120  # bajado para no tapar el título

        self.play_area = QRect(x, y, box_width, box_height)

    # Reposicionar paletas dentro de la caja
        if hasattr(self, "paddle_left"):
            self.paddle_left.moveLeft(self.play_area.x() + self.MARGIN + 8)
            self.paddle_left.moveTop(self.play_area.center().y() - self.paddle_left.height() // 2)

        if hasattr(self, "paddle_right"):
            self.paddle_right.moveLeft(self.play_area.right() - self.MARGIN - 8 - self.paddle_right.width())
            self.paddle_right.moveTop(self.play_area.center().y() - self.paddle_right.height() // 2)

    # Centrar pelota dentro de la caja
        if hasattr(self, "ball"):
            self.ball.moveCenter(self.play_area.center())

        self.update()




        #  Renderizado
    def paintEvent(self, event):
        painter = QPainter(self)

        # Fondo retro animado
        painter.fillRect(self.rect(), QColor(15, 15, 0))
        painter.setPen(QColor(60, 0, 40))
        for i in range(0, self.width(), 40):
            painter.drawLine(i, 0, i, self.height())
# Marco rosado estilo retro
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(40, 0, 30))  # rosa oscuro retro
        painter.drawRect(self.play_area)

    # Borde rosado retro
        painter.setPen(QPen(QColor(255, 120, 210), 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.play_area)
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


        # Letrero modo
        painter.setFont(QFont("Courier New", 16))
        painter.drawText(40, 50, "👤 1P" if self.mode == 1 else "👥 2P")
        
        if self.flash_opacity > 0:
            painter.setOpacity(self.flash_opacity)
            painter.fillRect(self.play_area, QColor(255, 170, 240))
            painter.setOpacity(1.0)


        




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

        