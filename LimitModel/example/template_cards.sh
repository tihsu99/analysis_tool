python Init.py --year 2017 --channel all
python Init.py --year 2018 --channel all
python Init.py --year 2016apv --channel all
python Init.py --year 2016postapv --channel all

#template
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
python prepareCards.py -y run2 -c ee --For template
python prepareCards.py -y run2 -c em --For template
python prepareCards.py -y run2 -c mm --For template

