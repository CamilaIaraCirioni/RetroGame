from PyQt5.QtWidgets import QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QColor


def transition_flash(stacked_widget, new_index, color="#00FF00", duration=500):
    """Animación de flash (verde) entre pantallas de un QStackedWidget."""

    overlay = QWidget(stacked_widget)
    overlay.setStyleSheet(f"background-color: {color};")
    overlay.setGeometry(stacked_widget.rect())
    overlay.raise_()
    overlay.show()

    # Efecto de opacidad
    effect = QGraphicsOpacityEffect()
    overlay.setGraphicsEffect(effect)
    overlay.effect = effect  # mantener referencia

    # Animación fade-in
    fade_in = QPropertyAnimation(effect, b"opacity", overlay)
    fade_in.setDuration(duration // 2)
    fade_in.setStartValue(0)
    fade_in.setEndValue(1)
    fade_in.setEasingCurve(QEasingCurve.InOutQuad)

    # Animación fade-out
    fade_out = QPropertyAnimation(effect, b"opacity", overlay)
    fade_out.setDuration(duration // 2)
    fade_out.setStartValue(1)
    fade_out.setEndValue(0)
    fade_out.setEasingCurve(QEasingCurve.InOutQuad)

    # Guardar referencias (para que no se destruyan antes)
    overlay.fade_in = fade_in
    overlay.fade_out = fade_out

    # Cambiar pantalla después del primer fade
    def switch_screen():
        stacked_widget.setCurrentIndex(new_index)
        fade_out.start()

    # Eliminar overlay al terminar
    def cleanup():
        overlay.deleteLater()

    fade_in.finished.connect(switch_screen)
    fade_out.finished.connect(cleanup)

    fade_in.start()
