import sys
import time


def GetTradeDateTime(year,month,day):
	return time.mktime((year,month,day,0,0,0,0,0,-1))

def TranTradeTime(sLine):
	YMD = sLine.split(",")[0].split("/")
	return GetTradeDateTime(int(YMD[0]),int(YMD[1]),int(YMD[2]))

if __name__ == "__main__":
	if len(sys.argv) == 1:
		print "usage:"
		print "  python ConcatenateHistory.py [base file] [new file]"
		exit()

	base_file_lines = open(sys.argv[1]).readlines()
	new_file_lines = open(sys.argv[2]).readlines()

	new_file_start_time = TranTradeTime(new_file_lines[1])

	nBaseFileLines = len(base_file_lines)
	for n in range(nBaseFileLines-1,-1,-1):
		TradeTime = TranTradeTime(base_file_lines[n])
		if TradeTime < new_file_start_time:
			del base_file_lines[n+1:]
			base_file_lines.extend(new_file_lines[1:])
			break
	open(sys.argv[1],"w").writelines(base_file_lines)
