python prepareCards.py -y 2016apv -c em -reg 'SR_em' --For template
python prepareCards.py -y 2016apv -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2016apv -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2016apv -c C  --For template 

python prepareCards.py -y 2016postapv -c em -reg 'SR_em' --For template
python prepareCards.py -y 2016postapv -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2016postapv -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2016postapv -c C  --For template 


python prepareCards.py -y 2017 -c em -reg 'SR_em' --For template
python prepareCards.py -y 2017 -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2017 -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2017 -c C  --For template 

python prepareCards.py -y 2018 -c em -reg 'SR_em' --For template
python prepareCards.py -y 2018 -c ee -reg 'SR_ee' --For template
python prepareCards.py -y 2018 -c mm -reg 'SR_mm' --For template
python prepareCards.py -y 2018 -c C  --For template 

python prepareCards.py -y run2 -c C --For template  
python prepareCards.py -y run2 -c em -reg 'SR_em' --For template 
python prepareCards.py -y run2 -c ee -reg 'SR_ee' --For template 
python prepareCards.py -y run2 -c mm -reg 'SR_mm' --For template

for ERA in 2016apv 2016postapv 2017 2018 run2 
do  
  for coupling in ${1}0p1 ${1}0p4 ${1}0p8 ${1}1p0
  do
    for CHANNEL in ee em mm
    do
      python prepareCards.py -y $ERA -c $CHANNEL -reg \'SR_$CHANNEL\' --For specific --coupling_value $coupling --Masses 200 300 350 400 500 600 700 800 900 1000 --scale
      python prepareCards.py -y $ERA -c $CHANNEL -reg \'SR_$CHANNEL\' --For specific --coupling_value $coupling --Masses 250 300 350 400 550 700 800 900 1000 --scale --interference
    done
    python prepareCards.py -y $ERA -c C --For specific --coupling_value $coupling --Masses 200 300 350 400 500 600 700 800 900 1000 --scale
    python prepareCards.py -y $ERA -c C --For specific --coupling_value $coupling --Masses 250 300 350 400 550 700 800 900 1000 --scale --interference

  done
done 


