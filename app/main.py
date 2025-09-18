from PySide6.QtWidgets import QApplication, QLabel
import sys

def main():
    app = QApplication(sys.argv)
    lbl = QLabel("timeline – it works!")
    lbl.resize(320, 80)
    lbl.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
