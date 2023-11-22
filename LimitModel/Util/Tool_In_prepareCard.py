from collections import OrderedDict
def getbinProcRate(ttcdict):
    #print ("inside getbinProcRate", ttcdict)
    
    
    
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
def Get_BinProcRate(DataCards_Input):
    '''
    Take the columns(list) "bin","process","rate", and "process1" of DataCards input 
    '''

    DataCards_Input_prime = OrderedDict()

    reg = str(DataCards_Input['bin'].keys()[0]) # transform the string in json form to python form string. 
    
    n = DataCards_Input['bin'][reg] 

    process = []
    for p in DataCards_Input['Process']:
        process.append(str(p))

    process1 = DataCards_Input['process1']

    rates = DataCards_Input['rate']

    DataCards_Input_prime['bin'] = [reg] * n
    DataCards_Input_prime['process'] = process
    DataCards_Input_prime['process1'] = process1
    DataCards_Input_prime['rate'] = rates


    return (DataCards_Input_prime)




def getUpperPart2(reg,year,signal_process_name='ttc'):
    ## old version to be kept
    #top_= 'shapes * '+reg+' ttc_'+year+'_WS.root ws_ttc_'+cat+'_'+year+':ttc2017_'+cat+'_'+reg+'_$PROCESS ws_ttc_'+cat+'_'+year+':ttc2017_'+cat+'_'+reg+'_$PROCESS_$SYSTEMATIC'+'\n'
    ###top_= 'shapes * '+reg+' inputs/COUPLINGVALUE/TMVApp_MASSPOINT_CHANNELNAME.root ttc2017_$PROCESS ttc2017_$PROCESS_$SYSTEMATIC'+'\n'
    ###top_= 'shapes * '+reg+' inputs/'+year+'/COUPLINGVALUE/TMVApp_MASSPOINT_CHANNELNAME.root ttc'+year+'_$PROCESS ttc'+year+'_$PROCESS_$SYSTEMATIC'+'\n'
    top_= 'shapes * '+reg+' FinalInputs/'+year+'/SIGNALPROCESS_a_COUPLINGVALUE_MAMASSPOINT/TMVApp_MASSPOINT_CHANNELNAME.root ttc'+year+'_$PROCESS ttc'+year+'_$PROCESS_$SYSTEMATIC'+'\n'
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

def Get_ProcSyst(DataCards_Input,nuisance_ordered_list):
    '''
    Take the columns(list) "bin","process","rate", and "process1" of DataCards input 
    '''

    DataCards_Input_prime = OrderedDict()

    NuisForProc = DataCards_Input['NuisForProc']
    uncertainties  = DataCards_Input['UnclnN']
    procs   = DataCards_Input['Process']
    
    
    for idx , unc_row in enumerate(uncertainties): #unc_row -> "fakeYEAR":1.3
        nuis = str(nuisance_ordered_list[str(idx)])
        nuis = nuis.split('_')[-1]
        syst = str(uncertainties[nuis])
        values=[]
        if syst=='shape': values.append('shape')
        else:values.append('lnN')

        for proc in procs : 
            
            if proc in (NuisForProc[nuis]):
                #print(proc) 
                if syst=='shape':
                    values.append(1)
                else:values.append(syst)
            else:values.append('-')
        DataCards_Input_prime[nuis] = values
    #print(DataCards_Input_prime)
    #print(uncertainties)
    return DataCards_Input_prime


    
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

