import ROOT
from ROOT import TCanvas,TH1F, TFile, TH2F, TTree, TLine, gStyle
import os

# variables name : year, month, day, hour, minute, second, unix_time, trigger, n_hits,
# n_hits_per_plane, plane, strip, QF, QB, TF, TB
# Définir une palette de couleurs

# Utilisation de la palette personnalisée

def gradient_couleur(charge):
    index_color = int(charge/2.5 + 22.3)
    if index_color > 99:
        index_color = 99
    if index_color < 0:
        index_color = 0
    return index_color
#try an other calibration

#Get data file
file = TFile("./data/dabc23292080012.root", "READ")
#Get the tree from the file
tree = file.Get("sRPCdata")

n_hits_values=[]
n_hits_per_plane_values=[]
plane_values=[]
strip_values=[]
qf_values=[]
qb_values=[]

n_entries = tree.GetEntries() #number of events
#print(n_entries)
i_event = 176700
n_plots =0

while n_plots <4: #while We have 4 plots
    tree.GetEntry(i_event) #gets variables for a certain event
    #tree.GetEntry(1)
    qb_event=list(tree.QB)
    qf_event=list(tree.QF)
    plane_event=list(tree.plane)
    n_hits_per_plane_event = list(tree.n_hits_per_plane)
    strip_event=list(tree.strip)
    trigger = tree.trigger

    if trigger ==1:
        n_plots += 1
        n_hits_values.append(tree.n_hits)
        n_hits_per_plane_values.append(n_hits_per_plane_event)
        plane_values.append(plane_event)
        strip_values.append(strip_event)
        qf_values.append(qf_event)
        qb_values.append(qb_event)
        print("les événements que l'on va tracer ",i_event)
    i_event += 1

# Ouvrir le fichier en mode lecture
with open('data2.txt', 'r') as file:
    lines = file.readlines()

# Initialiser une liste vide pour stocker les données
most_probable_charge = []

# Parcourir chaque ligne du fichier
for line in lines:
    # Utiliser eval pour convertir la chaîne de caractères en liste
    # Vous pouvez aussi utiliser ast.literal_eval pour plus de sécurité
    from ast import literal_eval
    list_line = literal_eval(line.strip())
    most_probable_charge.append(list_line)
#print(most_probable_charge[1])

#print(n_hits)
#print(plane_list)
#print(n_hits_per_plane_list)
#print(qb_list)

#calibration
for k in range(n_plots):
    for i in range(len(plane_values[k])):
        #print(plane_values[k][i]*16+strip_values[k][i])
        qf_values[k][i] = qf_values[k][i] - most_probable_charge[plane_values[k][i]*16+strip_values[k][i]][0]
        qb_values[k][i] = qb_values[k][i] - most_probable_charge[plane_values[k][i]*16+strip_values[k][i]][1]

max_i=[]

for i in range(n_plots):
    index_max = [-1, -1, -1, -1]
    max_QF = [-1, -1, -1, -1]

    max_QF[plane_values[i][0]] = qf_values[i][0]
    index_max[plane_values[i][0]] = 0

    for k in range(1,len(plane_values[i])):
        if max_QF[plane_values[i][k]] < qf_values[i][k]:
            max_QF[plane_values[i][k]] = qf_values[i][k]
            index_max[plane_values[i][k]] = k
    max_i.append(index_max)

print("max_i = ",max_i)

averages_list=[]
for k_event,k in enumerate(max_i):
    average_list=[]
    a = 0
    b = 0
    for i in range(4):
        if k[i] >= 0:
            #print("event = ", k_event)
            #print("k[i] = ",k[i])
            if k[i]-1 >= 0 and plane_values[k_event][k[i]-1] == plane_values[k_event][k[i]]:
                if qf_values[k_event][k[i]-1] >= 0:
                    a = qf_values[k_event][k[i]-1]
                else:
                    a =0
            if k[i]+1 < len(plane_values[k_event]) and plane_values[k_event][k[i]+1] == plane_values[k_event][k[i]]:
                if qf_values[k_event][k[i]+1] >= 0:
                    b = qf_values[k_event][k[i]+1]
                else:
                    b =0
            average_list.append([a,qf_values[k_event][k[i]],b])
            #print("average_list = ",average_list)
        a=0
        b=0
    averages_list.append(average_list)

print("qf_values = ",qf_values)
#print(qb_values)
#print("plane_values = ", plane_values)
#print("strip_values = ",strip_values)
      
print("average_list = ",averages_list)
#print(new_tf_list)
#print(new_tb_list)


#trajectory
histograms=[]
for k in range(n_plots): #loop all hist
    hist_name = f"h{k}"
    hist_title = f"Histogram {k};plane;strip"
    histogram = TH2F(hist_name, hist_title,100,-1,4,100,0,16)
    histograms.append(histogram)


#Plot trajectory of the particule with average
x_list,y_list =[],[]
points_list_average=[]
points_list_up=[]
points_list_center=[]
points_list_down=[]
index_color=[]
for i in range(n_plots):
    points_average=[]
    points_up=[]
    points_center=[]
    points_down=[]
    x,y=[],[]
    index = 0
    color=[]
    for k in max_i[i]:
        if k != -1:
            color_3_points=[-1,-1,-1]
            somme = averages_list[i][index][0]+averages_list[i][index][1]+averages_list[i][index][2]
            average = (averages_list[i][index][0]*(strip_values[i][k]-1) + averages_list[i][index][1]*strip_values[i][k] + averages_list[i][index][2]*(strip_values[i][k]+1))/somme
            #print("(",averages_list[i][index][0], strip_values[i][k]-1 , averages_list[i][index][1], strip_values[i][k], averages_list[i][index][2], strip_values[i][k]+1,")"," moyenne ", i," = ",average, "\n")
            histograms[i].Fill(plane_values[i][k],average)
            points_average.append([plane_values[i][k],average])
            if strip_values[i][k]+1 < 16:
                points_up.append([plane_values[i][k],strip_values[i][k]+1])
                color_3_points[0] = gradient_couleur(averages_list[i][index][2])
            points_center.append([plane_values[i][k], strip_values[i][k]])
            color_3_points[1] = gradient_couleur(averages_list[i][index][1])
            if strip_values[i][k]-1 > 0:
                points_down.append([plane_values[i][k],strip_values[i][k]-1])
                color_3_points[2] = gradient_couleur(averages_list[i][index][0])
            color.append(color_3_points)
            x.append(plane_values[i][k])
            y.append(average)
            index +=1
    index_color.append(color)
    points_list_average.append(points_average)
    points_list_up.append(points_up)
    points_list_center.append(points_center)
    points_list_down.append(points_down)
    x_list.append(x)
    y_list.append(y)
print(index_color)
print(points_list_down)
        #print(plane_values[i][k])
        #print(strip_values[i][k])
    #histograms[i].SetLineColor(ROOT.kBlue)

    # Ajouter les points au TPolyMarker
        

"""#Plot trajectory of the particule with QFmax+QBmax
index=0
for i in n_hits_per_plane_list:
    print("index= ", index)
    print("i = ",i)
    for k in range(i):
        print("k =", k)
        h.Fill(plane_list[i],strip_list[i],new_qf_list[index]+new_qb_list[index])
        h.SetLineColor(ROOT.kRed)
    
    index+=1"""
# divise charge par 4.55 pour te ramener à une échelle de 0 à 100
# ajouter 22.3
#print(points_list)
c = TCanvas("c1", "trajectory")
c.Divide(2,2) #divide the canva to plot 10 hist
#ROOT.gStyle.SetPalette(ROOT.kCool)  # You can choose others palettes like kBird, kCool, kCherry, etc.
ROOT.gStyle.SetOptStat(0)  
lines_list=[] 
for i, hist in enumerate(histograms):
    c.cd(i+1)
    polymarker_average = ROOT.TPolyMarker()
    polymarker_average.SetMarkerStyle(ROOT.kCircle)
    polymarker_average.SetMarkerColor(ROOT.kBlue)
    polymarker_average.SetMarkerSize(1)  # Agrandir les points
    for points in points_list_average[i]:
        polymarker_average.SetNextPoint(points[0], points[1])
    
    polymarker_up = ROOT.TPolyMarker()
    polymarker_center = ROOT.TPolyMarker()
    polymarker_down = ROOT.TPolyMarker()
    polymarker_up.SetMarkerStyle(20)
    polymarker_center.SetMarkerStyle(20)
    polymarker_down.SetMarkerStyle(20)
    for k,points in enumerate(points_list_up[i]):
        polymarker_up.SetNextPoint(points[0], points[1])
        polymarker_up.SetMarkerColor(index_color[i][k][0])
    for k,points in enumerate(points_list_center[i]):
        polymarker_center.SetNextPoint(points[0], points[1])
        polymarker_center.SetMarkerColor(index_color[i][k][1])
    for k,points in enumerate(points_list_down[i]):
        polymarker_down.SetNextPoint(points[0], points[1])
        polymarker_down.SetMarkerColor(index_color[i][k][2])

    #gStyle.SetPalette(ROOT.kRainbow)
    hist.Draw("COLZ")
    polymarker_up.Draw("P")
    polymarker_down.Draw("P")
    polymarker_center.Draw("P")
    polymarker_average.Draw("P")
    lines=[]
    for x in range(4):
        line = TLine(x, 0, x, 16)
        line.SetLineColor(ROOT.kGray)  # Define the line colour (optional)
        line.SetLineWidth(1)
        lines.append(line)
        line.Draw("SAME")
    lines_list.append(lines)
    # Créer une fonction linéaire pour la régression
    linear_fit = ROOT.TF1("linear_fit", "pol1", 0, 5)
    # Ajuster le graphique à la fonction linéaire
    hist.Fit(linear_fit, "Q")
    # Dessiner la fonction ajustée
    linear_fit.Draw("SAME")
    


c.Update()
c.SaveAs("plots_calibrated/average_events_1100_1104.png")
"""
#Creat a 2D histogram
h1 = TH1F("h_hits_per_plane", "Nombre de Hits par Plane;Plane;Nombre de Hits", 4, 0, 4)
# Remplir l'histogramme avec les données
for i in range(4):
    h1.SetBinContent(i + 1, n_hits_per_plane[i])
#Create a canva for histogram
c1 = TCanvas("c1", "c1")
h1.Draw()

c1.Update()
c1.SaveAs("hits_per_plane.png")"""