from OverlappingPlots import *



dirname='/afs/cern.ch/user/g/gkole/work/public/forTTC/BDT_output/2018/ttc_a_rtc04_MA300/'
#dirname= '/afs/cern.ch/user/m/melu/public/For_Raman/2018/rtc04/'
histoname1= ['ttc2018_TTTo1L', 'ttc2018_ttWtoLNu','ttc2018_ttZ','ttc2018_TAToTTQ_rtc04_MA300']
os.system("mkdir plots_limit_comp")

files=[dirname+'/TMVApp_300_ee.root']
legend=[ 'tt1L','ttWLnu','ttZ','SigmA350']
xtitle='BDT discriminant'
ytitle='# of events '
axistitle = [xtitle, ytitle]
DrawOverlap(files,histoname1,axistitle,legend,"sig_bkg_somparison_ee_2018",[0,0],[-1,1], legendheader="Yield Comparison ee") 
