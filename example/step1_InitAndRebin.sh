python Init.py --year 2017 --channel all
python Init.py --year 2018 --channel all
python Init.py --year 2016apv --channel all
python Init.py --year 2016postapv --channel all

unblind=$2

for Era in 2016apv 2016postapv 2017 2018
do 
  for coupling in 0p4
  do
    for coupling_name in rtc rtu
    do
      python ReBin.py -c all --Couplings $coupling --Coupling_Name $coupling_name --y $Era --Masses 200 300 350 400 500 600 700 800 900 1000 --inputdir $1 $unblind;
      python ReBin.py -c all --Couplings $coupling --Coupling_Name $coupling_name --y $Era --Masses 250 300 350 400 550 700 800 900 1000 --inputdir $1 --interference $unblind;
    done
  done
done

 
