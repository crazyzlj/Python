from qgis.core import QgsApplication
from PyQt4.QtGui import QDialog

GUIEnabled=True
app = QgsApplication([], GUIEnabled)

dlg = QDialog()
dlg.exec_()

app.exit(app.exec_())