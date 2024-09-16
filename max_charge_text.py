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

n_entries = tree.GetEntries() #number of events
#print(n_entries)
n_evenements = 0

for i_event in range(n_entries): #loops 4 tree events
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
        n_evenements += 1


# Ouvrir le fichier en mode lecture
with open('offset_charge.txt', 'r') as file:
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
#print(plane_values)
#print(n_hits_per_plane_list)
#print(qb_list)

for k in range(n_evenements):
    for i in range(len(plane_values[k])):
        #print(plane_values[k][i]*16+strip_values[k][i])
        qf_values[k][i] = qf_values[k][i] - most_probable_charge[plane_values[k][i]*16+strip_values[k][i]][0]
        qb_values[k][i] = qb_values[k][i] - most_probable_charge[plane_values[k][i]*16+strip_values[k][i]][1] 

max_i=[]

for i in range(n_evenements):
    index_max = [-1, -1, -1, -1]
    max_QF = [-1, -1, -1, -1]

    max_QF[plane_values[i][0]] = qf_values[i][0]
    index_max[plane_values[i][0]] = 0

    for k in range(1,len(plane_values[i])):
        if max_QF[plane_values[i][k]] < qf_values[i][k]:
            max_QF[plane_values[i][k]] = qf_values[i][k]
            index_max[plane_values[i][k]] = k
    max_i.append(index_max)


with open('max_charge.txt','w') as file:
    for row in max_i:
        file.write(f"{row}\n")