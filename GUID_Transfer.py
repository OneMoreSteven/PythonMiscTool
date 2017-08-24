"""
this tool convert GUID from registry form into cpp form

ex:
D:\>python GUID_Transfer.py MyGUID {187AEC20-70DB-404B-95BE-9DFC635855A8}

output:
static const GUID MyGUID =
{ 0x187AEC20, 0x70DB, 0x404B,{0x95,0xBE,0x9D,0xFC,0x63,0x58,0x55,0xA8} };

"""


import re
import sys

_Template_GUID_CPP="""
static const GUID %s =
{ 0x%s, 0x%s, 0x%s,{%s} };
"""


def TransferGUID(VarName,guid):
    sguid=re.split("[-{}]",guid)
    sguid=filter(None,sguid)
    
    mlp=sguid[3]+sguid[4]
    lp=""
    for a in range(0,len(mlp),2):
        lp+="0x%s,"%mlp[a:a+2]
    lp=lp[:-1]
    return _Template_GUID_CPP%(VarName,sguid[0],sguid[1],sguid[2],lp)


if __name__ == "__main__":
    print TransferGUID(sys.argv[1],sys.argv[2])