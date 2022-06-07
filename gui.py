#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import GrouponMain
import webaas_client as wc
import utils


def main():
    if len(sys.argv) == 1:
        wc.register_app("wegroupon")
        wc.create_schema("proto/wegroupon.proto")
        utils.initialize_meta()
    else:
        wc.register_app("wegroupon", sys.argv[1])
    app = QApplication(sys.argv)
    main_window = GrouponMain()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
