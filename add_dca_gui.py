# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'add_dca.ui'
#
# Created by: PyQt5 UI code generator 5.9.2

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_add_dca_dialog(QtWidgets.QDialog):
    def setupUi(self, add_dca_dialog, parent=None):
        self.parent = parent  # Parent of dialog = list dialog

        add_dca_dialog.setObjectName("add_dca_dialog")
        add_dca_dialog.resize(325, 155)
        self.formLayoutWidget = QtWidgets.QWidget(add_dca_dialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 20, 301, 124))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.add_dca_layout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.add_dca_layout.setContentsMargins(0, 0, 0, 0)
        self.add_dca_layout.setObjectName("add_dca_layout")
        self.base_currency_label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.base_currency_label.setFont(font)
        self.base_currency_label.setObjectName("base_currency_label")
        self.add_dca_layout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.base_currency_label)
        self.base_currency_input = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.base_currency_input.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.base_currency_input.setFont(font)
        self.base_currency_input.setInputMethodHints(QtCore.Qt.ImhNone)
        self.base_currency_input.setMaxLength(4)
        self.base_currency_input.setAlignment(QtCore.Qt.AlignCenter)
        self.base_currency_input.setObjectName("base_currency_input")
        self.add_dca_layout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.base_currency_input)
        self.quote_currency_label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.quote_currency_label.setFont(font)
        self.quote_currency_label.setObjectName("quote_currency_label")
        self.add_dca_layout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.quote_currency_label)
        self.quote_currency_input = QtWidgets.QLineEdit(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.quote_currency_input.setFont(font)
        self.quote_currency_input.setText("")
        self.quote_currency_input.setMaxLength(4)
        self.quote_currency_input.setAlignment(QtCore.Qt.AlignCenter)
        self.quote_currency_input.setObjectName("quote_currency_input")
        self.add_dca_layout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.quote_currency_input)

        self.quote_amount_label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.quote_amount_label.setFont(font)
        self.quote_amount_label.setObjectName("quote_amount_label")
        self.add_dca_layout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.quote_amount_label)

        self.quote_amount_input = QtWidgets.QSpinBox(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.quote_amount_input.setFont(font)
        self.quote_amount_input.setInputMethodHints(QtCore.Qt.ImhFormattedNumbersOnly | QtCore.Qt.ImhNoPredictiveText)
        self.quote_amount_input.setAlignment(QtCore.Qt.AlignCenter)
        self.quote_amount_input.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.quote_amount_input.setCorrectionMode(QtWidgets.QAbstractSpinBox.CorrectToNearestValue)
        self.quote_amount_input.setMinimum(5)
        self.quote_amount_input.setMaximum(100000000)
        self.quote_amount_input.setSingleStep(1)
        self.quote_amount_input.setStepType(QtWidgets.QAbstractSpinBox.DefaultStepType)
        self.quote_amount_input.setProperty("value", 5)
        self.quote_amount_input.setObjectName("quote_amount_input")
        self.add_dca_layout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.quote_amount_input)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.close_add_button = QtWidgets.QPushButton(self.formLayoutWidget)
        self.close_add_button.setDefault(False)
        self.close_add_button.setObjectName("close_add_button")
        self.horizontalLayout.addWidget(self.close_add_button)

        self.close_add_button.clicked.connect(add_dca_dialog.close)  # Close new dca window without saving

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.confirm_add_button = QtWidgets.QPushButton(self.formLayoutWidget)
        self.confirm_add_button.setDefault(True)
        self.confirm_add_button.setObjectName("confirm_add_button")
        self.horizontalLayout.addWidget(self.confirm_add_button)

        self.confirm_add_button.clicked.connect(lambda: self.confirm_clicked(
            base_currency=str(self.base_currency_input.text()).upper(),
            quote_currency=str(self.quote_currency_input.text()).upper(),
            amount=int(self.quote_amount_input.value())
        ))

        self.add_dca_layout.setLayout(6, QtWidgets.QFormLayout.SpanningRole, self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.add_dca_layout.setItem(4, QtWidgets.QFormLayout.LabelRole, spacerItem1)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.add_dca_layout.setItem(5, QtWidgets.QFormLayout.LabelRole, spacerItem2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.add_dca_layout.setItem(3, QtWidgets.QFormLayout.LabelRole, spacerItem3)

        self.retranslateUi(add_dca_dialog)
        QtCore.QMetaObject.connectSlotsByName(add_dca_dialog)

    def retranslateUi(self, add_dca_dialog):
        _translate = QtCore.QCoreApplication.translate
        add_dca_dialog.setWindowTitle(_translate("add_dca_dialog", "DCA Item Editor"))
        self.base_currency_label.setText(_translate("add_dca_dialog", "Base Currency (Crypto):"))
        self.base_currency_input.setPlaceholderText(_translate("add_dca_dialog", "BTC/ETH/ADA/etc."))
        self.quote_currency_label.setText(_translate("add_dca_dialog", "Quote Currency (Fiat):"))
        self.quote_currency_input.setPlaceholderText(_translate("add_dca_dialog", "USD/EUR/GBP/etc."))
        self.quote_amount_label.setText(_translate("add_dca_dialog", "Quote Currency Invested:"))
        self.quote_amount_input.setSuffix(_translate("add_dca_dialog", ".00"))
        self.quote_amount_input.setPrefix(_translate("add_dca_dialog", "$"))
        self.close_add_button.setText(_translate("add_dca_dialog", "Close"))
        self.confirm_add_button.setText(_translate("add_dca_dialog", "Add DCA Purchase"))

    def confirm_clicked(self, base_currency, quote_currency, amount):
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.amount = amount
        self.parent.add_new_dca(base_currency, quote_currency, amount)
