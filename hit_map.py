import ROOT
from ROOT import TCanvas,TH1F, TFile, TH2F, TTree, TLine, gStyle
import os

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
tf_values = []
tb_values = []

n_entries = tree.GetEntries() #number of events
#print(n_entries)
n_evenements = 0

for i_event in range(n_entries): #loops 4 tree events
    tree.GetEntry(i_event) #gets variables for a certain event
    #tree.GetEntry(1)
    qb_event=list(tree.QB)
    qf_event=list(tree.QF)
    tb_event=list(tree.TB)
    tf_event=list(tree.TF)
    plane_event=list(tree.plane)
    n_hits_per_plane_event = list(tree.n_hits_per_plane)
    strip_event=list(tree.strip)
    trigger = tree.trigger

    if trigger ==1 :
        n_hits_values.append(tree.n_hits)
        n_hits_per_plane_values.append(n_hits_per_plane_event)
        plane_values.append(plane_event)
        strip_values.append(strip_event)
        qf_values.append(qf_event)
        qb_values.append(qb_event)
        tf_values.append(tf_event)
        tb_values.append(tb_event)
        n_evenements += 1

# Ouvrir le fichier de charge en mode lecture
with open('offset_charge.txt', 'r') as file:
    lines_charge = file.readlines()

# Ouvrir le fichier du temps en mode lecture
with open('offset_time.txt', 'r') as file:
    lines_time = file.readlines()

# Initialiser une liste vide pour stocker les données
offset_charge = []
offset_time = []

# Parcourir chaque ligne des fichiers
for line in lines_charge:
    # Utiliser eval pour convertir la chaîne de caractères en liste
    from ast import literal_eval
    list_line = literal_eval(line.strip())
    offset_charge.append(list_line)

for line in lines_time:
    offset_time.append(float(line))

with open('max_charge.txt', 'r') as file:
    lines_charge = file.readlines()

max_i=[]
# Parcourir chaque ligne du fichier
for line in lines_charge:
    # Utiliser eval pour convertir la chaîne de caractères en liste
    from ast import literal_eval
    list_line = literal_eval(line.strip())
    max_i.append(list_line)

diff = []
for k in range(n_evenements):
    diff_event=[]
    for i in range(len(plane_values[k])):
        #print(plane_values[k][i]*16+strip_values[k][i])
        #qf_values[k][i] = qf_values[k][i] - offset_charge[plane_values[k][i]*16+strip_values[k][i]][0]
        #qb_values[k][i] = qb_values[k][i] - offset_charge[plane_values[k][i]*16+strip_values[k][i]][1]
        diff_event.append((tf_values[k][i]- tb_values[k][i]))
        #diff_event.append((tf_values[k][i]- tb_values[k][i]) - offset_time[plane_values[k][i]*16+strip_values[k][i]])
    diff.append(diff_event)

averages_list_charge=[]
averages_list_time=[]
for k_event,k in enumerate(max_i):
    average_list_charge=[]
    average_list_time=[]
    a = 0
    b = 0
    c = 0
    d = 0
    for i in range(4):
        if k[i] >= 0:
            #print("event = ", k_event)
            #print("k[i] = ",k[i])
            if k[i]-1 >= 0 and plane_values[k_event][k[i]-1] == plane_values[k_event][k[i]]:
                if qf_values[k_event][k[i]-1] >= 0:
                    if diff[k_event][k[i]-1] >= -10 and diff[k_event][k[i]-1] <= 10:
                        a = qf_values[k_event][k[i]-1]
                        c = diff[k_event][k[i]-1]
                else:
                    a = 0
                    c = 0
            if k[i]+1 < len(plane_values[k_event]) and plane_values[k_event][k[i]+1] == plane_values[k_event][k[i]]:
                if qf_values[k_event][k[i]+1] >= 0:
                    if diff[k_event][k[i]+1] >= -10 and diff[k_event][k[i]+1] <= 10:
                        b = qf_values[k_event][k[i]+1]
                        d = diff[k_event][k[i]+1] 
                else:
                    b = 0
                    d = 0
            average_list_charge.append([a,qf_values[k_event][k[i]],b])
            average_list_time.append([c,diff[k_event][k[i]],d])
            #print("average_list = ",average_list)
        a=0
        b=0
        c=0
        d=0
    averages_list_charge.append(average_list_charge)
    averages_list_time.append(average_list_time)

for numero_plane in range(4):    
    h = TH2F(f"plane{numero_plane+1}", "hit map charge calibration; x (time); y(charge)", 150,-450,450,40,-30,320)
    #h = TH2F(f"plane{numero_plane}", "hit map with calibration; x (time); y(charge)", 100,-10,10,50,0,16)    
    #print("plane = ", numero_plane, "/n")
    for i in range(len(max_i)): #boucle sur les événments
        index = 0
        for indice,k in enumerate(max_i[i]):
            if k != -1:
                somme = averages_list_charge[i][index][0]+averages_list_charge[i][index][1]+averages_list_charge[i][index][2]
                if somme >0:
                
                    #print(averages_list[i][index][0]," ", averages_list[i][index][1]," ", averages_list[i][index][2]," ssomme = ", somme)
                    average_time = (averages_list_charge[i][index][0]*averages_list_time[i][index][0] + averages_list_charge[i][index][1]*averages_list_time[i][index][1] + averages_list_charge[i][index][2]*averages_list_time[i][index][2])/somme
                    #print("(",averages_list[i][index][0], strip_values[i][k]-1 , averages_list[i][index][1], strip_values[i][k], averages_list[i][index][2], strip_values[i][k]+1,")"," moyenne ", i," = ",average, "\n")
                    average_charge = (averages_list_charge[i][index][0]*(strip_values[i][k]-1) + averages_list_charge[i][index][1]*strip_values[i][k] + averages_list_charge[i][index][2]*(strip_values[i][k]+1))/somme
                    #if plane_values[i][k] != numero_plane: #si différent du plan spécifique
                    h.Fill(average_time*165.7, average_charge*18.5)
                    index +=1
    c = TCanvas("c", f"plane{numero_plane}")
    h.Draw("COLZ")
    c.Update()
    c.SaveAs(f"hit_map/without_calibration/plane{numero_plane}.png")