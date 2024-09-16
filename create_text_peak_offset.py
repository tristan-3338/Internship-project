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
qf_values=[]
qb_values=[]

n_entries = tree.GetEntries() #number of events
N_events = 4
n_plots = 4

rows = 4  # number of planes
cols = 16  # number of strips

# Créer un tableau 2D de dimensions rows x cols initialisé à 0
coordonate_detector = [[[[]for _ in range(2)] for _ in range(cols)] for _ in range(rows)]
#print(coordonate_detector)

n_qf_zero =0
n_qb_zero =0
n_qb_qf_zero=0

for i_event in range(n_entries): #loops all tree events
    tree.GetEntry(i_event) #gets variables for each events

    trigger = tree.trigger
    plane_list =list(tree.plane)
    strip_list=list(tree.strip)
    qf_list =list(tree.QF)
    qb_list = list(tree.QB)

    #qf_number_values =[] #contient une liste de valeurs de qf et combien de hits associé aux mêmes coordonées
    
    if trigger==1:
        #print("plane = ",plane_list)
        #print("strip = ",strip_list)
        #print("qf = ", qf_list)
        for k in range(len(plane_list)):
            if abs(qf_list[k]-qb_list[k]) < 100:
            #if qf_list[k]!=0 and qb_list[k]!=0:
            #print("coordonée avant = ",coordonate_detector[plane_list[k]][strip_list[k]])
                if not coordonate_detector[plane_list[k]][strip_list[k]][0]: #si rien détecté aux coordonnées indiquées auparavant
                    
                    coordonate_detector[plane_list[k]][strip_list[k]][0].append([1,qf_list[k]])
                
                if not coordonate_detector[plane_list[k]][strip_list[k]][1]: #si rien détecté aux coordonnées indiquées auparavant
                    coordonate_detector[plane_list[k]][strip_list[k]][1].append([1,qb_list[k]])

                else:
                    search_qf=False
                    search_qb=False
                    for j in coordonate_detector[plane_list[k]][strip_list[k]][0]:
                        if qf_list[k] == j[1]:
                            j[0] += 1
                            search_qf=True
                            break
                    for j in coordonate_detector[plane_list[k]][strip_list[k]][1]:
                        if qb_list[k] == j[1]:
                            j[0] += 1
                            search_qb=True
                            break
                    if search_qf==False:
                        coordonate_detector[plane_list[k]][strip_list[k]][0].append([1,qf_list[k]])
                    if search_qb==False:
                        coordonate_detector[plane_list[k]][strip_list[k]][1].append([1,qb_list[k]])
                #print("coordonée après = ",coordonate_detector[plane_list[k]][strip_list[k]])

# Remplir les histogramme avec les données
#histograms = []
"""lines_plane=[]"""
most_probable_charge=[[[]for _ in range(16)]for _ in range(4)]
for i in range(4):
    #histogram = [[]for _ in range(16)]
    
    for k in range(16):
        
        #max_particles = max(number[0] for number in coordonate_detector[i][k])
        c = TCanvas("c", "c")
        c.Divide(2,1)
        hist_qf = TH1F(f"plane{i}_strip{k}_qf", ";Charge QF;Hits",2900, -10, 200)
        hist_qb = TH1F(f"plane{i}_strip{k}_qb", ";Charge QF;Hits",2900, -10, 200)
        for l in coordonate_detector[i][k][0]:
            #print(l)
            hist_qf.Fill(l[1],l[0])
        for l in coordonate_detector[i][k][1]:
            hist_qb.Fill(l[1],l[0])

        """c.cd(1)
        hist_qf.Draw()
        c.cd(2)
        hist_qb.Draw()
        c.SaveAs(f"plots_charge_with_charge_zero/charge_zero_appear/plane{i}_strip{k}.png")
"""
        hist_qf.GetXaxis().SetRangeUser(-10,300)
        hist_qb.GetXaxis().SetRangeUser(-10,300)

        max_bin_qf = hist_qf.GetMaximumBin()
        max_bin_qb = hist_qb.GetMaximumBin()
        most_probable_charge_qf = hist_qf.GetBinCenter(max_bin_qf) 
        most_probable_charge_qb = hist_qb.GetBinCenter(max_bin_qb) 

        most_probable_charge[i][k].append(most_probable_charge_qf)
        most_probable_charge[i][k].append(most_probable_charge_qb)


with open('data2.txt','w') as file:
    for row in most_probable_charge:
        for element in row:
            file.write(f"{element}\n")