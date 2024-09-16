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

plane_values=[]
strip_values=[]
qf_values=[]
qb_values=[]

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
        qf_values.append(tf_list)
        qb_values.append(tb_list)

histograms_1 =[]
for plane in range(4):
    for strip in range(16):
        h = TH1F(f"plane{plane} strip{strip}","(QF-QB); number", 450, -450,450)
        histograms_1.append(h)
for i in range(len(qf_values)):
    for k in range(len(qf_values[i])):
        diff = (qf_values[i][k] - qb_values[i][k])
        histograms_1[plane_values[i][k]*16 + strip_values[i][k]].Fill(diff)

for i,hist in enumerate(histograms_1):
    canva = TCanvas("c","c")
    canva.SetLogy()
    hist.Draw()
    canva.Update()
    plane_i = i//16
    strip_i = i%16
    canva.SaveAs(f"plots_without_calibration/check_diff/plane{plane_i}_strip{strip_i}.png")