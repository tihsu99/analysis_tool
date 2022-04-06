import os
import yaml
import numpy as np
from collections import OrderedDict
import pandas as pd
import sys, optparse,argparse

## ----- command line argument
usage = "python prepareCards.py -y 2017 -c emu -reg ['SR']"
parser = argparse.ArgumentParser(description=usage)
parser.add_argument("-y", "--year", dest="year", default="2017")
parser.add_argument("-m", "--model", dest="model", default="ExY")
parser.add_argument("-c", "--category",  dest="category",default="all")
parser.add_argument("-reg", nargs="+", default=["a", "b"])

args = parser.parse_args()


year     = args.year
category = args.category
regions  = args.reg
modelName = args.model


print (year, category, regions, modelName)

if category=='emu':
    f = open('ttc.yaml')
else:
    print "no category"
    exit 
    
doc = yaml.safe_load(f)


outdir = 'datacards_ttc_'+year
os.system('mkdir '+ outdir)
top_ = '''
imax *  number of channels
jmax *  number of backgrounds

kmax *  number of nuisance parameterS (sources of systematical uncertainties)
'''



def getUpperPart2(reg,cat):
    top_= 'shapes * '+reg+' ttc_'+year+'_WS.root ws_ttc_'+cat+'_'+year+':ttc2017_'+cat+'_'+reg+'_$PROCESS ws_ttc_'+cat+'_'+year+':ttc2017_'+cat+'_'+reg+'_$PROCESS_$SYSTEMATIC'+'\n'
    return top_


def getUpperPart3(reg):
	top_ = 'bin '+reg
	# observation -1
	return top_

def getDic(dics,name):
    return dics[name].keys()[0]

def getSyst(lists):
	syst=OrderedDict()
	# print getDic(lists,'bin')
	reg     = getDic(lists,'bin')[0].split(':')[0]
	length  = int(getDic(lists,'bin')[0].split(':')[1])
	nuis    = getDic(lists,'Nuisances')
	unc     = getDic(lists,'SystUnclnN')
	for n, u in zip(nuis,unc):
		# print 'testing ', n , u
		syst[str(n)]=[u] * length

	return syst




def getProcSyst(lists):
	nuisancesForCard=OrderedDict()
        print ('testing nuisances')
	NuisForProc = lists['NuisForProc']
	uncertainties  = lists['UnclnN']
	procs   = lists['Process']

	# print 'NuisForProc',NuisForProc
	for ij, istring in enumerate(uncertainties):
		nuis = istring.keys()[0]
		syst = istring[nuis]
		# print 'nuis, syst',nuis, syst
		values=[]
		if syst=='shape':  values.append('shape')
		else:values.append('lnN')
		
		for proc in procs:
			# print nuis,NuisForProc[ij]

			if proc in  (NuisForProc[ij])[nuis]:
				if syst=='shape':
					values.append(1)
				else:
					values.append(syst)
			else:values.append('-')
		nuisancesForCard[nuis]=values

	#print ('nuisancesForCard', nuisancesForCard)
	return nuisancesForCard





def getbinProcRate(ttcdict):
    print ("inside getbinProcRate", ttcdict)
    binProcRate = OrderedDict()
    reg     = ttcdict["bin"].keys()[0] 
    length  =  int(ttcdict["bin"][reg])
    
    process   = ttcdict['Process']
    process1  = ttcdict['process1']
    rates = ttcdict['rate']          ## rate = [int(i) for i in ttcdict['rate'][0].split(",")]  ## when all are in the same line, instead of one rate in one line 
    
    binProcRate['bin']      =  [reg] * length
    binProcRate['process']  =  process
    binProcRate['process1'] =  process1
    binProcRate['rate']     = rates
    return binProcRate
    
def getProcRate(lists):
    binProcRate = OrderedDict()
    reg     = getDic(lists,'bin')[0].split(':')[0]
    length  = int(getDic(lists,'bin')[0].split(':')[1])
    procs   = getDic(lists,'Process')
    procs1  = getDic(lists,'process1')
    rates =  getDic(lists,'rate')
    
    
    # binProcRate['bin']      =  [reg] * length
    # binProcRate['process']  =  procs
    binProcRate['process'] =  procs1
    binProcRate['rate']     = rates
    # print 'binProcRate', binProcRate
    
    # print (lists['rateTest'])
    
    return binProcRate


'''
=======================
START WRITING DATACARDS
=======================
'''
print (regions)

for reg in regions:
    outputfile = 'ttc_datacard_'+year+'_'+reg+'_'+category+'_template.txt'
    print (doc[reg])
    df0 = pd.DataFrame(getbinProcRate(doc[reg]))
    print (df0)
    
    #df1 = pd.DataFrame(getProcRate(doc[reg]))
    #df0['process'] = df0['process'].replace(['signal'],sigHist)
    # df =  pd.DataFrame(getSyst(doc))
    df1 =  pd.DataFrame(getProcSyst(doc[reg]))
    print (df1)
    
    #df = pd.merge(df0,df1)
    fout = open(outdir+'/'+outputfile,'w')
    p0 = df0.T.to_string(justify='right',index=True, header=False)
    p1 = df1.T.to_string(justify='right',index=True, header=False)
    
    part1 = top_
    part2 = getUpperPart2(reg,category)
    part3 = getUpperPart3(reg)
    #part4 = getEndPart(reg)
    
    fout.write(part1+'\n')
    fout.write('------------'+'\n')
    fout.write(part2+'\n')
    fout.write('------------'+'\n')
    fout.write(part3+'\n')
    fout.write('observation -1'+'\n')
    fout.write('------------'+'\n')
    
 
    fout.write(p0+'\n')
    fout.write(p1+'\n')
    # fout.write(p1+'\n')
    '''
    fout.write('------------'+'\n')
    fout.write(p+'\n')
    fout.write(part4+'\n')
    '''
    fout.close()

#os.system("sed -i'.bak' 's/process1/process /g' "+outdir+"/*")
#os.system("sed -i'.bak' 's/YEAR/"+year+"/g' "+outdir+"/*")
#os.system("rm -rf "+outdir+"/*bak")


'''
iregion=[]

#allregions.append(rl.TextFileToList(iregion))		 

modelRename =''

if modelName == 'THDMa' :
    modelRename = '2hdma'


monohbb_file='monohbb'+year+'_datacardslist_'+category+'_'+'allregion_'+modelName+'_all.txt'
monohbb_file_SR='monohbb'+year+'_datacardslist_'+category+'_'+'SR_'+modelName+'_all.txt'
#monohbb_file='monohbb'+year+'_datacardslist_'+category+'_'+modelName+'_all.txt'

#monoHbb2017_R_SR_ggF_sp_0p8_tb_1p0_mXd_10_mA_600_ma_200



ftxt = open(monohbb_file,'w')
ftxt_SR= open(monohbb_file_SR,'w')
for sigHist in getSignalHists(signalDoc,modelName):
    outfile_SR = 'monoHbb'+year+'_'+category+'_SR_'+sigHist
    srfile = 'ttc_datacard_'+year+'_SR_'+category+'_'+sigHist+'.txt'
    outfile= 'ttc_datacard_'+year+'_'+modelName+'_'+category+'_allregion_'+sigHist+'.txt'
    # os.system('combineCards.py sr='+outdir+'/'+srfile+' zee='+outdir+'/ttc_datacard_2017_ZEE_R.txt  zmumu='+outdir+'/ttc_datacard_2017_ZMUMU_R.txt wmu='+outdir+'/ttc_datacard_2017_WMU_R.txt we='+outdir+'/ttc_datacard_2017_WE_R.txt topmu='+outdir+'/ttc_datacard_2017_TOPMU_R.txt tope='+outdir+'/ttc_datacard_2017_TOPE_R.txt >'+outdir+'/'+outfile)
    os.system('combineCards.py sr='+outdir+'/'+srfile+' zee='+outdir+'/ttc_datacard_2017_ZEE_'+category+'.txt  zmumu='+outdir+'/ttc_datacard_2017_ZMUMU_'+category+'.txt topmu='+outdir+'/ttc_datacard_2017_TOPMU_'+category+'.txt tope='+outdir+'/ttc_datacard_2017_TOPE_'+category+'.txt >'+outdir+'/'+outfile)
    ftxt.write(outdir+'/'+outfile+' \n')
    ftxt_SR.write(outfile_SR+'\n')
    
ftxt.close()
ftxt_SR.close()
    
#print(iregion)


    
'''
