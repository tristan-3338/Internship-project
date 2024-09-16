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
n_evenements = 6000

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

indices_to_remove = [index for index, sublist in enumerate(max_i) if -1 in sublist]

for index in sorted(indices_to_remove, reverse=True):
    del max_i[index]
    del plane_values[index]
    del strip_values[index]
    del qf_values [index]

donnee_list=[]
for numero_plane in range(4):
    #print("plane = ", numero_plane, "/n")
    donnee=[]
    for i in range(len(max_i)): #boucle sur les événments
        x = [-1,-1,-1,-1]
        y = [-1,-1,-1,-1]
        index = 0
        histogram = TH2F("h", "h",100,-1,4,100,0,16)
        for indice,k in enumerate(max_i[i]):
            if k != -1:
                if plane_values[i][k] != numero_plane: #si différent du plan spécifique
                    histogram.Fill(plane_values[i][k],strip_values[i][k])
                x[indice] = plane_values[i][k]
                y[indice] = strip_values[i][k]
                index +=1
        #print("plane",plane_values[i][k], " événement = ", i)     
        #print("x = ",x)
        #print("y = ",y)
        # Créer une fonction linéaire pour la régression
        linear_fit = ROOT.TF1("linear_fit", "pol1", 0, 5)
        # Ajuster le graphique à la fonction linéaire
        #histogram.Fit(linear_fit, "Q")    
        histogram.Fit(linear_fit, "Q")

        # Récupérer les paramètres de la régression linéaire
        slope = linear_fit.GetParameter(1) #pente
        intercept = linear_fit.GetParameter(0) #ordonnée à l'origine
        
        #retrieve the y value for each planes
        for j in x:
            if j == numero_plane: #si hit dans le plan spécifique
                y_regression = slope*numero_plane + intercept
                #print("slope = ", slope,"intecept = ",intercept,"y régression = ",y_regression, "y réel = ",y[numero_plane],"différence = ",y_regression-y[numero_plane]) 
                if not donnee: #si la liste donnee est vide
                    donnee.append([(y_regression-y[numero_plane]),1])
                else:
                    trouver = False
                    for distance in donnee:
                        if distance[0] == (y_regression-y[numero_plane]):
                            distance[1] += 1
                            trouver = True
                            break
                    if trouver == False:
                        donnee.append([(y_regression-y[numero_plane]),1])
    donnee_list.append(donnee)
#print("distance plane  = ", donnee_list)                 


for i in range(4):
    h_distance = TH1F("distance", f"plane{i}", 35, -5,5)
    for k in donnee_list[i]:
        h_distance.Fill(k[0],k[1])
    c = TCanvas("c","distance")
    h_distance.Draw()
    c.Update()
    c.SaveAs(f"distance_plots/max_charge/plane{i}.png")