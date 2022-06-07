from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
import wegroupon_pb2 as wg
import services
import asyncio


class GroupItemWidget(QWidget):
    def __init__(self, group_item: wg.G_Item):
        super().__init__()
        self.init_ui(group_item)

    def init_ui(self, group_item: wg.G_Item):
        self.group_item = group_item
        self.group_item_id_label = QLabel(f"商品编号: {group_item.g_i_id}")
        self.group_item_name_label = QLabel(f"商品名: {group_item.g_i_name}")
        group_item_name_font = self.group_item_name_label.font()
        group_item_name_font.setBold(True)
        self.group_item_name_label.setFont(group_item_name_font)
        self.group_item_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_item_description_label = QLabel(
            f"商品描述: {group_item.g_i_description}")
        self.group_item_description_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft)
        self.group_item_count_label = QLabel(f"数量: {group_item.g_i_count}")
        self.group_item_price_label = QLabel(f"价格:{group_item.g_i_price}元")
        self.group_item_price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_item_price_label.setFont(group_item_name_font)
        hbox = QHBoxLayout()
        hbox.addWidget(self.group_item_id_label)
        hbox.addWidget(self.group_item_name_label)
        hbox.addWidget(self.group_item_count_label)
        hbox.addWidget(self.group_item_price_label)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.group_item_description_label)
        self.setLayout(vbox)


class GroupInfoWidget(QWidget):
    # TODO：整理一下layout
    join_group_signal = pyqtSignal(wg.Group)

    def __init__(self, group: wg.Group):
        super().__init__()
        self.init_ui(group)

    def init_ui(self, group: wg.Group):
        self.group = group
        self.group_id_name_label = QLabel(f"团购号: {group.g_id}")
        self.group_name_label = QLabel(group.g_name)
        group_name_font = self.group_name_label.font()
        group_name_font.setBold(True)
        self.group_name_label.setFont(group_name_font)
        self.group_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_description_label = QLabel(f"团购名:{group.g_description}")
        self.group_description_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.group_owner_label = QLabel(f"团长: {group.g_owner_id}")
        self.group_owner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_start_time_label = QLabel(f"开始时间: {group.g_created_at}")
        self.group_start_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_end_time_label = QLabel(f"结束时间: {group.g_finished_at}")
        self.group_end_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_items_label = QLabel(f"商品:")
        self.group_items_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_items_label.setFont(group_name_font)
        self.group_items_widget = QWidget()
        self.group_items_widget.setLayout(QVBoxLayout())
        self.join_group_button = QPushButton("加入团购")
        self.join_group_button.clicked.connect(self.join_group)
        for group_item in group.g_items:
            self.group_items_widget.layout().addWidget(GroupItemWidget(group_item))
        hbox = QHBoxLayout()
        hbox.addWidget(self.group_id_name_label)
        hbox.addWidget(self.group_name_label)
        hbox.addWidget(self.group_owner_label)
        hbox.addWidget(self.group_start_time_label)
        hbox.addWidget(self.group_end_time_label)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.group_description_label)
        vbox.addWidget(self.group_items_label)
        vbox.addWidget(self.group_items_widget)
        vbox.addWidget(self.join_group_button)
        self.setLayout(vbox)

    def join_group(self):
        self.join_group_signal.emit(self.group)


class GroupListWidget(QWidget):
    successed = pyqtSignal(wg.Customer)

    def __init__(self, customer: wg.Customer):
        super().__init__()
        self.customer = customer
        self.init_ui()

    def init_ui(self):
        self.all_groups = asyncio.run(services.get_all_groups())
        self.groups_widget = QWidget()
        self.groups_widget.setLayout(QVBoxLayout())
        for group in self.all_groups:
            group_info_widget = GroupInfoWidget(group)
            group_info_widget.join_group_signal.connect(self.join_group)
            self.groups_widget.layout().addWidget(group_info_widget)
        self.setLayout(self.groups_widget.layout())

    def join_group(self, group: wg.Group):
        asyncio.run(services.join_group_with_param(
            self.customer.c_phone, group.g_id))
        self.successed.emit(group.g_owner)
