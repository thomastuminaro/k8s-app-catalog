from PySide6 import QtWidgets, QtCore

from kube import Pod, list_all_namespace_pods, list_all_namespaces

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("K8s applications GUI")
        self.setup_ui()
        self.set_default_values()
        self.setup_connections()

    def setup_ui(self):
        self.layout = QtWidgets.QVBoxLayout(self) # type: ignore
        self.lw_podList = QtWidgets.QListWidget()
        self.cbb_namespaces = QtWidgets.QComboBox()

        self.layout.addWidget(self.lw_podList) # type: ignore
        self.layout.addWidget(self.cbb_namespaces) # type: ignore
    
    def set_default_values(self):
        self.cbb_namespaces.addItems(list_all_namespaces())
        self.lw_podList.addItems(list_all_namespace_pods("default"))

    def setup_connections(self):
        #print(self.cbb_namespaces.currentText())
        #namespace = self.cbb_namespaces.currentText()
        self.cbb_namespaces.activated.connect(self.list_pods)

    def list_pods(self):
        namespace = self.cbb_namespaces.currentText()
        self.lw_podList.clear()
        pods = list_all_namespace_pods(namespace=namespace)
        self.lw_podList.addItems(pods)

if __name__ == "__main__":
    app = QtWidgets.QApplication([]) 
    win = App() 
    win.show() 
    app.exec() 