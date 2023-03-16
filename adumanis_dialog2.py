import sys
import time
import os
import processing
import webbrowser
import numpy as np

from qgis.PyQt import QtWidgets, QtGui
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QApplication, QFileDialog, QComboBox, QMessageBox
from PyQt5.QtCore import QThread
from qgis.core import (
    QgsProject, 
    QgsVectorLayer,
    QgsMessageLog,
    QgsProcessingFeedback,
    QgsProcessing,
    QgsCoordinateReferenceSystem,
    NULL
)
from processing.core.Processing import Processing
from .adumanis_dialog_ui import Ui_adumanisDialogBase as Ui_Dialog

class adumanisDialog2(QDialog):
	def __init__(self):
		super().__init__()
		n = 100
		Processing.initialize()
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		self.ui.mMapLayerComboBox.layerChanged.connect(self.layer_changed)
		self.ui.mMapLayerComboBox.setCurrentIndex(-1)
		self.ui.mFieldComboBox.fieldChanged.connect(self.field_changed)
		self.ui.progressBar.setMinimum(0)
		self.ui.progressBar.setMaximum(n)

		#MEMBUAT DESKRIPSI PLUGIN
		self.ui.textBrowser_2.setFixedWidth(300)
		self.ui.textBrowser_2.setText("<b>ADUMANIS</b>"+
			"<p><br>Plugin Adumanis adalah tools untuk memanipulasi layer</p>")
		self.ui.textBrowser_2.setFont(QtGui.QFont("monospace", 11))

		self.ui.pushButton.setEnabled(False)
		self.ui.buttonBox.accepted.connect(self.upload)
		self.ui.buttonBox.accepted.connect(self.bar)
		self.ui.buttonBox.rejected.connect(self.reject)
		self.ui.buttonBox.helpRequested.connect(self.bantuan)
		
		self.show()


	#MEMANGGIL ATRIBUT DARI LAYER YANG DIPILIH
	def layer_changed(self, layer):
		self.ui.mFieldComboBox.setLayer(layer)

	#MENAMPILKAN HALAMAN BANTUAN
	def bantuan(self):
		webbrowser.open('https://docs.qgis.org/3.22/en/docs/index.html')
		
	#MEMANGGIL NILAI DARI ATRIBUT YANG DIPILIH
	def field_changed(self, field):
		# Memanggil layer yang sedang aktif saat ini
	    layer = self.ui.mMapLayerComboBox.currentLayer()
	    # get index of the field
	    i = layer.fields().indexFromName(field)
	    # get unique values
	    unique_values = layer.uniqueValues(i)
	    combovalues = []
	    for value in unique_values:
	    	if value == NULL:
	    		combovalues.append('')
	    	else:
	    		combovalues.append(str(value)) 
	    # remove all values from comboBoxAttribute
	    self.ui.mComboBox.clear()    
	    # add unique values
	    self.ui.mComboBox.addItems(combovalues)

	#MENAMPILKAN PROGRESS BAR
	def bar(self):
		for i in range(100):
			time.sleep(0.01)
			self.ui.progressBar.setValue(i+1)
			self.ui.pushButton.setEnabled(True)
			self.ui.pushButton.clicked.connect(self.cancelProses)
		self.ui.pushButton.setEnabled(False)
		self.ui.progressBar.setValue(0)


	#MEMBATALKAN PROGRESS BAR
	def cancelProses(self):
		self.ui.progressBar.reset()

	#MENAMBAHKAH LAYER TEMPORARY
	def upload(self):
		nama_layer_valid = str(self.ui.lineEdit1.text())
		nama_layer_invalid = str(self.ui.lineEdit2.text())
		nama_layer_error = str(self.ui.lineEdit3.text())
		tolerance = self.ui.doubleSpinBox.value()

		layer_input = self.ui.mMapLayerComboBox.currentLayer()
		selecting_feats_iterator = layer_input.getFeatures()
		sel_feats = []
		for s_feat in selecting_feats_iterator:
			sel_feats.append(s_feat) 

		input_crs_object = layer_input.crs()
		input_crs = input_crs_object.authid()
		input_input_crs = "Polygon?crs=%s" % input_crs

		layer_output = QgsVectorLayer(input_input_crs, nama_layer_valid, "memory")
		layer_output_pr = layer_output.dataProvider()
		layer_output_pr.addFeatures(sel_feats)

		QgsProject.instance().addMapLayer(layer_output)

		#MENAMPILKAN LOG
		params = {
		'INPUT' : layer_output,
		'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
		'OUTPUT' : QgsProcessing.TEMPORARY_OUTPUT
		}
		feedback = QgsProcessingFeedback()
		res = processing.run('native:reprojectlayer', params, feedback=feedback)
		res2 = res['OUTPUT']
		self.ui.textBrowser.setText(str(res2))

		#SOURCE CODE ADUMANIS
	
	def Euclidean(a, b):
	    Distance = np.linalg.norm(np.array(a) - np.array(b))
	    return Distance

	def deep_index1(lst, w):
	    for (i, sub) in enumerate(lst):
	        #print(i, sub[1])
	        for (j, subsub) in enumerate(sub[1]):
	            #print(j, subsub)
	            if w==subsub[0]:
	                return(sub[1])
	            
	def deep_index2(lst, w):
	    for (i, sub) in enumerate(lst):
	        #print(i, sub[1])
	        if w==sub[0]:
	            return(sub[0])

if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MyForm()
    w.show()
    sys.exit(app.exec_())

	# 	number = self.ui.lineEdit.text()
	# 	try:
	# 	    number = float(number)
	# 	except Exception:
	# 	    QMessageBox.about(self, 'Error','Nilai Toleransi harus berupa angka!')
	# 	    pass

	# 	return number
	

	# def test(self):
	# 	lyr = iface.activeLayer()
	# 	idx = lyr.dataProvider().fieldNameIndex(self.layer_changed ) 
	# 	uv = lyr.dataProvider().uniqueValues( idx )
	# 	cb = QComboBox()
	# 	cb.addItems( uv )


	# def browsefiles(self):
	# 	global fname
	# 	fname = QFileDialog.getOpenFileName(self, 'Open file', 'C:\\Users', 'SHP files (*.shp)')
	# 	self.ui.filename.setText(fname[0])

	# msg = QMessageBox()
	# msg.setWindowTitle('Bantuan Plugin Adumanis')
	# msg.setText("Bantuan")
	# msg.exec_()


		