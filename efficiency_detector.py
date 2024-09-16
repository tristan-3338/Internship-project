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
#print(most_probable_charge[1])

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
        qf_values[k][i] = qf_values[k][i] - offset_charge[plane_values[k][i]*16+strip_values[k][i]][0]
        qb_values[k][i] = qb_values[k][i] - offset_charge[plane_values[k][i]*16+strip_values[k][i]][1]
        diff_event.append((tf_values[k][i]- tb_values[k][i]) - offset_time[plane_values[k][i]*16+strip_values[k][i]])
    diff.append(diff_event)

#print("tous les événements ", max_i)
#print(qf_values)

#print(plane_values)
#print(strip_values)
new_max_i = []
new_plane_values = []
new_strip_values = []
new_qf_values = []
new_diff = []

indices_to_keep = [index for index, sublist in enumerate(max_i) if sublist.count(-1) == 1]

#garde les événements avec 3 hits
for index in sorted(indices_to_keep, reverse=True):
    new_max_i.append(max_i[index])
    new_plane_values.append(plane_values[index])
    new_strip_values.append(strip_values[index])
    new_qf_values.append(qf_values[index])
    new_diff.append(diff[index])
indices_to_remove = [index for index, sublist in enumerate(max_i) if -1 in sublist]

#garde les événements avec 4 hits
for index in sorted(indices_to_remove, reverse=True):
    del max_i[index]
    del plane_values[index]
    del strip_values[index]
    del qf_values[index]
    del diff[index]
#print("nombre événements avec 3 hits = ", len(new_max_i))
#print("nombre événements avec 4 hits = ", len(max_i))

averages_list_charge_4points=[]
averages_list_time_4points=[]
for k_event,k in enumerate(max_i):
    average_list_charge_4points=[]
    average_list_time_4points=[]
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
            average_list_charge_4points.append([a,qf_values[k_event][k[i]],b])
            average_list_time_4points.append([c,diff[k_event][k[i]],d])
            #print("average_list = ",average_list)
        a=0
        b=0
        c=0
        d=0
    averages_list_charge_4points.append(average_list_charge_4points)
    averages_list_time_4points.append(average_list_time_4points)

averages_list_charge_3points=[]
averages_list_time_3points=[]
for k_event,k in enumerate(new_max_i):
    average_list_charge_3points=[]
    average_list_time_3points=[]
    a = 0
    b = 0
    c = 0
    d = 0
    for i in range(4):
        if k[i] >= 0:
            #print("event = ", k_event)
            #print("k[i] = ",k[i])
            if k[i]-1 >= 0 and new_plane_values[k_event][k[i]-1] == new_plane_values[k_event][k[i]]:
                if new_qf_values[k_event][k[i]-1] >= 0:
                    if new_diff[k_event][k[i]-1] >= -10 and new_diff[k_event][k[i]-1] <= 10:
                        a = new_qf_values[k_event][k[i]-1]
                        c = new_diff[k_event][k[i]-1]
                else:
                    a = 0
                    c = 0
            if k[i]+1 < len(new_plane_values[k_event]) and new_plane_values[k_event][k[i]+1] == new_plane_values[k_event][k[i]]:
                if new_qf_values[k_event][k[i]+1] >= 0:
                    if new_diff[k_event][k[i]+1] >= -10 and new_diff[k_event][k[i]+1] <= 10:
                        b = new_qf_values[k_event][k[i]+1]
                        d = new_diff[k_event][k[i]+1] 
                else:
                    b = 0
                    d = 0
            average_list_charge_3points.append([a,new_qf_values[k_event][k[i]],b])
            average_list_time_3points.append([c,new_diff[k_event][k[i]],d])
            #print("average_list = ",average_list)
        a=0
        b=0
        c=0
        d=0
    averages_list_charge_3points.append(average_list_charge_3points)
    averages_list_time_3points.append(average_list_time_3points)

treshold_time= [0.714,0.453,0.465,0.741]
treshold_charge = 0.597
h_list=[]
h_list_tot=[]

for n in range(4):
    h_list.append(TH2F(f"efficiency plane{n}", f"efficiency plane{n};x (time);y (charge)",36,-300,300,36,-30,320))
    h_list_tot.append(TH2F("h", "h",36,-300,300,36,-30,320))
ROOT.gStyle.SetOptStat(0) 
for numero_plane in range(4):    
    #print("plane = ", numero_plane, "/n")
    for i in range(len(max_i)): #boucle sur les événments
        x = [-1,-1,-1,-1]
        y_time = [-1,-1,-1,-1]
        y_charge = [-1,-1,-1,-1]
        index = 0
        h_time = TH2F("h", "h",100,-1,4,100,-5,5)
        h_charge = TH2F("h", "h",100,-1,4,100,0,16)
        for indice,k in enumerate(max_i[i]):
            if k != -1:
                somme = averages_list_charge_4points[i][index][0]+averages_list_charge_4points[i][index][1]+averages_list_charge_4points[i][index][2]
                #print(averages_list[i][index][0]," ", averages_list[i][index][1]," ", averages_list[i][index][2]," ssomme = ", somme)
                average_time = (averages_list_charge_4points[i][index][0]*averages_list_time_4points[i][index][0] + averages_list_charge_4points[i][index][1]*averages_list_time_4points[i][index][1] + averages_list_charge_4points[i][index][2]*averages_list_time_4points[i][index][2])/somme
                #print("(",averages_list[i][index][0], strip_values[i][k]-1 , averages_list[i][index][1], strip_values[i][k], averages_list[i][index][2], strip_values[i][k]+1,")"," moyenne ", i," = ",average, "\n")
                average_charge = (averages_list_charge_4points[i][index][0]*(strip_values[i][k]-1) + averages_list_charge_4points[i][index][1]*strip_values[i][k] + averages_list_charge_4points[i][index][2]*(strip_values[i][k]+1))/somme
                #if plane_values[i][k] != numero_plane: #si différent du plan spécifique
                h_time.Fill(plane_values[i][k],average_time)
                h_charge.Fill(plane_values[i][k],average_charge)
                x[indice] = plane_values[i][k]
                y_time[indice] = average_time
                y_charge[indice] = average_charge
                index +=1

                linear_fit = ROOT.TF1("linear_fit", "pol1", 0, 5)
        # Ajuster le graphique à la fonction linéaire
        #histogram.Fit(linear_fit, "Q")    
        h_time.Fit(linear_fit, "Q")
        
        # Récupérer les paramètres de la régression linéaire
        slope_time = linear_fit.GetParameter(1) #pente
        intercept_time = linear_fit.GetParameter(0) #ordonnée à l'origine

        h_charge.Fit(linear_fit, "Q")
        slope_charge = linear_fit.GetParameter(1) #pente
        intercept_charge = linear_fit.GetParameter(0)

        #retrieve the y value for each planes
        for j in x:
            if j == numero_plane: #si hit dans le plan spécifique
                y_regression_time = slope_time*numero_plane + intercept_time
                y_regression_charge = slope_charge*numero_plane + intercept_charge
                #print("slope = ", slope,"intecept = ",intercept,"y régression = ",y_regression, "y réel = ",y[numero_plane],"différence = ",y_regression-y[numero_plane]) 
                h_list_tot[numero_plane].Fill(y_regression_time*165.7,y_regression_charge*18.5)
                if abs((y_regression_time-y_time[numero_plane])) <= treshold_time[numero_plane] and abs((y_regression_charge-y_charge[numero_plane])) <= treshold_charge:
                    h_list[numero_plane].Fill(y_regression_time*165.7,y_regression_charge*18.5)

for i in range(len(new_max_i)): #boucle sur les événments
    x = [-1,-1,-1,-1]
    y_time_3points = [-1,-1,-1,-1]
    y_charge_3points = [-1,-1,-1,-1]
    index = 0
    h_time_3points = TH2F("h", "h",100,-1,4,100,-5,5)
    h_charge_3points = TH2F("h", "h",100,-1,4,100,0,16)
    for indice,k in enumerate(new_max_i[i]):
        if k != -1:
            somme_3points = averages_list_charge_3points[i][index][0]+averages_list_charge_3points[i][index][1]+averages_list_charge_3points[i][index][2]
            average_time_3points = (averages_list_charge_3points[i][index][0]*averages_list_time_3points[i][index][0] + averages_list_charge_3points[i][index][1]*averages_list_time_3points[i][index][1] + averages_list_charge_3points[i][index][2]*averages_list_time_3points[i][index][2])/somme_3points
            average_charge_3points = (averages_list_charge_3points[i][index][0]*averages_list_time_3points[i][index][0] + averages_list_charge_3points[i][index][1]*averages_list_time_3points[i][index][1] + averages_list_charge_3points[i][index][2]*averages_list_time_3points[i][index][2])/somme_3points
            h_time_3points.Fill(new_plane_values[i][k],average_time_3points)
            h_charge_3points.Fill(new_plane_values[i][k],average_charge_3points)
            x[indice] = new_plane_values[i][k]
            y_time_3points[indice] = average_time_3points
            y_charge_3points[indice] = average_charge_3points
            index +=1

    linear_fit = ROOT.TF1("linear_fit", "pol1", 0, 5)

    # Ajuster le graphique à la fonction linéaire  
    h_time_3points.Fit(linear_fit, "Q")
    slope_time_3points = linear_fit.GetParameter(1) #pente
    intercept_time_3points = linear_fit.GetParameter(0) #ordonnée à l'origine

    h_charge_3points.Fit(linear_fit, "Q")
    slope_charge_3points = linear_fit.GetParameter(1) #pente
    intercept_charge_3points = linear_fit.GetParameter(0)

    #retrieve the y value for each planes
    for j in x:
        if j == -1:
            y_regression_time_3points = slope_time_3points*x.index(j) + intercept_time_3points
            y_regression_charge_3points = slope_charge_3points*x.index(j) + intercept_charge_3points
            if -2 <= y_regression_time_3points <= 2 and 0<= y_regression_charge_3points <=16:
                print("coordonnée point 4eme hit : [",y_regression_time_3points,",",y_regression_charge_3points,"]")
                h_list_tot[x.index(j)].Fill(y_regression_time_3points*165.7,y_regression_charge_3points*18.5)
                   
for n in range(4):
    # Cloner le premier histogramme pour stocker le résultat
    h = h_list[n].Clone("efficiency_detector")
    h.SetTitle("efficiency of the detector")

    # Diviser histoResult par histo2
    h.Divide(h_list_tot[n])   
    """nbins_x = h_list[n].GetNbinsX()
    nbins_y = h_list[n].GetNbinsY()
    #h = TH2F(f"efficiency plane{n}", f"efficiency plane{n};x (time);y (charge)",36,-2,2,36,-1,17)
    for i in range(1, nbins_x + 1):
        for j in range(1, nbins_y + 1):
            #print("coordonée : (",i,",",j,")")
            n_point = h_list[n].GetBinContent(i, j)
            n_total_point= h_list_tot[n].GetBinContent(i,j)
            if n_total_point > 0 :
                #print("nombre points divisés  = ",n_point/n_total_point)
                h.Fill(h.GetXaxis().GetBinCenter(i), h.GetYaxis().GetBinCenter(j), n_point/n_total_point)"""
     # Initialiser la somme et le nombre de bins
    sum_values = 0
    total_bins = 0
    # Parcourir tous les bins pour calculer la somme des contenus
    for bin_x in range(3, 35):
        for bin_y in range(3, 33):
            value = h.GetBinContent(bin_x, bin_y)
            sum_values += value
            total_bins += 1  # Incrémenter le compteur de bins

    # Calculer la moyenne
    mean_value = sum_values / total_bins
    print("efficiency = ", mean_value) 
    c=TCanvas(f"c_{n}","efficiency")
    h.SetMinimum(0)   # Minimum de l'échelle de couleur
    h.SetMaximum(1)
    h.Draw("COLZ")
    c.Update()
    c.SaveAs(f"plot_efficiency_detector/plane{n}.png")
    
