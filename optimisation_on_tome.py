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

#calibration
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
indices_to_remove = [index for index, sublist in enumerate(max_i) if -1 in sublist]
indices_to_keep = [index for index, sublist in enumerate(max_i) if sublist.count(-1) == 1]

#garde les événements avec 3 hits
for index in sorted(indices_to_keep, reverse=True):
    new_max_i.append(max_i[index])
    new_plane_values.append(plane_values[index])
    new_strip_values.append(strip_values[index])
    new_qf_values.append(qf_values[index])
    new_diff.append(diff[index])
#garde les événements avec 4 hits
for index in sorted(indices_to_remove, reverse=True):
    del max_i[index]
    del plane_values[index]
    del strip_values[index]
    del qf_values[index]
    del diff[index]


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

donnee_list_4points=[]
donnee_list_3points=[]
for numero_plane in range(4):
    #print("plane = ", numero_plane, "/n")
    donnee4=[]
    donnee3=[]
    for i in range(len(max_i)): #boucle sur les événments
        x = [-1,-1,-1,-1]
        y = [-1,-1,-1,-1]
        index = 0
        histogram = TH2F("h_4", "h_4",100,-1,4,100,-5,5)
        for indice,k in enumerate(max_i[i]):
            if k != -1:
                somme = averages_list_charge_4points[i][index][0]+averages_list_charge_4points[i][index][1]+averages_list_charge_4points[i][index][2]
                #print(averages_list[i][index][0]," ", averages_list[i][index][1]," ", averages_list[i][index][2]," ssomme = ", somme)
                average = (averages_list_charge_4points[i][index][0]*averages_list_time_4points[i][index][0] + averages_list_charge_4points[i][index][1]*averages_list_time_4points[i][index][1] + averages_list_charge_4points[i][index][2]*averages_list_time_4points[i][index][2])/somme
                #print("(",averages_list[i][index][0], strip_values[i][k]-1 , averages_list[i][index][1], strip_values[i][k], averages_list[i][index][2], strip_values[i][k]+1,")"," moyenne ", i," = ",average, "\n")
                if plane_values[i][k] != numero_plane: #si différent du plan spécifique
                    histogram.Fill(plane_values[i][k],average)
                x[indice] = plane_values[i][k]
                y[indice] = average
                index +=1

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
                if not donnee4: #si la liste donnee est vide
                    donnee4.append([(y_regression-y[numero_plane]),1])
                else:
                    trouver = False
                    for distance in donnee4:
                        if distance[0] == (y_regression-y[numero_plane]):
                            distance[1] += 1
                            trouver = True
                            break
                    if trouver == False:
                        donnee4.append([(y_regression-y[numero_plane]),1])
    donnee_list_4points.append(donnee4)

    for i in range(len(new_max_i)): #boucle sur les événments
        x = [-1,-1,-1,-1]
        y = [-1,-1,-1,-1]
        index = 0
        histogram = TH2F("h_3", "h_3",100,-1,4,100,-20,20)
        for indice,k in enumerate(new_max_i[i]):
            if k != -1:
                somme = averages_list_charge_3points[i][index][0]+averages_list_charge_3points[i][index][1]+averages_list_charge_3points[i][index][2]
                #print(averages_list[i][index][0]," ", averages_list[i][index][1]," ", averages_list[i][index][2]," ssomme = ", somme)
                average = (averages_list_charge_3points[i][index][0]*averages_list_time_3points[i][index][0] + averages_list_charge_3points[i][index][1]*averages_list_time_3points[i][index][1] + averages_list_charge_3points[i][index][2]*averages_list_time_3points[i][index][2])/somme
                #print("(",averages_list[i][index][0], strip_values[i][k]-1 , averages_list[i][index][1], strip_values[i][k], averages_list[i][index][2], strip_values[i][k]+1,")"," moyenne ", i," = ",average, "\n")
                if new_plane_values[i][k] != numero_plane: #si différent du plan spécifique
                    histogram.Fill(new_plane_values[i][k],average)
                x[indice] = new_plane_values[i][k]
                y[indice] = average
                index +=1

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
                if not donnee3: #si la liste donnee est vide
                    donnee3.append([(y_regression-y[numero_plane]),1])
                else:
                    trouver = False
                    for distance in donnee3:
                        if distance[0] == (y_regression-y[numero_plane]):
                            distance[1] += 1
                            trouver = True
                            break
                    if trouver == False:
                        donnee3.append([(y_regression-y[numero_plane]),1])
    donnee_list_3points.append(donnee3)
#print(donnee_list_3points)
"""donnee_list=[]
for numero_plane in range(4):
    #print("plane = ", numero_plane, "/n")
    donnee=[]
    for i in range(len(max_i)): #boucle sur les événments
        x = [-1,-1,-1,-1]
        y = [-1,-1,-1,-1]
        index = 0
        histogram = TH2F("h", "h",100,-1,4,100,-5,5)
        for indice,k in enumerate(max_i[i]):
            if plane_values[i][k] != numero_plane: #si différent du plan spécifique
                histogram.Fill(plane_values[i][k],diff[i][k])
            x[indice] = plane_values[i][k]
            y[indice] = diff[i][k]
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
    donnee_list.append(donnee)"""
#print("distance plane  = ", donnee_list)          


for i in range(4):
    h_distance_3_points = TH1F("distance", f"distance plane{i}", 120, -3,3)
    h_distance_4_points = TH1F("distance", f"distance plane{i}", 300, -4,4)
    for k in donnee_list_4points[i]:
        h_distance_4_points.Fill(k[0],k[1])
    for j in donnee_list_3points[i]:
        h_distance_3_points.Fill(j[0],j[1])
    c = TCanvas("c","distance average")
    h_distance_3_points.SetLineColor(ROOT.kBlue)
    h_distance_3_points.SetLineWidth(2)
    h_distance_3_points.SetLineStyle(1)
    h_distance_3_points.Draw() 
    h_distance_4_points.SetLineColor(ROOT.kRed)
    h_distance_4_points.SetLineWidth(2)
    h_distance_4_points.SetLineStyle(1)       
    h_distance_4_points.Draw("SAME")    
    gaussian1 = ROOT.TF1("gaussian", "gaus", -1, 1)
    gaussian2 = ROOT.TF1("gaussian", "gaus", -1, 1)
    gaussian1.SetParameters(2, 0, 2) #amplitude,mean,sigma
    gaussian2.SetParameters(1, 0, 0.5) 
    h_distance_3_points.Fit(gaussian1, "E")
    h_distance_4_points.Fit(gaussian2, "E")
    gaussian1.Draw("SAME")
    gaussian2.Draw("SAME")
    #x = ROOT.RooRealVar("distance", "distance", -5, 5, "")
    # Transformation de l'histogramme en un objet RooDataHist
    #data = ROOT.RooDataHist("data", "dataset with x", ROOT.RooArgList(x), h_distance)
    
    """mean = ROOT.RooRealVar("mean", "mean", 0.1, -1, 1)
    alphaL = ROOT.RooRealVar("sigmaL", "sigmaL", 1,0.1,10)
    alphaR = ROOT.RooRealVar("sigmaR", "sigmaR", 2,0.1,10)
    sigmaR = ROOT.RooRealVar("alphaR", "alphaR", 1.5, 0, 5)
    sigmaL = ROOT.RooRealVar("alphaL", "alphaL", 0.3, 0, 5)
    n = ROOT.RooRealVar("n", "n", 5, 0.1, 10)
    fit = ROOT.RooCrystalBall("distance fiting", "distance fiting", x, mean,sigmaL, sigmaR,alphaL,n,alphaR,n)"""

    # Définir les paramètres pour la première gaussienne
    """mean = ROOT.RooRealVar("mean", "mean of gaussian", 0, -2, 2)
    sigma1 = ROOT.RooRealVar("sigma1", "width of gaussian 1", 1, 0.1, 10)
    gauss1 = ROOT.RooGaussian("gauss1", "Gaussian 1 PDF", x, mean, sigma1)
"""
    # Définir les paramètres pour la deuxième gaussienne
    
    """sigma2 = ROOT.RooRealVar("sigma2", "width of gaussian 2", 3, 0.1, 10)
    gauss2 = ROOT.RooGaussian("gauss2", "Gaussian 2 PDF", x, mean, sigma2)

    # Définir le coefficient pour la somme
    frac = ROOT.RooRealVar("frac", "fraction of gauss1", 0.5, 0.0, 1.0)
    # Créer le modèle de somme de gaussiennes
    model = ROOT.RooAddPdf("model", "Sum of Gaussians", ROOT.RooArgList(gauss1, gauss2),ROOT.RooArgList(frac))"""

    # Ajuster la fonction RooCrystalBall sur une plage spécifique
    """fit_min = -1
    fit_max = 1
    x.setRange("fitRange", fit_min, fit_max)

    # Ajustement de la fonction aux données
    gauss1.fitTo(data,"E")

    # Création d'un cadre pour tracer l'histogramme et la courbe ajustée
    frame = x.frame(ROOT.RooFit.Title("CrystalBall fit to histogram data"))
    data.plotOn(frame)
    gauss1.plotOn(frame)
    frame.Draw()

    # Retrieve the fitted parameters
    mean_val = mean.getVal()
    sigma1_val = sigma1.getVal()
    #sigma2_val = sigmaL.getVal()"""

    """fit_results = h_distance.GetFunction("gaussian")
    chi2 = f1.GetChisquare()
    mean = fit_results.GetParameter(1)
    sigma = fit_results.GetParameter(2)
    # Create a TPaveText to display the parameters
    pave_text = ROOT.TPaveText(0.65, 0.7, 0.9, 0.9, "NDC")  # NDC: normalized device coordinates
    pave_text.AddText(f"Mean = {mean:.3f}")
    pave_text.AddText(f"Sigma = {sigma:.3f}")
    pave_text.SetFillColor(0)
    pave_text.SetTextSize(0.03)
    pave_text.SetBorderSize(1)
    pave_text.Draw()"""
    legend = ROOT.TLegend(0.7, 0.7, 0.9, 0.9)
    legend.AddEntry(h_distance_4_points, "4 points", "1")
    legend.AddEntry(h_distance_3_points, "3 points", "1")
    legend.SetTextSize(0.03)
    legend.Draw()
    
    c.Update()
    c.SaveAs(f"distance_plots/time_difference_average/plane{i}.png")
    