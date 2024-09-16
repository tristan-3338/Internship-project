import ROOT
from ROOT import TCanvas,TH1F, TFile, TH2F, TTree, TLine,TLegend,gStyle
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
tf_values=[]
tb_values=[]

n_entries = tree.GetEntries() #number of events
N_events = 4
n_plots = 4


for i_event in range(n_entries): #loops 10 tree events
    tree.GetEntry(i_event) #gets variables for a certain event

    trigger = tree.trigger
    plane_list =list(tree.plane)
    strip_list=list(tree.strip)
    tf_list =list(tree.TF)
    tb_list = list(tree.TB)

    if trigger ==1:
        plane_values.append(plane_list)
        strip_values.append(strip_list)
        tf_values.append(tf_list)
        tb_values.append(tb_list)

# Ouvrir le fichier de max_charge en mode lecture
with open('max_charge.txt', 'r') as file:
    lines_charge = file.readlines()

i_max=[]
# Parcourir chaque ligne du fichier
for line in lines_charge:
    # Utiliser eval pour convertir la chaîne de caractères en liste
    from ast import literal_eval
    list_line = literal_eval(line.strip())
    i_max.append(list_line)

histograms_1 =[]
for plane in range(4):
    for strip in range(16):
        h = TH1F(f"plane{plane} strip{strip}","(TF-TB); number", 300, -10, 10)
        histograms_1.append(h)
for i in range(len(i_max)):
    for k in i_max[i]:
        sum = (tf_values[i][k] - tb_values[i][k])
        if sum <= 10 and sum >= -10:
            histograms_1[plane_values[i][k]*16 + strip_values[i][k]].Fill(sum)
        
        #most_probable_time = histograms[plane_values[i][k]*16 + strip_values[i][k]].GetBinCenter(max_bin)
        #print(most_probable_time)


max = []
x_values = []
y_values = []
first_points = []
last_points = []
for i,hist in enumerate(histograms_1):
    threshold = hist.GetBinContent(hist.GetMaximumBin())/2
    print("seuil = ",threshold)
    max.append(threshold)
    #retrieve the first point crossing the threshold
    bin_index1 = hist.FindFirstBinAbove(threshold)
    first_points.append(hist.GetBinCenter(bin_index1))
    #retrieve the last point crossing the threshold
    bin_index2 =hist.FindLastBinAbove(threshold)
    last_points.append(hist.GetBinCenter(bin_index2))
             
    canva = TCanvas("c","c")
    hist.Draw()
    canva.Update()
    canva.SaveAs(f"time_plots_calibration/difference/difference{i}.png")
#print("x = ",x_values)
#print("y = ", y_values)

"""histograms_2 =[]
for plane in range(4):
    for strip in range(16):
        h = TH1F(f"plane{plane} strip{strip}","(TF-TB); number", 300, -10, 10)
        histograms_2.append(h)


#print("first points = ", first_points)
#print("last points = ",last_points)
#print(max)

for i in range(len(i_max)):
    for k in i_max[i]:
        diff = (tf_values[i][k] - tb_values[i][k])
        if sum <= 10 and sum >= -10:
            index = plane_values[i][k]*16 + strip_values[i][k]
            histograms_2[index].Fill(diff - ((first_points[index]+last_points[index])/2))"""


"""for i,hist in enumerate(histograms_2):
    c = TCanvas("c","c")
    hist.Draw("HIST")
    c.Update()
    c.SaveAs(f"time_plots_calibration/difference_calibrated/difference{i}.png")"""

"""offset = []
for i in range(len(first_points)):
    offset.append((first_points[i]+last_points[i])/2)

with open('offset_time.txt','w') as file:
    for i in offset:
        file.write(f"{i}\n")"""