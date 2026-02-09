from PySide6 import QtWidgets, QtCore
import time
from kube import Pod, list_all_namespace_pods, list_all_namespaces


class mainWindow(QtWidgets.QWidget):
    def __init__(self):
        """
        Initialiazes the main window UI
        Calls for setup UI which creates main UI components
        Sets defaults
        Create connections
        """
        super().__init__()
        self.setWindowTitle("K8s applications GUI")
        self.setup_ui()
        self.set_default_values()
        self.setup_connections()

    def setup_ui(self):
        """
        Creates a main layout in vertical mode
        Creates two drop down lists and a text list object, adds them to UI
        Creates also creates another widget which will be a vertical layout
            => this one will contain the other widgets which are dynamically displayed
        """
        self.layout = QtWidgets.QVBoxLayout(self) # type: ignore
        self.lw_podList = QtWidgets.QListWidget()
        self.cbb_namespaces = QtWidgets.QComboBox()
        self.cbb_actions = QtWidgets.QComboBox()

        self.layout.addWidget(QtWidgets.QLabel("Pod list")) # type: ignore
        self.layout.addWidget(self.lw_podList) # type: ignore

        self.layout.addWidget(QtWidgets.QLabel("Namespace selection")) # type: ignore
        self.layout.addWidget(self.cbb_namespaces) # type: ignore

        self.layout.addWidget(QtWidgets.QLabel("Pod actions")) # type: ignore
        self.layout.addWidget(self.cbb_actions) # type: ignore

        self.action_widget = QtWidgets.QWidget()
        self.action_layout = QtWidgets.QVBoxLayout(self.action_widget)
        self.layout.addWidget(self.action_widget) # type: ignore

    def clear_action_ui(self):
        """
        Helps to delete the contextual widgets created when deleting/creating pods
        Iterates through the action widget (which represents a layout of multiple widgets)
        Deletes the first one 
        takeAt returns a layout object item, needs to mark it for clean deletion after 
        """
        while self.action_layout.count():
            item = self.action_layout.takeAt(0)
            widget = item.widget() # type: ignore
            if widget:
                widget.deleteLater()
    
    def set_default_values(self):
        """
        Adds possible actions for the pods 
        Sets the default entry of the namespace list to the default one 
        List by default pods from default namespace
        """
        self.cbb_actions.addItems(["Choose action...", "Create pod", "Delete pod(s)"])

        self.cbb_namespaces.addItems(list_all_namespaces())
        for i in range(self.cbb_namespaces.count()):
            if self.cbb_namespaces.itemText(i) == "default":
                self.cbb_namespaces.setCurrentIndex(i)

        self.lw_podList.addItems(list_all_namespace_pods("default"))

    def setup_connections(self):
        """
        When changing namespace will list the pods 
        When selecting what to do, will call the main function for this 
        """
        self.cbb_namespaces.activated.connect(self.list_pods)
        self.cbb_actions.activated.connect(self.perform_action)
    
    def perform_action(self):
        """
        First clears the UI if there was a previous action being done 
        Then calls functions to set up UI depending on what was selected
        """
        self.clear_action_ui()

        if self.cbb_actions.currentText() == "Create pod":
            self.ui_create_pod()
        elif self.cbb_actions.currentText() == "Delete pod(s)":
            self.ui_delete_pod()

    def ui_create_pod(self): 
        """
        Adds the required widgets and creates connection for the button to create
        """
        self.le_podname = QtWidgets.QLineEdit()
        self.action_layout.addWidget(QtWidgets.QLabel("New pod name"))
        self.action_layout.addWidget(self.le_podname)

        self.le_img = QtWidgets.QLineEdit()
        self.action_layout.addWidget(QtWidgets.QLabel("Image name"))
        self.action_layout.addWidget(self.le_img)

        self.btn_create = QtWidgets.QPushButton("Create new pod")
        self.action_layout.addWidget(self.btn_create)

        self.btn_create.pressed.connect(self.create_pod)
    
    def ui_delete_pod(self):
        """
        Adds the required widgets and creates connection for the button to delete
        """
        self.btn_delete = QtWidgets.QPushButton("Delete selected pods")
        self.action_layout.addWidget(self.btn_delete)

        self.btn_delete.pressed.connect(self.delete_pod)

    def delete_pod(self):
        """
        Grabs all selected items for deletion
        Iterates through them and display message box to confirm if pod was deleted
        Resets the action option to nothing
        Waits 1 sec before refreshing list as pod can take a second to delete
        Refresh the lists 
        Clears the delete widgets from main window
        """
        to_delete = self.lw_podList.selectedItems()
        ns = self.cbb_namespaces.currentText()
        result = True
        
        for podname in to_delete:
            pod = Pod(name=podname.text(), namespace=ns)
            if not pod.delete_resource():
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
        
        self.clear_action_ui()
        self.cbb_actions.setCurrentIndex(0)
        time.sleep(1)
        self.list_pods()

    def create_pod(self):
        """
        Creates a pod object based on widget current settings
        Displays message box depending on result 
        Clears creation UI widgets 
        Sets actions widget to default and list pods again
        """
        pod = Pod(name=self.le_podname.text(), namespace=self.cbb_namespaces.currentText())
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
        self.clear_action_ui()
        self.cbb_actions.setCurrentIndex(0)
        self.list_pods()

    def list_pods(self):
        """
        Clears all pods showing
        Get the name of the namespace selected
        Fills the list again with pods from the namespace
        """
        namespace = self.cbb_namespaces.currentText()
        self.lw_podList.clear()
        pods = list_all_namespace_pods(namespace=namespace)
        self.lw_podList.addItems(pods)

if __name__ == "__main__":
    app = QtWidgets.QApplication([]) 
    win = mainWindow() 
    win.show() 
    app.exec() 