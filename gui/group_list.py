from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox,QScrollArea,QGridLayout,QCheckBox,QSlider
from PyQt6.QtCore import pyqtSignal, Qt
import wegroupon_pb2 as wg
import services
import asyncio



class GroupItemWidget(QWidget):
    checked = pyqtSignal(wg.G_P_Item)
    unchecked = pyqtSignal(wg.G_P_Item)
    def __init__(self, group_item: wg.G_Item):
        super().__init__()
        self.init_ui(group_item)

    def init_ui(self, group_item: wg.G_Item):
        group_item.g_i_price = group_item.g_i_price + 1
        self.group_item = group_item
        self.buy_item= wg.G_P_Item()
        self.buy_item.g_p_id = group_item.g_i_id
        self.buy_item.g_p_count = 0
        self.buy_item.g_p_price = group_item.g_i_price
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
        self.number_chooser = QSlider(Qt.Orientation.Horizontal)
        self.number_chooser.setMinimum(1)
        self.number_chooser.setMaximum(group_item.g_i_count)
        self.number_chooser.setValue(self.buy_item.g_p_count)
        self.number_chooser.valueChanged.connect(self.number_chooser_changed)
        self.number_label = QLabel(f"{self.buy_item.g_p_count}")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.check_box = QCheckBox()
        self.check_box.setChecked(False)
        self.check_box.stateChanged.connect(self.check_box_changed)
        self.sum_price_label = QLabel(f"小计:{self.buy_item.g_p_count*self.group_item.g_i_price}元")
        hbox = QHBoxLayout()
        hbox.addWidget(self.group_item_id_label)
        hbox.addWidget(self.group_item_name_label)
        hbox.addWidget(self.group_item_count_label)
        hbox.addWidget(self.group_item_price_label)
        hbox.addWidget(self.number_chooser)
        hbox.addWidget(self.number_label)
        hbox.addWidget(self.check_box)
        hbox.addWidget(self.sum_price_label)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.group_item_description_label)
        self.setLayout(vbox)

    def check_box_changed(self):
        if self.check_box.isChecked():
            self.checked.emit(self.buy_item)
        else:
            self.unchecked.emit(self.buy_item)
    
    def number_chooser_changed(self):
        self.buy_item.g_p_count = self.number_chooser.value()
        self.number_label.setText(f"{self.buy_item.g_p_count}")
        self.sum_price_label.setText(f"小计:{self.buy_item.g_p_count*self.group_item.g_i_price}元")


class GroupInfoWidget(QWidget):
    # TODO：整理一下layout
    join_group_signal = pyqtSignal(wg.Group,list)
    finish_group_signal = pyqtSignal(wg.Group)
    buy_items = []

    def __init__(self, group: wg.Group,customer: wg.Customer):
        super().__init__()
        self.init_ui(group,customer)

    def init_ui(self, group: wg.Group,customer: wg.Customer):
        self.group = group
        self.group_id_name_label = QLabel(f"团购号: {group.g_id}")
        self.group_name_label = QLabel(f"团购名:{group.g_name}")
        group_name_font = self.group_name_label.font()
        group_name_font.setBold(True)
        self.group_name_label.setFont(group_name_font)
        self.group_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.group_description_label = QLabel(f"团购描述:{group.g_description}")
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
        self.total_price=0
        for buy_item in self.buy_items:
            self.total_price += buy_item.g_p_count*buy_item.g_i_price
        self.sum_price_label = QLabel(f"总计: {self.total_price}元")
        self.join_group_button = QPushButton("加入团购")
        self.join_group_button.clicked.connect(self.join_group)
        self.finish_group_button = QPushButton("提醒取货")
        self.finish_group_button.clicked.connect(self.finish_group)

        # 初始化商品列表

        for group_item in group.g_items:
            item_widget=GroupItemWidget(group_item)
            self.group_items_widget.layout().addWidget(item_widget)
            item_widget.checked.connect(self.item_checked)
            item_widget.unchecked.connect(self.item_unchecked)

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
        vbox.addWidget(self.sum_price_label)
        vbox.addWidget(self.join_group_button)
        if customer.c_phone == group.g_owner_id:
            vbox.addWidget(self.finish_group_button)
        self.setLayout(vbox)

    def join_group(self):
        self.join_group_signal.emit(self.group,self.buy_items)

    def finish_group(self):
        self.finish_group_signal.emit(self.group)
    
    def item_checked(self, group_item):
        self.buy_items.append(group_item)
        self.total_price += group_item.g_p_price * group_item.g_p_count
        self.sum_price_label.setText(f"总计: {self.total_price}元")
    
    def item_unchecked(self, group_item):
        self.buy_items.remove(group_item)
        self.total_price -= group_item.g_p_price * group_item.g_p_count
        self.sum_price_label.setText(f"总计: {self.total_price}元")


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
            group_info_widget = GroupInfoWidget(group,self.customer)
            group_info_widget.join_group_signal.connect(self.join_group)
            group_info_widget.finish_group_signal.connect(self.finish_group)
            self.groups_widget.layout().addWidget(group_info_widget)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.groups_widget)
        self.scroll_area.setWidgetResizable(True)
        vbox = QVBoxLayout()
        vbox.addWidget(self.scroll_area)
        self.setLayout(vbox)

    def join_group(self, group:wg.Group,items:list):
        print("join group")
        asyncio.run(services.join_group_with_param(
            self.customer.c_phone, group.g_id,items))
        QMessageBox.information(self, '提示', '加入成功')
        self.successed.emit(self.customer)

    def finish_group(self, group: wg.Group):
        print("finish group")
        asyncio.run(services.finish_group_with_param(group.g_id))
        QMessageBox.information(self, '提示', '团购已完成')
        self.successed.emit(self.customer)
