import asyncio
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox
from PyQt6.QtCore import pyqtSignal
import wegroupon_pb2 as wg
import services


class CreateGroupWidget(QWidget):

    successed = pyqtSignal(wg.Customer)
    item_id = 0

    def __init__(self, customer: wg.Customer):
        super().__init__()
        self.customer = customer
        self.init_ui()

    def init_ui(self):
        # 输入团购名，团购描述
        self.group_name = QLabel('团购名:')
        self.group_name_edit = QLineEdit()
        self.group_description = QLabel('团购描述:')
        self.group_description_edit = QLineEdit()

        # 增加商品按钮
        self.add_item_button = QPushButton('增加商品')
        self.add_item_button.clicked.connect(self.add_item)

        # 创建团购按钮
        self.create_group_button = QPushButton('创建团购')
        self.create_group_button.clicked.connect(self.create_group)

        # 商品相关
        self.item_label = QLabel('商品名:')
        self.item_edit = QLineEdit()
        self.item_price = QLabel('商品价格:')
        self.item_price_edit = QLineEdit()
        self.item_count = QLabel('商品数量:')
        self.item_count_edit = QLineEdit()
        self.item_description = QLabel('商品描述:')
        self.item_description_edit = QLineEdit()

        # 布局
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.group_name)
        self.layout.addWidget(self.group_name_edit)
        self.layout.addWidget(self.group_description)
        self.layout.addWidget(self.group_description_edit)

        self.layout.addWidget(self.item_label)
        self.layout.addWidget(self.item_edit)
        self.layout.addWidget(self.item_price)
        self.layout.addWidget(self.item_price_edit)
        self.layout.addWidget(self.item_count)
        self.layout.addWidget(self.item_count_edit)
        self.layout.addWidget(self.item_description)
        self.layout.addWidget(self.item_description_edit)

        self.layout.addWidget(self.add_item_button)
        self.layout.addWidget(self.create_group_button)

        self.setLayout(self.layout)

    def add_item(self):
        # TODO: add this
        print("not support yet")

    def create_group(self):
        print("create group")
        g_name = self.group_name_edit.text()
        g_description = self.group_description_edit.text()
        if g_name == '' or g_description == '':
            QMessageBox.warning(self, '警告', '请输入完整信息')
            return
        c_phone = self.customer.c_phone
        g_item_list = []
        item = wg.G_Item()
        item.g_i_id = self.item_id
        item.g_i_name = self.item_edit.text()
        item.g_i_description = self.item_description_edit.text()
        item.g_i_count = int(self.item_count_edit.text())
        item.g_i_price = int(self.item_price_edit.text())
        g_item_list.append(item)
        asyncio.run(services.create_group(
            g_name, g_description, c_phone, g_item_list))
        self.customer = asyncio.run(services.get_customer(c_phone))
        self.successed.emit(self.customer)
        QMessageBox.information(self, '提示', '创建成功')
