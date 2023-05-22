unblind="${2:-''}"
for CHANNEL in C ee mm em
do
  for ERA in run2
  do
    for coupling in rtc0p1 rtc0p4 rtc1p0 rtu0p1 rtu0p4 rtu1p0
    do
      python Results_Integrate.py --mode LimitTables --channel $CHANNEL --coupling_value $coupling --year $ERA $1 $unblind
      python Results_Integrate.py --mode LimitTables --channel $CHANNEL --coupling_value $coupling --year $ERA --interference $1 $unblind
    done
  done
done

