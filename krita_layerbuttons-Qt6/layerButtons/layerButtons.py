# LayerButtons
# Copyright (C) 2023 Simolette

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from krita import *
from PyQt5.QtWidgets import QToolButton

background = "0000000"
activated = "0033BB"

application = Krita.instance()

class LayerButtons(krita.Extension):

    def __init__(self, parent):
        super(LayerButtons, self).__init__(parent)        
        
        self.kritaSoloAction = None     
        self.soloBtn = self.buildButton("isolate_active_layer","visible","Isolate Active Layer",True)
        self.mergeBtn = self.buildButton("merge_layer","merge-layer-below","Merge with Layer Below")
        appNotifier  = application.notifier()
        appNotifier.windowCreated.connect(self.addElement)           

    def setup(self):
        pass

    def createActions(self, window):
        pass

    def activateSoloing(self):
        if self.kritaSoloAction == None:
            self.kritaSoloAction = Application.action("isolate_active_layer")
            self.kritaSoloAction.changed.connect(self.ensure_button_toggled)        
            
    def ensure_button_enabled(self):
        selNodes = Krita.instance().activeWindow().activeView().selectedNodes()
        # Check if there even are any layers
        if not selNodes:
            return  # Exit early if no layers are selected
        # disable solo button if there are more than 1 layer selected
        if (len(selNodes) > 1):
            self.buttonToggle(self.soloBtn,False)
            self.buttonToggle(self.mergeBtn,True)
        else:
            self.buttonToggle(self.soloBtn,True) 
            # disable merge button when current layer or layer below is locked (only if not multiple selected)
            inx = selNodes[0].index()
            if(selNodes[0].locked() or (inx > 0 and selNodes[0].parentNode().childNodes()[inx-1].locked())):
                self.buttonToggle(self.mergeBtn,False)
            else:
                self.buttonToggle(self.mergeBtn,True)        
        
    def ensure_button_toggled(self):
        self.soloBtn.setStyleSheet(f"background-color: #{activated if self.kritaSoloAction.isChecked() else background}")
        self.soloBtn.setChecked(self.kritaSoloAction.isChecked())
                
    def buttonToggle(self,btn,enable=False):
        # grey out the button if disabled
        btn.setEnabled(enable)
        btn.setAutoRaise(enable)
        btn.setDown(not enable)
        
        
    def addElement(self):
        layerDocker = next((w for w in Krita.instance().dockers() if w.objectName() == 'KisLayerBox'), None)
        layout = layerDocker.findChild(QHBoxLayout,'hbox1')
        layerList = layerDocker.findChild(QWidget, "listLayers")
        layerList.selectionModel().selectionChanged.connect(self.ensure_button_enabled)        
        
        layout.insertWidget(4,self.soloBtn)
        layout.insertWidget(5,self.mergeBtn)
        self.soloBtn.clicked.connect(self.soloBtnClick)
        self.mergeBtn.clicked.connect(self.clickButton)
        
        
    def soloBtnClick(self):
        self.activateSoloing()
        self.clickButton()
        
    
    def clickButton(self):
        application.action(self.sender().action).trigger()    


    def buildButton(self,act,icn,tip,tog=False)->QToolButton:
        newButton = QToolButton()
        newButton.setFixedSize(32,32)
        newButton.setIconSize(QSize(22,22))
        newButton.setAutoRaise(True)
        newButton.setCheckable(tog)
        newButton.setIcon(Krita.instance().icon(icn))
        newButton.setToolTip(tip)
        newButton.action = act
        return newButton
        