#Copyright Yien Chao 2020

import clr

# Import DocumentManager and TransactionManager
clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

clr.AddReference("RevitAPIUI")
from  Autodesk.Revit.UI import *
# Import RevitAPI
clr.AddReference("RevitAPI")
import Autodesk
from Autodesk.Revit.DB import *

doc = DocumentManager.Instance.CurrentDBDocument
view = doc.ActiveView
#Vcollector = FilteredElementCollector(doc)
#views = Vcollector.OfClass(View).ToElements()
#Serie900 = [v for v in views if "DRF" in v.Name]

#dict of linestyles
try:
	cat = Category.GetCategory(doc, BuiltInCategory.OST_Lines)
	gs = cat.GetGraphicsStyle(GraphicsStyleType.Projection)
	gsCat = gs.GraphicsStyleCategory.SubCategories
	LS = [i.GetGraphicsStyle(GraphicsStyleType.Projection) for i in gsCat]
	names = [i.Name for i in LS]
except AttributeError:
	pass
	
Dict = dict(zip(names,LS))

def getDRF(wall):
	type = doc.GetElement(wall.GetTypeId())
	return type.get_Parameter(BuiltInParameter.FIRE_RATING).AsString()

def getStyle(value):
	for k in Dict.keys():
		try:
			if value in k:
				return Dict[k]
			else:
				pass
		except:
			pass

def draw2D(view):
	collector = FilteredElementCollector(doc)
	filter = Selection.SelectableInViewFilter(doc,view.Id)
	elements = collector.OfClass(Wall).WherePasses(filter)
	walls = [w for w in elements if getDRF(w)]
	wallsDRF = [getDRF(w) for w in walls]
	
	Locations = [w.Location for w in walls]
	curves = [L.Curve for L in Locations]
	
	#drawings and settings detail lines
	for curve, DRF in zip(curves,wallsDRF):
		line = doc.Create.NewDetailCurve(view,curve)
		line.LineStyle = getStyle(DRF)
	else:
		pass

	

TransactionManager.Instance.ForceCloseTransaction()
t = Transaction(doc,"creation de ligne DRF")
t.Start()

draw2D(view)
	
t.Commit()