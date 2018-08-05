#coding=utf8
"""
Authur: Steven Wu

"""


import sys
import re
from operator import itemgetter

class InvestingComParser:
    def __init__(self):
        self.ChLine = "\r\n"
        self.sEnterDataBlock = "Download Data"
        self.sLeaveDataBlock = "Highest:"
        self.sIgnoreBlockHead = "Date"
        self.mapMonth = {}
        self.mapMonth["Jan"] = 1
        self.mapMonth["Feb"] = 2
        self.mapMonth["Mar"] = 3
        self.mapMonth["Apr"] = 4
        self.mapMonth["May"] = 5
        self.mapMonth["Jun"] = 6
        self.mapMonth["Jul"] = 7
        self.mapMonth["Aug"] = 8
        self.mapMonth["Sep"] = 9
        self.mapMonth["Oct"] = 10
        self.mapMonth["Nov"] = 11
        self.mapMonth["Dec"] = 12


    def OutDayString(self,year,month,date):
        return "%04d/%02d/%02d"%(year,month,date)

    def ParseDate(self,ds):
        s = filter(None,re.split("[ ,]",ds))
        if len(s) != 3:
            return ""
        return self.OutDayString(int(s[2]),int(self.mapMonth[s[0]]),int(s[1]))

    def ParseVol(self,vs):
        s = filter(None,re.split("[ K]",vs))
        return str(int(float(s[0])*1000))

    def ParseFloat(self,fs):
        s=fs.split(",")
        return "".join(s).strip()

    def ParseLine(self,line):
        s = line.split("\t")
        if len(s) != 7:
            return
        if s[0].strip() == self.sIgnoreBlockHead:
            return
        if s[5].strip() == "-":
            return
        data=[]
        data.append(self.ParseDate(s[0])) #Date
        data.append(self.ParseFloat(s[2])) #Open
        data.append(self.ParseFloat(s[3])) #High
        data.append(self.ParseFloat(s[4])) #Low
        data.append(self.ParseFloat(s[1])) #Close
        data.append(self.ParseVol(s[5])) #Volume
        return data


    def ParseLines(self,lines):
        bParsed = False
        bDataRegion = False
        listData = []
        for l in lines:
            if (not bParsed) and (not bDataRegion) and l.strip().find(self.sEnterDataBlock) == 0:
                bDataRegion = True
            elif bDataRegion:
                if l.find(self.sLeaveDataBlock) == 0:
                    bDataRegion = False
                    bParsed = True
                else:
                        data = self.ParseLine(l)
                        if data != None:
                            listData.append(data)

        listData = sorted(listData,key=itemgetter(0))
        out="Date,Open,High,Low,Close,Volume" + self.ChLine
        for d in listData:
            s = ",".join(d) + self.ChLine
            out += s
        return out

class InvestingComCNParser(InvestingComParser):
    def __init__(self):
        InvestingComParser.__init__(self)
        self.sEnterDataBlock = "下载数据"
        self.sLeaveDataBlock = "最高:"
        self.sIgnoreBlockHead = "日期"
    def ParseDate(self,ds):
        s = filter(None,re.split("[年月日]",ds))
        if len(s) != 3:
            return ""
        return self.OutDayString(int(s[0]),int(s[1]),int(s[2]))



if __name__ == "__main__":
    pl = len(sys.argv)
    if pl < 3:
        print "usage: [python] InvestingComParser (Investing com page txt file) (output file) [-cn]"
        print "Options:"
        print "         -cn : use file from China(.cn) site"
    else:
        source = sys.argv[1]
        dest = sys.argv[2]
        parser = InvestingComParser()
        if pl == 4:
            if sys.argv[3] == "-cn":
                parser = InvestingComCNParser()
        out = parser.ParseLines(open(source,"r").readlines())
        open(dest,"w").write(out)

