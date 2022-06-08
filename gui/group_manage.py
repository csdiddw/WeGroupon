import asyncio
from copy import deepcopy
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit, QMessageBox, QScrollArea, QGridLayout
from PyQt6.QtCore import pyqtSignal
import wegroupon_pb2 as wg
import services


class InputItemWidget(QWidget):
    changed = pyqtSignal(wg.G_Item)
    item = wg.G_Item()

    def __init__(self, id):
        super().__init__()
        self.item.g_i_id = id
        self.init_ui()

    def init_ui(self):
        self.item_label = QLabel('商品名:')
        self.item_edit = QLineEdit()
        self.item_edit.textChanged.connect(self.change_item_name)
        self.item_price = QLabel('商品价格:')
        self.item_price_edit = QLineEdit()
        self.item_price_edit.textChanged.connect(self.change_item_price)
        self.item_count = QLabel('商品数量:')
        self.item_count_edit = QLineEdit()
        self.item_count_edit.textChanged.connect(self.change_item_count)
        self.item_description = QLabel('商品描述:')
        self.item_description_edit = QLineEdit()
        self.item_description_edit.textChanged.connect(
            self.change_item_description)
        self.item_layout = QGridLayout()
        self.item_layout.addWidget(self.item_label, 0, 0)
        self.item_layout.addWidget(self.item_edit, 0, 1)
        self.item_layout.addWidget(self.item_price, 1, 0)
        self.item_layout.addWidget(self.item_price_edit, 1, 1)
        self.item_layout.addWidget(self.item_count, 2, 0)
        self.item_layout.addWidget(self.item_count_edit, 2, 1)
        self.item_layout.addWidget(self.item_description, 3, 0)
        self.item_layout.addWidget(self.item_description_edit, 3, 1)
        self.item_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.item_layout)

    def change_item_name(self):
        self.item.g_i_name = self.item_edit.text()
        self.changed.emit(self.item)

    def change_item_price(self):
        try:
            self.item.g_i_price = float(self.item_price_edit.text())
            self.changed.emit(self.item)
        except:
            pass

    def change_item_count(self):
        try:
            self.item.g_i_count = int(self.item_count_edit.text())
            self.changed.emit(self.item)
        except:
            pass

    def change_item_description(self):
        self.item.g_i_description = self.item_description_edit.text()
        self.changed.emit(self.item)


class CreateGroupWidget(QWidget):

    successed = pyqtSignal(wg.Customer)
    item_id = 0
    items = {}

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
        self.items_widget = QWidget()
        self.items_widget.setLayout(QVBoxLayout())
        self.items_area = QScrollArea()
        self.items_area.setWidget(self.items_widget)
        self.items_area.setWidgetResizable(True)
        # 布局
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.group_name)
        self.layout.addWidget(self.group_name_edit)
        self.layout.addWidget(self.group_description)
        self.layout.addWidget(self.group_description_edit)

        self.layout.addWidget(self.items_area)

        self.layout.addWidget(self.add_item_button)
        self.layout.addWidget(self.create_group_button)

        self.setLayout(self.layout)

    def add_item(self):
        self.items[self.item_id] = wg.G_Item()
        item_widget = InputItemWidget(self.item_id)
        item_widget.changed.connect(self.change_item)
        self.items_widget.layout().addWidget(item_widget)
        self.item_id += 1

    def change_item(self, item):
        self.items[item.g_i_id] = deepcopy(item)

    def create_group(self):
        print("create group")
        g_name = self.group_name_edit.text()
        g_description = self.group_description_edit.text()
        if g_name == '' or g_description == '':
            QMessageBox.warning(self, '警告', '请输入完整信息')
            return
        c_phone = self.customer.c_phone
        g_item_list = []
        for item in self.items.values():
            g_item_list.append(item)
        asyncio.run(services.create_group_with_param(
            g_name, g_description, c_phone, g_item_list))
        self.customer = asyncio.run(services.get_customer(c_phone))
        self.successed.emit(self.customer)
        QMessageBox.information(self, '提示', '创建成功')

# 增加一个join group的逻辑，可以选择一个团购中的商品，然后加入团购
