import ROOT
from ROOT import TCanvas,TH1F, TFile, TH2F, TTree, TLine, gStyle
import os
# variables name : year, month, day, hour, minute, second, unix_time, trigger, n_hits,
# n_hits_per_plane, plane, strip, QF, QB, TF, TB

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
N_events = 4
n_plots = 4

for i_event in range(n_entries-n_plots,n_entries): #loops 10 tree events
    tree.GetEntry(i_event) #gets variables for a certain event
    #tree.GetEntry(1)
    qb_event=list(tree.QB)
    qf_event=list(tree.QF)
    plane_event=list(tree.plane)
    n_hits_per_plane_event = list(tree.n_hits_per_plane)
    strip_event=list(tree.strip)
    trigger = tree.trigger

    if trigger ==1:
        n_hits_values.append(tree.n_hits)
        n_hits_per_plane_values.append(n_hits_per_plane_event)
        plane_values.append(plane_event)
        strip_values.append(strip_event)
        qf_values.append(qf_event)
        qb_values.append(qb_event)

print(plane_values)
print(strip_values)
print(qf_values)
    
max_i=[]
for i in range(n_plots):
    max_i_per_event=[]
    max_QF =qf_values[i][0]
    index_max = 0
    if len(plane_values[i])==1:
        max_i_per_event.append(0)
    else:
        for k in range(1,len(plane_values[i])):
            if plane_values[i][k-1]< plane_values[i][k] or k == len(plane_values[i])-1:
                max_QF = 0.0
                max_i_per_event.append(index_max)
                index_max = 0
            if max_QF < qf_values[i][k]:
                max_QF = qf_values[i][k]
                index_max = k
            
    max_i.append(max_i_per_event)
print(max_i)        

#print(new_tf_list)
#print(new_tb_list)


#trajectory
histograms=[]
for k in range(n_plots): #loop all hist
    hist_name = f"h{k}"
    hist_title = f"Histogram {k};plane;strip"
    histogram = TH2F(hist_name, hist_title,100,-1,4,100,0,16)
    histograms.append(histogram)


#Plot trajectory of the particule with QF+QB
x_list,y_list =[],[]
points_list=[]
for i in range(n_plots):
    points=[]
    x,y=[],[]
    for k in max_i[i]:
        histograms[i].Fill(plane_values[i][k],strip_values[i][k])
        points.append([plane_values[i][k],strip_values[i][k]])
        x.append(plane_values[i][k])
        y.append(strip_values[i][k])
    points_list.append(points)
    x_list.append(x)
    y_list.append(y)

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
print(points_list)
c = TCanvas("c1", "trajectory")
c.Divide(2,2) #divide the canva to plot 10 hist
#ROOT.gStyle.SetPalette(ROOT.kCool)  # You can choose others palettes like kBird, kCool, kCherry, etc.
ROOT.gStyle.SetOptStat(0)
lines_list=[]
for i, hist in enumerate(histograms):
    c.cd(i+1)
    polymarker = ROOT.TPolyMarker()
    polymarker.SetMarkerStyle(ROOT.kCircle)
    polymarker.SetMarkerColor(ROOT.kBlue)
    polymarker.SetMarkerSize(1)  # Agrandir les points
    for points in points_list[i]:
        polymarker.SetNextPoint(points[0], points[1])

    #gStyle.SetPalette(ROOT.kRainbow)
    hist.Draw("COLZ")
    polymarker.Draw("P")
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
c.SaveAs("plots_without_calibration/4_last_events_qf.png")