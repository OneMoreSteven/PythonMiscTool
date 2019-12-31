#coding=utf8
import sys
import csv
import numpy as np

ChLine="\n"

class TWFHistoryParser:
    """Authur: Steven Wu
    """
    def __init__(self,SelectedComm,bDayTrade,bParseWeekly):
        self.SelectedComm = SelectedComm
        self.bParseWeekly = bParseWeekly
        self.CurDate = ""
        self.lDate=[]
        self.lOpen=[]
        self.lHigh=[]
        self.lLow=[]
        self.lClose=[]
        self.lVolume=[]
        self.sDayTrade=u"一般"
        self.sNightTrade=u"盤後"
        self.IsSelectedPeriod = self.IsNightTrade
        if bDayTrade:
            self.IsSelectedPeriod = self.IsDayTrade

    def IsDayTrade(self,l):
        if len(l) <= 17:
            return True
        elif (len(l) >= 18) and l[17].decode("big5")==self.sDayTrade:
            return True
        return False

    def IsNightTrade(self,l):
        if (len(l) >= 18) and l[17].decode("big5")==self.sNightTrade:
            return True
        return False

    def IsSelectedComm(self,l):
        if l[1]==self.SelectedComm and l[2].find("/") < 0:
            return True
        return False

    def IsWeekly(self,l):
        return l[2].find("W") >= 0

    def IsNewDate(self,l):
        if l[0]==self.CurDate:
            return False
        self.CurDate = l[0]
        return True

    def ParseFile(self,FileName):
        csvfile = open(FileName,'r')
        csvobj = csv.reader(csvfile)
        bFirstLine = True
        for l in csvobj:
            if bFirstLine:
                bFirstLine = False
                continue
            if not self.IsSelectedPeriod(l):
                continue
            if self.IsWeekly(l) and not self.bParseWeekly:
                continue
            if self.IsSelectedComm(l):
                if self.IsNewDate(l):
                    self.lDate.append(l[0])
                    self.lOpen.append(l[3])
                    self.lHigh.append(l[4])
                    self.lLow.append(l[5])
                    self.lClose.append(l[6])
                    self.lVolume.append(l[9])

    def Output(self,FileName):
        f = open(FileName,'w')
        f.write("Date,Time,Open,High,Low,Close,TotalVolume"+ChLine)
        nLines=len(self.lDate)
        lTime=[]
        for a in xrange(nLines):
            lTime.append("08:46:00")
        l2d=[self.lDate,lTime,self.lOpen,self.lHigh,self.lLow,self.lClose,self.lVolume]
        aLines=np.array(l2d).T
        for a in xrange(nLines):
            f.write((",".join(aLines[a])) + ChLine)


_DataLists = ["lDate","lOpen","lHigh","lLow","lClose","lVolume"]
def Handle2017(P,FirstDay):
    lDate = getattr(P,"lDate")
    FDidx = -1
    for a in range(len(lDate)):
        if lDate[a] == FirstDay:
            FDidx = a
            break
    assert FDidx >= 0
    for l in _DataLists:
        lst = getattr(P,l)
        setattr(P,l,lst[FDidx:])


def MergeToDay(PD,PN):
    #print len(PD.lOpen),len(PN.lOpen)
    if int(PD.lDate[0].split("/")[0]) < 2017:
        print "there is no full day data before 2017"
        exit()
    if PN.lDate[0].find("2017/") == 0:
        Handle2017(PD,PN.lDate[0])

    #print len(PD.lOpen),len(PN.lOpen)
    nData = len(PD.lOpen)
    for a in range(nData):
        """
            if TWF trade on Sat, there would be no night trade this day
            so the next Mon data would lack night trade data
            in this case, use day trade data alone
        """
        if PD.lDate[a] != PN.lDate[a]:
            print "half day detect:",PD.lDate[a],PN.lDate[a]
            for l in _DataLists:
                lst = getattr(PN,l)
                lst.insert(a,"")
            continue
        """
            there is no valid night trade data, it shows '-' like this:
            2017/12/26,UDF,201803,-,-,-,-,-,-,0,-,-,24765,24783,25000,20790,,盤後
        """
        if PN.lOpen[a] == "-":
            print "no night trade data(-):",PN.lDate[a]
            continue
        PD.lOpen[a] = PN.lOpen[a]
        if float(PN.lHigh[a]) > float(PD.lHigh[a]):
            PD.lHigh[a] = PN.lHigh[a]
        if float(PN.lLow[a]) < float(PD.lLow[a]):
            PD.lLow[a] = PN.lLow[a]
        PD.lVolume[a] = str(int(PD.lVolume[a]) + int(PN.lVolume[a]))


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "-f":
        pd=TWFHistoryParser(sys.argv[2],True,False)
        pd.ParseFile(sys.argv[3])
        pn=TWFHistoryParser(sys.argv[2],False,False)
        pn.ParseFile(sys.argv[3])
        """
        pd.Output("day.txt")
        pn.Output("night.txt")
        """
        MergeToDay(pd,pn)
        pd.Output(sys.argv[4])
    if len(sys.argv) == 5 and sys.argv[1] == "-w":
        p=TWFHistoryParser(sys.argv[2],True,True)
        p.ParseFile(sys.argv[3])
        p.Output(sys.argv[4])
    elif len(sys.argv) == 4:
        p=TWFHistoryParser(sys.argv[1],True,False)
        p.ParseFile(sys.argv[2])
        p.Output(sys.argv[3])
    else:
        print "usage:"
        print "    Parse day trade"
        print "     python TWFHistoryParser.py [commodity] [source file] [dest file]"
        print "    Parse full trade"
        print "     python TWFHistoryParser.py -f [commodity] [source file] [dest file]"
