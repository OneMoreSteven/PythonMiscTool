#coding=utf8
import sys
import csv
import numpy as np

ChLine="\r\n"

class TWFHistoryParser:
    """Authur: Steven Wu
    """
    def __init__(self,SelectedComm):
        self.SelectedComm = SelectedComm
        self.CurDate = ""
        self.lDate=[]
        self.lOpen=[]
        self.lHigh=[]
        self.lLow=[]
        self.lClose=[]
        self.lVolume=[]
        self.sDayTrade=u"一般"
        self.sNightTrade=u"盤後"

    def IsDayTrade(self,l):
        if len(l) == 17:
            return True
        elif (len(l) == 18 or len(l) == 19) and l[17].decode("big5")==self.sDayTrade:
            return True
        return False


    def IsSelectedComm(self,l):
        if l[1]==self.SelectedComm and len(l[2])<=6:
            return True
        return False

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
            if not self.IsDayTrade(l):
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



if __name__ == "__main__":
    p=TWFHistoryParser(sys.argv[1])
    p.ParseFile(sys.argv[2])
    p.Output(sys.argv[3])
