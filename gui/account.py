from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QVBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSignal
import wegroupon_pb2 as wg
import services
import asyncio


class RegisterWidget(QWidget):
    successed = pyqtSignal(wg.Customer)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 输入手机号、用户名和密码
        self.phone_label = QLabel('手机号:')
        self.phone_edit = QLineEdit()
        self.username_label = QLabel('用户名:')
        self.username_edit = QLineEdit()
        self.password_label = QLabel('密码:')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        # 注册按钮
        self.register_button = QPushButton('注册')
        self.register_button.clicked.connect(self.register)
        # 注册布局
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_edit)
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.register_button)
        self.setLayout(self.layout)

    def register(self):
        phone = self.phone_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        if phone == '' or username == '' or password == '':
            QMessageBox.warning(self, '警告', '请填写完整信息')
            return
        customer = asyncio.run(
            services.register_with_param(phone, username, password))
        if customer is None:
            QMessageBox.warning(self, '警告', '注册失败')
            return
        QMessageBox.information(self, '提示', '注册成功')
        self.successed.emit(customer)


class LoginWidget(QWidget):
    successed = pyqtSignal(wg.Customer)
    register = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 输入手机号、用户名和密码
        self.phone_label = QLabel('手机号:')
        self.phone_edit = QLineEdit()
        self.password_label = QLabel('密码:')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        # 登录按钮
        self.login_button = QPushButton('登录')
        self.login_button.clicked.connect(self.login)
        # 注册按钮
        self.register_button = QPushButton('注册')
        self.register_button.clicked.connect(self.register.emit)
        # 登录布局
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_edit)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)
        self.setLayout(self.layout)

    def login(self):
        phone = self.phone_edit.text()
        password = self.password_edit.text()
        if phone == '' or password == '':
            QMessageBox.warning(self, '警告', '请填写完整信息')
            return
        customer = asyncio.run(services.login_with_param(phone, password))
        if customer is None:
            QMessageBox.warning(self, '警告', '登录失败')
            return
        QMessageBox.information(self, '提示', '登录成功')
        self.successed.emit(customer)


class UserInfoWidget(QWidget):
    """
    显示用户信息
    """
    back = pyqtSignal()

    def __init__(self, customer):
        super().__init__()
        self.customer = customer
        self.init_ui()

    def init_ui(self):
        self.username_label = QLabel('用户名:')
        self.username_value = QLabel(self.customer.c_name)
        self.phone_label = QLabel('手机号:')
        self.phone_value = QLabel(self.customer.c_phone)
        self.owned_groups_label = QLabel('发起的团购列表:')
        self.owned_groups_value = QLabel(
            ','.join(str(x) for x in self.customer.c_owned_groups))
        self.participated_groups_label = QLabel('参与的团购列表:')
        self.participated_groups_value = QLabel(
            ','.join(str(x) for x in self.customer.c_participated_groups))
        self.back_button = QPushButton('返回')
        self.back_button.clicked.connect(self.back_clicked)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_value)
        self.layout.addWidget(self.phone_label)
        self.layout.addWidget(self.phone_value)
        self.layout.addWidget(self.owned_groups_label)
        self.layout.addWidget(self.owned_groups_value)
        self.layout.addWidget(self.participated_groups_label)
        self.layout.addWidget(self.participated_groups_value)
        self.setLayout(self.layout)

    def back_clicked(self):
        self.back.emit()
