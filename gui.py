#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QGridLayout, QMessageBox
from gui.main_window import GrouponMain
import webaas_client as wc
import utils


def main():
    wc.register_app("wegroupon")
    wc.create_schema("proto/wegroupon.proto")
    utils.initialize_meta()
    app = QApplication(sys.argv)
    main_window = GrouponMain()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
