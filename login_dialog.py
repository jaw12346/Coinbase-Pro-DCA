# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_login_dialog(object):
    def setupUi(self, login_dialog):
        login_dialog.setObjectName("login_dialog")
        login_dialog.resize(240, 130)
        self.formLayoutWidget = QtWidgets.QWidget(login_dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 50, 221, 21))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.password_layout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.password_layout.setContentsMargins(0, 0, 0, 0)
        self.password_layout.setObjectName("password_layout")
        self.password_label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")
        self.password_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.password_label)
        self.password_input = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.password_input.setObjectName("password_input")
        self.password_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.password_input)
        self.verticalLayoutWidget = QtWidgets.QWidget(login_dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 241, 41))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.title_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setObjectName("title_layout")
        self.title_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.title_label.setFont(font)
        self.title_label.setObjectName("title_label")
        self.title_layout.addWidget(self.title_label, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayoutWidget = QtWidgets.QWidget(login_dialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(20, 90, 201, 21))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.buttons_layout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.setObjectName("buttons_layout")
        self.existing_account_button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.existing_account_button.setAutoDefault(False)
        self.existing_account_button.setObjectName("existing_account_button")
        self.buttons_layout.addWidget(self.existing_account_button)
        self.new_account_button = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.new_account_button.setAutoDefault(False)
        self.new_account_button.setDefault(True)
        self.new_account_button.setObjectName("new_account_button")
        self.buttons_layout.addWidget(self.new_account_button)

        self.retranslateUi(login_dialog)
        QtCore.QMetaObject.connectSlotsByName(login_dialog)

    def retranslateUi(self, login_dialog):
        _translate = QtCore.QCoreApplication.translate
        login_dialog.setWindowTitle(_translate("login_dialog", "Settings Login"))
        self.password_label.setText(_translate("login_dialog", "Password"))
        self.password_input.setPlaceholderText(_translate("login_dialog", "Enter a new or existing password"))
        self.title_label.setText(_translate("login_dialog", "DCA Settings Login"))
        self.existing_account_button.setText(_translate("login_dialog", "Existing Account"))
        self.new_account_button.setText(_translate("login_dialog", "New Account"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    login_dialog = QtWidgets.QDialog()
    ui = Ui_login_dialog()
    ui.setupUi(login_dialog)
    login_dialog.show()
    sys.exit(app.exec_())

