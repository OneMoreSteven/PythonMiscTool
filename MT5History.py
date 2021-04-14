from datetime import datetime
import MetaTrader5 as mt5
import sys
import time
import numpy as np

ChLn = "\n"


def ToDateTime(strTime):
    Y,M,D = [int(x) for x in strTime.split("/")]
    return datetime(Y,M,D)

if __name__ == "__main__":
    strComm,strDateB,strDateE,strOutFile = sys.argv[1:]
    # connect to MetaTrader 5
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        sys.exit()
    
    f = open(strOutFile,"w")
    f.write("Date,Time,Open,High,Low,Close,Volume" + ChLn)
    his = mt5.copy_rates_range(strComm, mt5.TIMEFRAME_D1, ToDateTime(strDateB), ToDateTime(strDateE))
    for l in his:
        t = time.localtime(l[0])
        listLine = ["%4d/%02d/%02d"%(t.tm_year,t.tm_mon,t.tm_mday),"%02d:%02d:%02d"%(t.tm_hour,t.tm_min,t.tm_sec)]
        #listLine += [str(x) for x in l[1:6]]
        listLine += [x.strip() for x in str(l).split(",")[1:6]]
        f.write(",".join(listLine) + ChLn)
    f.close()

