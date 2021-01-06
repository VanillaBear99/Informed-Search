import sys
import os
import math
import gridworld
import ai
import a_star
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *

rows = 120
cols = 160
w_highway = 3
w_path = 2

class AppWindow(QMainWindow):
    __grid = None 
    __gridView = None
    __dialog = None
    __filemenu = None
    __menu = None
    __ai = None
    __settings_w = None
    __settings_s = None
    __family = None
    __heuristic = None
    __w_w1 = None
    __w_w2 = None

    def __init__(self, parent = None):
        super().__init__(parent)
       
        central = QWidget()
        toolbar = self.buildGridToolbar()
        ai = self.buildAISettings()
        menu = self.buildMenubar()
        grid = QGridScene() 
        gridView = QGridView(grid)

        ai.setEnabled(False)

        c_layout = QHBoxLayout()
        c_layout.addWidget(ai)
        c_layout.addWidget(gridView)
        central.setLayout(c_layout)

        self.setMenuBar(menu) 
        self.addToolBar(toolbar) 
        self.setCentralWidget(central)         
        self.setWindowTitle("Gridworld (Informed Search)") 

        dialog = QFileDialog(self) 
        dialog.setViewMode(QFileDialog.List)
        dialog.setNameFilter("Gridworld (*.gw)")
        dialog.setDefaultSuffix("gw")

        self.__grid = grid
        self.__gridView = gridView
        self.__dialog = dialog
        self.__menu = menu
        self.__ai = ai

    def buildAISettings(self):
        ret = QWidget()
        layout = QVBoxLayout()
        v_w = QDoubleValidator() 

        family = QGroupBox("A* Algorithm") 
        f_layout = QVBoxLayout()
        f_group = QButtonGroup()

        rbtn_uc = QRadioButton("Uniform-Cost")
        rbtn_w = QRadioButton("Weighted")
        rbtn_s = QRadioButton("Sequential-Heuristic")

        f_group.addButton(rbtn_uc, 0)
        f_group.addButton(rbtn_w, 1)
        f_group.addButton(rbtn_s, 2)

        f_layout.addWidget(rbtn_uc)
        f_layout.addWidget(rbtn_w)
        f_layout.addWidget(rbtn_s)
      
        f_group.button(1).setChecked(True)

        family.setLayout(f_layout)

        v_w.setBottom(1.0)
        v_w.setDecimals(4)

        s_weighted = QGroupBox("Weighted A* Settings")
        sw_layout = QFormLayout()

        cbo_h = QComboBox()
        cbo_h.addItems([
            "Pythagorean",
            "Manhattan",
            "Manhattan (Hex)",
            "Axial",
            "Start Delta", 
        ])

        le_w = QLineEdit("1")
        le_w.setValidator(v_w)

        sw_layout.addRow("Heuristic function:", cbo_h)
        sw_layout.addRow("Weight:", le_w)

        s_weighted.setLayout(sw_layout)

        s_seq = QGroupBox("Sequential-Heuristic A* Settings") 
        ss_layout = QFormLayout()

        le_w1 = QLineEdit("1.25")
        le_w2 = QLineEdit("2")

        le_w1.setValidator(v_w)
        le_w2.setValidator(v_w)

        ss_layout.addRow("Overall weight:", le_w1)
        ss_layout.addRow("Non-anchor weight:", le_w2)

        s_seq.setLayout(ss_layout)

        s_weighted.setVisible(True)
        s_seq.setVisible(False)

        btn_runAI = QPushButton("Run AI")

        family.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        s_weighted.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        s_seq.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(family)
        layout.addWidget(s_weighted)
        layout.addWidget(s_seq)
        layout.addStretch(1) 
        layout.addWidget(btn_runAI)
        
        layout.setAlignment(Qt.AlignTop)

        ret.setLayout(layout)

        f_group.idToggled.connect(self.selectAStar)
        btn_runAI.clicked[bool].connect(self.runAI)
      
        self.__settings_w = s_weighted
        self.__settings_s = s_seq

        self.__family = f_group
        self.__heuristic = cbo_h 
        self.__w = le_w
        self.__w1 = le_w1
        self.__w2 = le_w2

        ret.setFixedWidth(250)     

        return ret

    def buildGridToolbar(self):
        ret = QToolBar("Grid View", self)
    
        a_zoomin = QAction(QIcon.fromTheme("zoom-in", QIcon("zoom-in.svg")), "Zoom +", self)
        a_zoomout = QAction(QIcon.fromTheme("zoom-out", QIcon("zoom-out.svg")), "Zoom -", self)
        a_resetzoom = QAction(QIcon.fromTheme("zoom-original", QIcon("zoom-original.svg")), "Reset Zoom", self)  

        a_zoomin.setShortcut("Ctrl+=")
        a_zoomout.setShortcut("Ctrl+-")
        a_resetzoom.setShortcut("Ctrl+0")

        ret.addAction(a_zoomin) 
        ret.addAction(a_zoomout)
        ret.addAction(a_resetzoom)
        
        ret.actionTriggered[QAction].connect(self.zoom)

        return ret

    def buildMenubar(self):
        ret = QMenuBar()
    
        mFile = ret.addMenu("File")
        a_new = mFile.addAction("New")
        a_open = mFile.addAction("Open")
        a_save = mFile.addAction("Save")
        mFile.addSeparator()
        a_quit = mFile.addAction("Quit")
       
        a_new.setShortcut("Ctrl+N")
        a_open.setShortcut("Ctrl+O")
        a_save.setShortcut("Ctrl+S")
        a_quit.setShortcut("Ctrl+Q")

        a_save.setEnabled(False)

        ret.triggered[QAction].connect(self.doFileAction)

        self.__filemenu = mFile

        return ret

    def selectAStar(self, i, check):
        if check:
            self.__settings_w.setVisible(i == 1)
            self.__settings_s.setVisible(i == 2)

    def runAI(self, event):
        map = gridworld.terrain
        start = gridworld.start
        goal = gridworld.goal

        grid = self.__grid
        algo = self.__family.checkedId()
                
        if algo == 0: # Uniform-Cost
            info = a_star.uniform(map, start, goal)
        elif algo == 1: # Weighted
            w = float(self.__w.text())
            h = self.__heuristic.currentText()
    
            if h == "Manhattan":
                h = ai.h_manhattan
            elif h == "Manhattan (Hex)":
                h = ai.h_manhattan_hex
            elif h == "Axial":
                h = ai.h_axis_dist
            elif h == "Start Delta":
                h = ai.h_delta
            else:
                h = ai.h_pythagorean

            info = a_star.weighted(map, start, goal, w, h)

        elif algo == 2: # Sequential
            w1 = float(self.__w1.text())
            w2 = float(self.__w2.text())

            info = a_star.sequential(map, start, goal, w1, w2)

        if info:
            grid.displayPathfinding(info)

    def zoom(self, event):
        view = self.__gridView
        t = event.text()
        if t == "Zoom +":
            view.zoom(1.1)
        elif t == "Zoom -":
            view.zoom(0.9)
        else:
            view.resetZoom()

    def doFileAction(self, event): 
        t = event.text() 
        dialog = self.__dialog
        grid = self.__grid
        ai = self.__ai

        if t == "New":
            gridworld.initGridworld()
            grid.updateScene()
        elif t == "Save":
            dialog.setFileMode(QFileDialog.AnyFile)
            dialog.setAcceptMode(QFileDialog.AcceptSave)
            if dialog.exec():
                gridworld.writeGridworld(dialog.selectedFiles()[0])
        elif t == "Open":
            dialog.setFileMode(QFileDialog.ExistingFile)
            dialog.setAcceptMode(QFileDialog.AcceptOpen)
            if dialog.exec():
                gridworld.loadGridworld(dialog.selectedFiles()[0])
                grid.updateScene()
        else:
            QApplication.quit()

        ai.setEnabled(True)

        next(a for a in self.__filemenu.actions() if a.text() == "Save").setEnabled(True)

class QGridScene(QGraphicsScene):
    __WIDTH = 7 
    __HEIGHT = 7
    __cells = None
    __highways = None 
    __start = None
    __goal = None
    __path = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cells = QGraphicsItemGroup()
        highways = QGraphicsItemGroup() 
        points = QGraphicsItemGroup()
        grid = QGraphicsItemGroup()
        path = QGraphicsItemGroup()

        width = cols * self.__WIDTH
        height = rows * self.__HEIGHT
       
        cells.setZValue(0) 
        grid.setZValue(1)
        highways.setZValue(2)
        points.setZValue(3)
        path.setZValue(4)

        self.addItem(cells) 
        self.addItem(grid)
        self.addItem(highways) 
        self.addItem(points)
        self.addItem(path)

        self.setSceneRect(0, 0, width, height)
        self.setItemIndexMethod(QGraphicsScene.NoIndex)

        self.__start = QGraphicsRectItem(0, 0, self.__WIDTH, self.__HEIGHT)
        self.__goal = QGraphicsRectItem(0, 0, self.__WIDTH, self.__HEIGHT)  

        p_start = QPen(Qt.green)
        p_end = QPen(Qt.red)
        p_start.setWidth(2)
        p_end.setWidth(2)
        self.__start.setPen(p_start)
        self.__start.setBrush(QBrush(Qt.NoBrush))
        self.__goal.setPen(p_end)
        self.__goal.setBrush(QBrush(Qt.NoBrush))

        self.__start.setVisible(False)
        self.__goal.setVisible(False)

        points.addToGroup(self.__start)
        points.addToGroup(self.__goal)

        trans = QColor(0, 0, 0, 1)

        for i in range(rows):
            for j in range(cols):
                cells.addToGroup(QGraphicsRectItem(j * self.__WIDTH, i * self.__HEIGHT, self.__WIDTH, self.__HEIGHT))

        for x in range(0, cols + 1):
            xc = x * self.__WIDTH
            line = QGraphicsLineItem(xc, 0, xc, height)
            line.setPen(QPen(trans))

            grid.addToGroup(line)

        for y in range(0, rows + 1):
            yc = y * self.__HEIGHT
            line = QGraphicsLineItem(0, yc, width, yc) 
            line.setPen(QPen(trans))
            
            grid.addToGroup(line)

        self.__cells = cells
        self.__highways = highways
        self.__path = path

    def updateScene(self):
        self.__start.setPos((gridworld.start[0] - 1) * self.__WIDTH, (gridworld.start[1] - 1) * self.__HEIGHT)
        self.__goal.setPos((gridworld.goal[0] - 1) * self.__WIDTH, (gridworld.goal[1] - 1) * self.__HEIGHT)

        self.__start.setVisible(True)
        self.__goal.setVisible(True)
        
        for c in self.__path.childItems():
            self.removeItem(c)

        for c in self.__highways.childItems():
            self.removeItem(c)

        if gridworld.terrain: 
            cells = self.__cells.childItems() 
            for y in range(rows):
                for x in range(cols):
                    v = gridworld.terrain[y + 1][x + 1] 
                    b = QBrush(Qt.NoBrush)

                    if v.isHardToTraverse():
                        b.setColor(Qt.darkGreen)
                        b.setStyle(Qt.DiagCrossPattern)
                    elif v.isBlocked():
                        b.setColor(Qt.gray)
                        b.setStyle(Qt.SolidPattern)
            
                    cells[y * cols + x].setBrush(b)
                    cells[y * cols + x].setToolTip(f"({x}, {y})")

                    if v.isHighway():
                        v_n = gridworld.terrain[y][x + 1]
                        v_s = gridworld.terrain[y + 2][x + 1]
                        v_w = gridworld.terrain[y + 1][x]
                        v_e = gridworld.terrain[y + 1][x + 2]

                        p_hw = QPen(Qt.blue)
                        p_hw.setWidth(w_highway)

                        xc = x * self.__WIDTH + 0.5 * self.__WIDTH
                        yc = y * self.__HEIGHT + 0.5 * self.__HEIGHT
                        
                        if v_n.isHighway():
                            h = QGraphicsLineItem(xc, yc, xc, yc - 0.5 * self.__HEIGHT)
                            h.setPen(p_hw)
                            self.__highways.addToGroup(h)

                        if v_s.isHighway():
                            h = QGraphicsLineItem(xc, yc, xc, yc + 0.5 * self.__HEIGHT)
                            h.setPen(p_hw)
                            self.__highways.addToGroup(h)

                        if v_w.isHighway():
                            h = QGraphicsLineItem(xc, yc, xc - 0.5 * self.__WIDTH, yc)
                            h.setPen(p_hw)
                            self.__highways.addToGroup(h)

                        if v_e.isHighway():
                            h = QGraphicsLineItem(xc, yc, xc + 0.5 * self.__WIDTH, yc)
                            h.setPen(p_hw)
                            self.__highways.addToGroup(h)
 
    def displayPathfinding(self, info):
        path = self.__path  
        cells = self.__cells.childItems() 
        parent = None

        map = info['map']
        f = info['f']
        g = info['g']
        h = info['h']

        for c in path.childItems():
            self.removeItem(c)

        for v in map:
            xc = (v[0] - 1) * self.__WIDTH + 0.5 * self.__WIDTH
            yc = (v[1] - 1) * self.__HEIGHT + 0.5 * self.__HEIGHT 

            if parent != None:
                pxc = (parent[0] - 1) * self.__WIDTH + 0.5 * self.__WIDTH
                pyc = (parent[1] - 1) * self.__HEIGHT + 0.5 * self.__HEIGHT 
                line = QGraphicsLineItem(xc, yc, pxc, pyc)
                pen = QPen(Qt.red)
                pen.setWidth(w_path)
                line.setPen(pen)
                path.addToGroup(line)

            parent = v

        for y in range(rows):
            for x in range(cols):
                v_f = f[y + 1][x + 1]
                v_g = g[y + 1][x + 1]
                v_h = h[y + 1][x + 1]

                tt = f"({x}, {y})" + os.linesep
                tt += f"f: {v_f}" + os.linesep
                tt += f"g: {v_g}" + os.linesep
                tt += f"h: {v_h}" + os.linesep

                cells[y * cols + x].setToolTip(tt)

class QGridView(QGraphicsView):
    __zoom = 1
    def __init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.view_menu = QMenu(self)

    def zoom(self, v):
        self.__zoom *= v
        self.scale(v, v)

    def resetZoom(self):
        v = 1 / self.__zoom
        self.scale(v, v)
        self.__zoom = 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show() 
    sys.exit(app.exec_())
