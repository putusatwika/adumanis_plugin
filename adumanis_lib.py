# //ADUMANIS LIBRARY
import math
import numpy as np
from qgis.core import QgsPointXY

class TiePoints:
    def __init__(self):
        self.nib = []        
        self.index = []
        self.control = []
        self.x = []
        self.y = []
    
    def destroy(self):
        self.nib.clear()
        self.index.clear()
        self.control.clear()
        self.x.clear()
        self.y.clear()
        
    def add(self, NIB, index, control, x, y):
        self.nib.append(NIB)
        self.index.append(index)
        self.control.append(control)
        self.x.append(x)
        self.y.append(y)
        
    def isContainControl(self):
        if True in self.control: return True 
        else: return False
    
    def isGrouped(self, nib, index):
        indices = [i for i, x in enumerate(self.nib) if x == nib]
        if (len (indices)>0):
            returnVal = False
            for k in range (len(indices)):
                if self.index[indices[k]] == index :
                    returnVal = True
            return returnVal
        else:
            return False
    
    def closestControl(self, x, y):
        point = [x,y]
        closest = -1
        closestControl = []
        for i in range (len(self.control)):
            if (self.control[i]):
                control = [self.x[i] , self.y[i]]
                temp = Euclidean(point, control)
                if (closest == -1 or closest > temp):
                    closest = temp
                    closestControl = control
        
        return closestControl
    
    def show(self):
        print ("NIB\t","index\t","control\t","x\t\t","y")
        for i in range (len(self.nib)):
            print (self.nib[i],end ="\t")
            print (self.index[i],end ="\t")
            print (self.control[i],end ="\t")
            print (self.x[i],end ="\t")
            print (self.y[i])
            
    def length(self):
        return len(self.nib)

class Points:
    ## # Struktur simpan points[x,y,idx, controlStatus]
    ## # 0 : x, 1: y, 2: index, 3: controlStatus
    def __init__(self):
        self.order = 0
        self.points = []
        self.node = 0
    
    def add(self, persil, points, node_status):
        #node is 1 if vertex is node, and 0 if are ordinary vertex
        self.order = persil
        self.points = points
        self.node = node_status
    
    def addPoint(self, point):
        self.points.append(point)

        

# Mendefinisikan fungsi pencarian jarak terdekat (Euclidean Distance)
def Euclidean(a, b):
    Distance = np.linalg.norm(np.array(a) - np.array(b))
    return Distance

def findNIBIndex(Fields):
    NIBIndex = 0
    ALATIndex = 0
    for i in range(len(Fields)):
        if Fields[i][0] == "NIB":
            NIBIndex = i - 1
        elif Fields[i][0] == "ALATUKUR":
            ALATIndex = i-1
    return NIBIndex

def nodeEvaluation(prevPoint, nextPoint, currPoint):
    toleranceNode = 2.5
    x12 = prevPoint[0]-currPoint[0]
    y12 = prevPoint[1]-currPoint[1]
    x23 = nextPoint[0]-currPoint[0]
    y23 = nextPoint[1]-currPoint[1]

    D12 = math.sqrt( x12**2 + y12**2)
    D23 = math.sqrt( x23**2 + y23**2)

    # Selisih lebih dari 1 meter
    if (D12 > toleranceNode or D23 > toleranceNode):
        #jika sudut tegak lurus, menghindari nilai pembagian dengan 0 ketika menghitung azimut.
        if y12 == 0 or y23 == 0:
            return True
        else:
            Az1 = math.degrees(math.atan( x12/y12 ))
            Az2 = math.degrees(math.atan( x23/y23 ))
            absolutSelisih = abs(Az1 - Az2);
            if absolutSelisih < 100:
                if not(absolutSelisih > 0 and absolutSelisih < 4.6):
                    return True
                else:
                    return False
            else:
                if not(absolutSelisih > 175.4 and absolutSelisih < 184.6):
                    return True
                else:
                    return False
    else:
        return False

def closestControl(tie, dataPoint):
    point = [dataPoint.loc['x'], dataPoint.loc['y']]
    closest = -1
    closestControl = []
    for i in range (len(tie.index)):
        if (tie.loc[i,'control'])== 1:
            control = [tie.loc[i,'x'] , tie.loc[i, 'y']]
            temp = Euclidean(point, control)
            if (closest == -1 or closest > temp):
                closest = temp
                closestControl = control
    return closestControl

def checkSameNode(pointA, pointB, pointB2):
        ax = round(pointA['x'],1)
        ay = round(pointA['y'],1)
        bx = round(pointB['x'],1)
        by = round(pointB['y'],1)
        bx2 = round(pointB2['x'],1)
        by2 = round(pointB2['y'],1)
        # print (ax, bx, bx2, ay, by, by2)
        if (ax == bx) and (ay == by):
            return True
        else:
            if (ax == bx2) and (ay == by2):
                return True
            else:
                # print ("point A beda sama point B")
                return False
            
def proj2(point, segment_start, segment_end):
    # print ('Running projection ...')
    # return distance, pointOnSegment
    x1 = segment_start['x']
    x2 = segment_end['x']
    y1 = segment_start['y']
    y2 = segment_end['y']
    xp = point['x']
    yp = point['y']
    x12 = x2 - x1
    y12 = y2 - y1
    dotp = x12 * (xp - x1) + y12 * (yp - y1)
    dot12 = x12 * x12 + y12 * y12
    if dot12:
        coeff = dotp / dot12
        lx = x1 + x12 * coeff
        ly = y1 + y12 * coeff
        point = QgsPointXY(xp, yp)
        pointOnSegment = QgsPointXY(lx, ly)
        outPoint = [lx, ly]
        distance = point.distance(pointOnSegment)
        if ((lx >= x1 and lx <= x2) or (lx <= x1 and lx >= x2)) and ((ly >= y1 and ly <= y2) or (ly <= y1 and ly >= y2)) and (distance > 0):
            return distance, outPoint
        else:
            return -1, 0
    else:
        # return None
        return -1, 0

def proj(point, segment_start, segment_end):
    # print ('Running projection ...')
    # return distance, pointOnSegment
    x1 = segment_start[0]
    x2 = segment_end[0]
    y1 = segment_start[1]
    y2 = segment_end[1]
    xp = point[0]
    yp = point[1]
    x12 = x2 - x1
    y12 = y2 - y1
    dotp = x12 * (xp - x1) + y12 * (yp - y1)
    dot12 = x12 * x12 + y12 * y12
    if dot12:
        coeff = dotp / dot12
        lx = x1 + x12 * coeff
        ly = y1 + y12 * coeff
        pointToCheck = QgsPointXY(point[0], point[1])
        pointOnSegment = QgsPointXY(lx, ly)
        distance = pointToCheck.distance(pointOnSegment)
        if ((lx >= x1 and lx <= x2) or (lx <= x1 and lx >= x2)) and ((ly >= y1 and ly <= y2) or (ly <= y1 and ly >= y2)) and (distance > 0):
            return distance, pointOnSegment
        else:
            return -1, 0
    else:
        # return None
        return -1, 0

def merge(lsts):
    sets = [set(lst) for lst in lsts if lst]
    merged = True
    while merged:
        merged = False
        results = []
        while sets:
            common, rest = sets[0], sets[1:]
            sets = []
            for x in rest:
                if x.isdisjoint(common):
                    sets.append(x)
                else:
                    merged = True
                    common |= x
            results.append(common)
        sets = results
    return sets