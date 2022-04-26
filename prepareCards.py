import os
import yaml
import numpy as np
from collections import OrderedDict
import pandas as pd
import sys, optparse,argparse

## ----- command line argument
usage = "python prepareCards.py -y 2017 -c em -reg 'SR_em'"
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


print (year)#, category, regions, modelName)

if category=='em' or category=='ee' or category=='mm':
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
    ## old version to be kept
    #top_= 'shapes * '+reg+' ttc_'+year+'_WS.root ws_ttc_'+cat+'_'+year+':ttc2017_'+cat+'_'+reg+'_$PROCESS ws_ttc_'+cat+'_'+year+':ttc2017_'+cat+'_'+reg+'_$PROCESS_$SYSTEMATIC'+'\n'
    top_= 'shapes * '+reg+' inputs/TMVApp_MASSPOINT_CHANNELNAME.root ttc2017_$PROCESS ttc2017_$PROCESS_$SYSTEMATIC'+'\n'
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
    
    print ("reg:",reg)
    print (doc[reg])
    df0 = pd.DataFrame(getbinProcRate(doc[reg]))
    df0 = df0.rename(columns={"process1":"process"})   ## replacing process1 by process
    print (df0)
    
    df1 =  pd.DataFrame(getProcSyst(doc[reg]))
    print (df1)
    
    fout = open(outdir+'/'+outputfile,'w')
    p0 = df0.T.to_string(justify='right',index=True, header=False)
    p1 = df1.T.to_string(justify='right',index=True, header=False)
    
    part1 = top_
    part2 = getUpperPart2(reg,category)
    part2 = part2.replace("CHANNELNAME",category)
    print ("part2: ",part2)
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




'''
[khurana@lxplus752 LimitModel]$ combineCards.py mm=datacards_ttc_2017/ttc_datacard_2017_SR_mm_mm_template.txt ee=datacards_ttc_2017/ttc_datacard_2017_SR_ee_ee_template.txt em=datacards_ttc_2017/ttc_datacard_2017_SR_em_em_template.txt > combo.txt
'''
