from PyQt6.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from gui.account import RegisterWidget, LoginWidget, UserInfoWidget
from gui.group_list import GroupListWidget
from gui.group_manage import CreateGroupWidget


class InitialMenu(QWidget):
    register_signal = pyqtSignal()
    login_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.register_button = QPushButton('注册')
        self.register_button.clicked.connect(self.register)
        self.login_button = QPushButton('登录')
        self.login_button.clicked.connect(self.login)
        self.layout = QGridLayout()
        self.layout.addWidget(self.register_button, 0, 0)
        self.layout.addWidget(self.login_button, 0, 1)
        self.setLayout(self.layout)

    def register(self):
        self.register_signal.emit()

    def login(self):
        self.login_signal.emit()


class GrouponMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.customer = None
        self.init_ui()

    def show_initial_menu(self):
        self.initial_menu = InitialMenu()
        self.setCentralWidget(self.initial_menu)
        self.initial_menu.register_signal.connect(self.register)
        self.initial_menu.login_signal.connect(self.login)

    def init_ui(self):
        self.statusBar().showMessage("欢迎使用WeGroupon")
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('WeGroupon')

        showUserInfoAct = QAction('用户信息', self)
        showUserInfoAct.triggered.connect(self.show_user_info)
        showGroupListAct = QAction('显示团购列表', self)
        showGroupListAct.triggered.connect(self.show_group_list)
        createGroupAct = QAction('创建团购', self)
        createGroupAct.triggered.connect(self.create_group)

        menuBar = self.menuBar()
        showUserInfoActMenu = menuBar.addMenu('用户信息')
        showUserInfoActMenu.addAction(showUserInfoAct)

        showGroupListMenu = menuBar.addMenu('团购列表')
        showGroupListMenu.addAction(showGroupListAct)

        createGroupListMenu = menuBar.addMenu('创建团购')
        createGroupListMenu.addAction(createGroupAct)

        self.show_initial_menu()
        self.show()

    def register(self):
        self.register_widget = RegisterWidget()
        # 跳转到注册界面
        self.setCentralWidget(self.register_widget)
        self.register_widget.successed.connect(
            self.login_or_register_successed)

    def login_or_register_successed(self, customer):
        self.customer = customer
        self.show_user_info()
        self.statusBar().showMessage("你好，{}".format(customer.c_name))

    def login(self):
        self.login_widget = LoginWidget()
        # 跳转到登录界面
        self.setCentralWidget(self.login_widget)
        self.login_widget.successed.connect(self.login_or_register_successed)
        self.login_widget.register.connect(self.register)

    def show_user_info(self):
        if self.customer is None:
            self.login()
            return
        self.user_info_widget = UserInfoWidget(self.customer)
        self.setCentralWidget(self.user_info_widget)
        self.user_info_widget.back.connect(self.show_initial_menu)

    def show_group_list(self):
        if self.customer is None:
            self.login()
            return
        self.group_list_widget = GroupListWidget(self.customer)
        self.setCentralWidget(self.group_list_widget)

    def create_group(self):
        if self.customer is None:
            self.login()
            return
        self.create_group_widget = CreateGroupWidget(self.customer)
        self.setCentralWidget(self.create_group_widget)
