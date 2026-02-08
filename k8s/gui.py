from PySide6 import QtWidgets, QtCore

from kube import Pod, list_all_namespace_pods, list_all_namespaces

class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K8s applications GUI")
        self.setup_ui()
        self.set_default_values()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self) # type: ignore

        while self.layout.count():
            item = self.layout.takeAt(0)

            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.lw_podList = QtWidgets.QListWidget()
        self.cbb_namespaces = QtWidgets.QComboBox()
        self.cbb_actions = QtWidgets.QComboBox()

        self.layout.addWidget(QtWidgets.QLabel("Pod list"))
        self.layout.addWidget(self.lw_podList) # type: ignore

        self.layout.addWidget(QtWidgets.QLabel("Namespace selection"))
        self.layout.addWidget(self.cbb_namespaces) # type: ignore

        self.layout.addWidget(QtWidgets.QLabel("Pod actions"))
        self.layout.addWidget(self.cbb_actions) # type: ignore
    
    def set_default_values(self):
        self.cbb_actions.addItems(["", "Create pod", "Delete pod(s)"])
        self.cbb_namespaces.addItems(list_all_namespaces())
        self.lw_podList.addItems(list_all_namespace_pods("default"))

    def setup_connections(self):
        self.cbb_namespaces.activated.connect(self.list_pods)
        #self.cbb_actions.activated.connect(self.perform_action)
        self.cbb_actions.currentIndexChanged.connect(self.perform_action)
        self._previous_index = -1
    
    def perform_action(self):
        #self.setup_ui()
        if self.cbb_actions.currentText() == "Create pod":
            self.ui_create_pod()
        elif self.cbb_actions.currentText() == "Delete pod(s)":
            self.ui_delete_pod()

    def ui_create_pod(self):
        self.le_podname = QtWidgets.QLineEdit()
        self.layout.addWidget(QtWidgets.QLabel("New pod name"))
        self.layout.addWidget(self.le_podname)

        self.le_ns = QtWidgets.QLineEdit()
        self.layout.addWidget(QtWidgets.QLabel("Namespace"))
        self.layout.addWidget(self.le_ns)

        self.le_img = QtWidgets.QLineEdit()
        self.layout.addWidget(QtWidgets.QLabel("Image name"))
        self.layout.addWidget(self.le_img)

        self.btn_create = QtWidgets.QPushButton("Create new pod")
        self.layout.addWidget(self.btn_create)

        self.btn_create.pressed.connect(self.create_pod)
    
    def ui_delete_pod(self):
        self.btn_delete = QtWidgets.QPushButton("Delete selected pods")
        self.layout.addWidget(self.btn_delete)

        self.btn_create.pressed.connect(self.delete_pod)

    def delete_pod(self):
        to_delete = self.lw_podList.selectedItems()
        ns = self.cbb_namespaces.currentText()
        result = True
        
        for podname in to_delete:
            pod = Pod(name=podname.text(), namespace=ns)
            if pod.delete():
                result = False
        
        if result:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Pod deletion result")
            dlg.setText("You successfully deleted the pod(s).")
            dlg.exec()
        else:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Pod deletion result")
            dlg.setText("There was an issue deleting the pod(s).")
            dlg.exec()


    def create_pod(self):
        pod = Pod(name=self.le_podname.text(), namespace=self.le_ns.text())
        if (pod.create(cont_image=self.le_img.text())):
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Pod creation result")
            dlg.setText("You successfully created the pod.")
            dlg.exec()
        else:
            dlg = QtWidgets.QMessageBox(self)
            dlg.setWindowTitle("Pod creation result")
            dlg.setText("There was an issue creating the pod.")
            dlg.exec()
        self.setup_ui()

    def list_pods(self):
        namespace = self.cbb_namespaces.currentText()
        self.lw_podList.clear()
        pods = list_all_namespace_pods(namespace=namespace)
        self.lw_podList.addItems(pods)

class resultMessage(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        resultMessage = "You have successfully created the pod."

        layout = QtWidgets.QHBoxLayout()
        self.lbl_msg = QtWidgets.QLabel(resultMessage)
        self.layout.addWidget(self.lbl_msg)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QtWidgets.QApplication([]) 
    win = mainWindow() 
    win.show() 
    app.exec() 