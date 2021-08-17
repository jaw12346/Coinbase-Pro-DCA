# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edit_dca_list.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_purchase_list_widget(object):
    def setupUi(self, purchase_list_widget):
        purchase_list_widget.setObjectName("purchase_list_widget")
        purchase_list_widget.resize(320, 240)
        self.verticalLayoutWidget = QtWidgets.QWidget(purchase_list_widget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(230, 20, 77, 191))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.dca_edit_buttons_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.dca_edit_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.dca_edit_buttons_layout.setObjectName("dca_edit_buttons_layout")
        self.add_dca_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.add_dca_button.setDefault(False)
        self.add_dca_button.setObjectName("add_dca_button")
        self.dca_edit_buttons_layout.addWidget(self.add_dca_button)
        self.edit_dca_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.edit_dca_button.setObjectName("edit_dca_button")
        self.dca_edit_buttons_layout.addWidget(self.edit_dca_button)
        self.remove_dca_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.remove_dca_button.setObjectName("remove_dca_button")
        self.dca_edit_buttons_layout.addWidget(self.remove_dca_button)
        self.save_list_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.save_list_button.setFont(font)
        self.save_list_button.setDefault(True)
        self.save_list_button.setObjectName("save_list_button")
        self.dca_edit_buttons_layout.addWidget(self.save_list_button)
        self.dca_list = QtWidgets.QListView(purchase_list_widget)
        self.dca_list.setGeometry(QtCore.QRect(10, 20, 211, 192))
        self.dca_list.setObjectName("dca_list")

        self.retranslateUi(purchase_list_widget)
        self.remove_dca_button.clicked.connect(self.dca_list.clearSelection)
        QtCore.QMetaObject.connectSlotsByName(purchase_list_widget)

    def retranslateUi(self, purchase_list_widget):
        _translate = QtCore.QCoreApplication.translate
        purchase_list_widget.setWindowTitle(_translate("purchase_list_widget", "Edit DCA Purchase List"))
        self.add_dca_button.setText(_translate("purchase_list_widget", "Add"))
        self.edit_dca_button.setText(_translate("purchase_list_widget", "Edit"))
        self.remove_dca_button.setText(_translate("purchase_list_widget", "Remove"))
        self.save_list_button.setText(_translate("purchase_list_widget", "Save and Exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    purchase_list_widget = QtWidgets.QWidget()
    ui = Ui_purchase_list_widget()
    ui.setupUi(purchase_list_widget)
    purchase_list_widget.show()
    sys.exit(app.exec_())

