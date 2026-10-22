import os
import sys
import math
import random
from PySide6.QtCore import Qt, QTimer, QPoint, QRectF
from PySide6.QtGui import QPixmap, QPainter, QFont, QColor, QBrush, QPen
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QMessageBox

APP_NAME = "奶油猫桌面宠物"
WINDOW_W, WINDOW_H = 250, 300

def asset_path(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "assets", name)

class CatPet(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(WINDOW_W, WINDOW_H)

        self.cat = QPixmap(asset_path("cat.png"))
        self.drag_offset = None
        self.last_pos = QPoint(180, 160)
        self.mode = "闲逛"
        self.bubble = ""
        self.bubble_ticks = 0
        self.tick = 0
        self.ball_x, self.ball_y = 32.0, 242.0
        self.ball_vx, self.ball_vy = 2.8, -1.7
        self.ball_visible = True
        self.target = None
        self.wander_pause = random.randint(35, 85)
        self.setToolTip("左键戳戳猫咪 · 右键打开菜单")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_pet)
        self.timer.start(45)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.left() + 80, screen.top() + screen.height() - WINDOW_H - 50)

    def show_bubble(self, text, ticks=48):
        self.bubble = text
        self.bubble_ticks = ticks
        self.update()

    def update_pet(self):
        self.tick += 1
        if self.bubble_ticks > 0:
            self.bubble_ticks -= 1
            if self.bubble_ticks == 0:
                self.bubble = ""

        # Occasional independent cat activities.
        if self.mode not in ("追毛线球", "被戳互动"):
            if self.wander_pause > 0:
                self.wander_pause -= 1
            else:
                action = random.choice(["wander", "groom", "sleep", "ball"])
                if action == "groom":
                    self.mode = "舔毛"
                    self.show_bubble("舔舔毛，保持漂亮 ✨", 60)
                    self.wander_pause = 65
                elif action == "sleep":
                    self.mode = "打盹"
                    self.show_bubble("呼噜……Z z z", 75)
                    self.wander_pause = 80
                elif action == "ball":
                    self.mode = "追毛线球"
                    self.ball_visible = True
                    self.ball_x, self.ball_y = 30, 245
                    self.ball_vx, self.ball_vy = 3.4, -2.1
                    self.show_bubble("毛线球！让我抓住你！", 45)
                    self.wander_pause = 95
                else:
                    self.mode = "闲逛"
                    self.wander_pause = random.randint(55, 100)

        # Move the window around the desktop, keeping it inside the available screen.
        if self.mode == "闲逛" and self.tick % 3 == 0:
            if self.target is None or (self.pos() - self.target).manhattanLength() < 12:
                screen = QApplication.primaryScreen().availableGeometry()
                max_x = max(screen.left(), screen.right() - self.width() + 1)
                max_y = max(screen.top(), screen.bottom() - self.height() + 1)
                self.target = QPoint(random.randint(screen.left(), max_x),
                                     random.randint(screen.top(), max_y))
            dx = self.target.x() - self.x()
            dy = self.target.y() - self.y()
            self.move(self.x() + max(-3, min(3, dx)), self.y() + max(-3, min(3, dy)))

        # Animate the yarn ball inside the pet's transparent window.
        if self.mode == "追毛线球":
            self.ball_x += self.ball_vx
            self.ball_y += self.ball_vy
            if self.ball_x < 18 or self.ball_x > self.width() - 22:
                self.ball_vx *= -1
            if self.ball_y < 220 or self.ball_y > self.height() - 24:
                self.ball_vy *= -1
            if self.tick % 100 == 0:
                self.mode = "闲逛"
                self.show_bubble("抓到了……咦？又跑了！", 55)
                self.wander_pause = 50
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Soft speech bubble
        if self.bubble:
            painter.setPen(QPen(QColor(255, 255, 255, 225), 1))
            painter.setBrush(QBrush(QColor(255, 250, 238, 235)))
            painter.drawRoundedRect(QRectF(12, 5, 226, 36), 13, 13)
            painter.setPen(QColor(75, 63, 51))
            painter.setFont(QFont("Microsoft YaHei UI", 9))
            painter.drawText(QRectF(18, 7, 214, 32), Qt.AlignCenter, self.bubble)

        # Draw cat; tiny vertical bob during idle/activities.
        bob = int(math.sin(self.tick / 5.0) * 2)
        cat_rect = QRectF(6, 43 + bob, 238, 238)
        if not self.cat.isNull():
            painter.drawPixmap(cat_rect, self.cat, QRectF(self.cat.rect()))

        # Yarn ball: colorful and visible near the paws.
        if self.ball_visible:
            bx, by = self.ball_x, self.ball_y
            painter.setPen(QPen(QColor(90, 62, 50), 1.5))
            painter.setBrush(QBrush(QColor(230, 105, 128)))
            painter.drawEllipse(QPoint(int(bx), int(by)), 12, 12)
            painter.setPen(QPen(QColor(255, 224, 220), 2))
            painter.drawArc(QRectF(bx-8, by-7, 16, 14), 20*16, 130*16)
            painter.drawArc(QRectF(bx-8, by-7, 16, 14), 190*16, 120*16)
            painter.drawLine(int(bx+8), int(by+5), int(bx+17), int(by+10))

        # Small status label
        painter.setPen(QColor(90, 75, 63, 190))
        painter.setFont(QFont("Microsoft YaHei UI", 8))
        painter.drawText(QRectF(60, 279, 130, 17), Qt.AlignCenter, self.mode)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.open_menu(event.globalPosition().toPoint())
            return
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.mode = "被戳互动"
            line = random.choice([
                "喵！不要戳我的脸啦～",
                "你是在叫我吗？喵！",
                "呼噜呼噜……再摸一下嘛",
                "看什么？本猫很可爱吧！",
                "喵呜！我也戳你一下！",
                "想玩？把毛线球拿来！"
            ])
            self.show_bubble(line, 60)
            self.wander_pause = 65

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        if self.mode == "被戳互动":
            self.mode = "闲逛"

    def mouseDoubleClickEvent(self, event):
        self.mode = "打盹"
        self.show_bubble("两只眼睛闭起来……呼噜～", 75)

    def contextMenuEvent(self, event):
        self.open_menu(event.globalPos())

    def open_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background: #fffaf0; color: #473b32; padding: 6px; } QMenu::item { padding: 7px 22px; } QMenu::item:selected { background: #f4d7c4; }")
        play = menu.addAction("🧶  和毛线球玩")
        groom = menu.addAction("🧼  梳理毛毛")
        sleep = menu.addAction("💤  让猫咪睡觉")
        menu.addSeparator()
        top = menu.addAction("📌  切换置顶")
        hide_ball = menu.addAction("🧶  显示/隐藏毛线球")
        menu.addSeparator()
        about = menu.addAction("关于奶油猫")
        quit_action = menu.addAction("退出")
        selected = menu.exec(pos)
        if selected == play:
            self.mode = "追毛线球"
            self.ball_visible = True
            self.ball_x, self.ball_y = 32, 245
            self.ball_vx, self.ball_vy = 3.4, -2.1
            self.show_bubble("来追我呀！", 45)
        elif selected == groom:
            self.mode = "舔毛"
            self.show_bubble("认真洗脸中……", 70)
        elif selected == sleep:
            self.mode = "打盹"
            self.show_bubble("晚安，喵～", 85)
        elif selected == top:
            flags = self.windowFlags()
            self.setWindowFlag(Qt.WindowStaysOnTopHint, not bool(flags & Qt.WindowStaysOnTopHint))
            self.show()
        elif selected == hide_ball:
            self.ball_visible = not self.ball_visible
            self.update()
        elif selected == about:
            QMessageBox.information(self, "关于奶油猫", "奶油猫桌面宠物 1.0\n\n独立运行的 Windows 桌面小宠物。\n左键戳戳/拖动，双击让猫咪打盹，右键打开菜单。")
        elif selected == quit_action:
            QApplication.quit()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    pet = CatPet()
    pet.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
