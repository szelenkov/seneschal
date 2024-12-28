import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


def main():
    print("Starting test application...")
    app = QApplication(sys.argv)
    print("Created QApplication")

    window = QMainWindow()
    print("Created QMainWindow")

    button = QPushButton("Test Button", window)
    print("Created QPushButton")

    window.show()
    print("Showing window")

    return app.exec()

if __name__ == "__main__":
    main()
