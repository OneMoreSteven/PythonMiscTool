
import sys

ChLine="\n"

if __name__ == "__main__":
	fname = sys.argv[1]
	lines = open(fname,"r").readlines()
	outf = open(fname,"w")
	for l in lines:
		l = l.strip()
		if l != "":
			outf.write(l+ChLine)
	outf.close()
