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
        test = False
        for i in range(len(qb_event)):
            if abs(qf_event[i] - qb_event[i]) > 100:
                test = True
        if test == False:
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

#print("tous les événements ", max_i)
#print(qf_values)

#print(plane_values)
#print(strip_values) 
indices_to_remove = [index for index, sublist in enumerate(max_i) if -1 in sublist]

for index in sorted(indices_to_remove, reverse=True):
    del max_i[index]
    del plane_values[index]
    del strip_values[index]
    del qf_values [index]
 
#print("en comptant que les événements avec 4 hits ", max_i)
#print(qf_values)

#print(plane_values)
#print(strip_values) 
#print("max_i = ",max_i)

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
    #print(max_i)
    #print(plane_values)
    #print(strip_values)
    #print(qf_values)       
    #print(averages_list)
    #print(new_tf_list)
    #print(new_tb_list)

    #Plot trajectory of the particule with QF+QB
#ROOT.gStyle.SetOptStat(0) 
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
                somme = averages_list[i][index][0]+averages_list[i][index][1]+averages_list[i][index][2]
                #print(averages_list[i][index][0]," ", averages_list[i][index][1]," ", averages_list[i][index][2]," ssomme = ", somme)
                average = (averages_list[i][index][0]*(strip_values[i][k]-1) + averages_list[i][index][1]*strip_values[i][k] + averages_list[i][index][2]*(strip_values[i][k]+1))/somme
                #print("(",averages_list[i][index][0], strip_values[i][k]-1 , averages_list[i][index][1], strip_values[i][k], averages_list[i][index][2], strip_values[i][k]+1,")"," moyenne ", i," = ",average, "\n")
                if plane_values[i][k] != numero_plane: #si différent du plan spécifique
                    histogram.Fill(plane_values[i][k],average)
                x[indice] = plane_values[i][k]
                y[indice] = average
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
    h_distance = TH1F("distance", f"Charge distance plane {i}", 70, -5,5)
    h_distance_off = TH1F("distance", f"Charge distance plane {i}", 70, -1,1)
    for k in donnee_list[i]:
        h_distance.Fill(k[0],k[1])
        h_distance_off.Fill(k[0],k[1])
    c = TCanvas("c",f"Charge distance plane {i}")
    h_distance.Draw()
    x = ROOT.RooRealVar("distance", f"Charge distance plane {i}", -1, 1, "")
    # Transformation de l'histogramme en un objet RooDataHist
    data = ROOT.RooDataHist("data", "dataset with x", ROOT.RooArgList(x), h_distance)
    
    mean = ROOT.RooRealVar("mean", "mean", 0.1, -1, 1)
    alphaL = ROOT.RooRealVar("sigmaL", "sigmaL", 1,0.1,10)
    alphaR = ROOT.RooRealVar("sigmaR", "sigmaR", 2,0.1,10)
    sigmaR = ROOT.RooRealVar("alphaR", "alphaR", 1.5, 0, 5)
    sigmaL = ROOT.RooRealVar("alphaL", "alphaL", 0.3, 0, 5)
    n = ROOT.RooRealVar("n", "n", 5, 0.1, 10)
    fit = ROOT.RooCrystalBall("distance fiting", "distance fiting", x, mean,sigmaL, sigmaR,alphaL,n,alphaR,n)

    # Ajuster la fonction RooCrystalBall sur une plage spécifique
    fit_min = -1
    fit_max = 1
    x.setRange("fitRange", fit_min, fit_max)
    # Ajustement de la fonction aux données
    fitResult = fit.fitTo(data, ROOT.RooFit.Save())

    # Création d'un cadre pour tracer l'histogramme et la courbe ajustée
    frame = x.frame(ROOT.RooFit.Title("CrystalBall fit to histogram data"))
    data.plotOn(frame)
    fit.plotOn(frame)
    frame.Draw("SAME")

    # Retrieve the fitted parameters
    #mean_val = mean.getVal()
    #sigma1_val = sigmaR.getVal()
    #sigma2_val = sigmaL.getVal()
    chi2_crystalBall = 0
    for j in range(1, h_distance_off.GetNbinsX() + 1):
        x_val = h_distance_off.GetBinCenter(j)
        y_obs = h_distance_off.GetBinContent(j)
        x.setVal(x_val)
        y_exp = fit.getVal(ROOT.RooArgSet(x)) * h_distance_off.GetBinWidth(j) * h_distance_off.GetEntries()
        if y_exp > 0:
            chi2_crystalBall += (y_obs - y_exp) ** 2 / y_exp
    
    double_gaus = ROOT.TF1("double_gaus", "[0]*TMath::Gaus(x, [1], [2]) + [3]*TMath::Gaus(x, [4], [5])", -1, 1)
    double_gaus.SetParameters(2, 0, 0.6, 2, 0, 0.8)
    h_distance.Fit(double_gaus, "E")
    double_gaus.Draw("SAME")
    chi2_gauss = double_gaus.GetChisquare()
    #sigma1 = double_gaus.GetParameter(2)
    #sigma2 = double_gaus.GetParameter(5)

    # Create a TPaveText to display the parameters
    pave_text = ROOT.TPaveText(0.65, 0.7, 0.9, 0.9, "NDC")  # NDC: normalized device coordinates
    #pave_text.AddText(f"Sigma1 = {sigma1:.3f}")
    #pave_text.AddText(f"Sigma2 = {sigma2:.3f}")
    pave_text.AddText(f"chi2 db_gauss = {chi2_gauss:.3f}")
    pave_text.AddText(f"chi2 crystalBall = {chi2_crystalBall:.3f}")
    pave_text.SetFillColor(0)
    pave_text.SetTextSize(0.03)
    pave_text.SetBorderSize(1)
    pave_text.Draw("SAME")

    legend = ROOT.TLegend(0.15, 0.7, 0.35, 0.9)
    legend.AddEntry(double_gaus, "Double Gauss", "l")
    legend.AddEntry(fit, "CrystalBall Fit", "l")
    legend.Draw("SAME")

    c.SaveAs(f"distance_plots/fiting/plane{i}.png")
    