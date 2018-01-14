import re



ChLine = "\n"

def DecoExternC(f):
    def myf(self):
        t = f(self)
        return 'extern "C" {%s%s%s}'%('\n',t,'\n')
    return myf


class OLEItf_Parser:
    class Func:
        def __init__(self,name):
            self.dispid = -1
            self.name = name
            self.ReturnType = ""
            self.params = []

    class ClassData:
        def __init__(self,name):
            self.name = name
            self.listFunc = []


    def __init__(self):
        self.dictClasses = {}


    def HandleFunction(self,ItfDesc,Head,Params):
        phead = Head.rsplit(" ",1)
        Fun = self.Func(phead[1])
        Fun.ReturnType = phead[0].strip()

        pdid = re.findall("id\((.*?)\)",ItfDesc)
        Fun.dispid = int(pdid[0],16)

        pparam = filter(None,Params.split(","))
        for p in pparam:
            p = re.sub("\[.*?\]","",p)
            Fun.params.append(p.strip())

        return Fun


    def FindMethodBlock(self,content):
        sch = re.search("\smethods\s*:",content)
        e=sch.end()
        sMethodBlock =  content[e:]
        sch = re.search("\sproperties\s*:",sMethodBlock)
        if sch != None:
            sMethodBlock = sMethodBlock[:sch.start()]
        return sMethodBlock


    def HandleInterface(self,sItfName,content):
        c = self.ClassData(sItfName)

        sMethodBlock = self.FindMethodBlock(content)

        fa=re.findall("\[(.*?)\](.*?)\((.*?)\)",sMethodBlock,re.DOTALL)
        for fun in fa:
            rf = self.HandleFunction(fun[0],fun[1],fun[2])
            c.listFunc.append(rf)

        return c


    def Parse(self,sCppContent):
        f=re.findall("dispinterface\s+(\S*)\s*{(.*?)}",sCppContent,re.DOTALL)
        for c in f:
            sItfName = c[0]
            cls = self.HandleInterface(sItfName,c[1])
            self.dictClasses[sItfName] = cls

class OLE_Parse(OLEItf_Parser):
    """
Authur: Steven Wu
    1. Inherit and implement IDispEventSimpleImpl
    2. Copy ole interface definition from oleview

    example:
    ole=OLE_Parse()
    s=open("ole.txt","r").read()
    ole.Parse(s)
    print ole.GenSinkMapEx("EvtCls","123")
    print ole.GenFuncInfo()
"""
    def __init__(self):
        OLEItf_Parser.__init__(self)
        self.VarTypeMap = {}
        self.BuildVarTypeMap()

    def Parse(self,sCppContent):
        OLEItf_Parser.Parse(self,sCppContent)

    def BuildVarTypeMap(self):
        self.VarTypeMap["short"] = "VT_I2"
        self.VarTypeMap["long"] = "VT_I4"
        self.VarTypeMap["float"] = "VT_R4"
        self.VarTypeMap["double"] = "VT_R8"
        self.VarTypeMap["BSTR"] = "VT_BSTR"
        self.VarTypeMap["IDispatch*"] = "VT_DISPATCH"
        self.VarTypeMap["BOOL"] = "VT_BOOL"
        self.VarTypeMap["VARIANT"] = "VT_VARIANT"
        self.VarTypeMap["char"] = "VT_I1"
        self.VarTypeMap["unsigned char"] = "VT_UI1"
        self.VarTypeMap["unsigned short"] = "VT_UI2"
        self.VarTypeMap["unsigned long"] = "VT_UI4"
        self.VarTypeMap["long long"] = "VT_I8"
        self.VarTypeMap["unsigned long long"] = "VT_UI8"
        self.VarTypeMap["int"] = "VT_INT"
        self.VarTypeMap["unsigned int"] = "VT_UINT"
        self.VarTypeMap["void"] = "VT_VOID"
        self.VarTypeMap["HRESULT"] = "VT_HRESULT"

        """
{	VT_EMPTY	= 0,
	VT_NULL	= 1,
	VT_CY	= 6,
	VT_DATE	= 7,
	VT_ERROR	= 10,
	VT_UNKNOWN	= 13,
	VT_DECIMAL	= 14,
	VT_PTR	= 26,
	VT_SAFEARRAY	= 27,
	VT_CARRAY	= 28,
	VT_USERDEFINED	= 29,
	VT_LPSTR	= 30,
	VT_LPWSTR	= 31,
	VT_RECORD	= 36,
	VT_INT_PTR	= 37,
	VT_UINT_PTR	= 38,
	VT_FILETIME	= 64,
	VT_BLOB	= 65,
	VT_STREAM	= 66,
	VT_STORAGE	= 67,
	VT_STREAMED_OBJECT	= 68,
	VT_STORED_OBJECT	= 69,
	VT_BLOB_OBJECT	= 70,
	VT_CF	= 71,
	VT_CLSID	= 72,
	VT_VERSIONED_STREAM	= 73,
	VT_BSTR_BLOB	= 0xfff,
	VT_VECTOR	= 0x1000,
	VT_ARRAY	= 0x2000,
	VT_BYREF	= 0x4000,
	VT_RESERVED	= 0x8000,
	VT_ILLEGAL	= 0xffff,
	VT_ILLEGALMASKED	= 0xfff,
	VT_TYPEMASK	= 0xfff
    } ;

        """


    def FunInfoName(self,fn):
        return fn+"_Info"

    def GenSinkMap(self,sClsName,sID):
        "Generate sink map for SINK_ENTRY"
        sRet=""
        for cn in self.dictClasses:
            sClass = "BEGIN_SINK_MAP(%s)%s"%(sClsName,ChLine)
            c = self.dictClasses[cn]
            for f in c.listFunc:
                fn = f.name
                sFunInfoName = self.FunInfoName(fn)
                sClass += "\tSINK_ENTRY(%s, %d, %s)%s"%(sID,f.dispid,f.name,ChLine)
            sClass += "END_SINK_MAP()%s"%(ChLine)
            sRet += sClass
        return sRet

    def GenSinkMapEx(self,sClsName,sID,sIID):
        "Generate sink map for SINK_ENTRY_EX"
        sRet=""
        for cn in self.dictClasses:
            sClass = "BEGIN_SINK_MAP(%s)%s"%(sClsName,ChLine)
            c = self.dictClasses[cn]
            for f in c.listFunc:
                fn = f.name
                sFunInfoName = self.FunInfoName(fn)
                sClass += "\tSINK_ENTRY_EX(%s, %s, %d, %s)%s"%(sID,sIID,f.dispid,f.name,ChLine)
            sClass += "END_SINK_MAP()%s"%(ChLine)
            sRet += sClass
        return sRet

    def GenSinkMapInfo(self,sClsName,sID,sIID):
        "Generate sink map for SINK_ENTRY_INFO"
        sRet=""
        for cn in self.dictClasses:
            sClass = "BEGIN_SINK_MAP(%s)%s"%(sClsName,ChLine)
            c = self.dictClasses[cn]
            for f in c.listFunc:
                fn = f.name
                sFunInfoName = self.FunInfoName(fn)
                sClass += "\tSINK_ENTRY_INFO(%s, %s, %d, %s, &%s)%s"%(sID,sIID,f.dispid,f.name,sFunInfoName,ChLine)
            sClass += "END_SINK_MAP()%s"%(ChLine)
            sRet += sClass
        return sRet

    def GenFuncInfo(self):
        "Generate function info"
        sRet = ""
        for cn in self.dictClasses:
            sRet += "// %s%s"%(cn,ChLine)
            c = self.dictClasses[cn]
            for f in c.listFunc:
                params = []
                for ps in f.params:
                    sps = ps.rsplit(" ",1)
                    sType = sps[0].strip()
                    sMapType = ""
                    try:
                        sMapType = self.VarTypeMap[sType.strip()]
                    except:
                        print "type map failed :", sType
                    params.append(sMapType)
                sParam = "{%s}"%(",".join(params))
                fn = f.name
                sFunInfoName = self.FunInfoName(fn)
                sFunc = "static _ATL_FUNC_INFO %s = {CC_STDCALL, VT_EMPTY, %d, %s};%s"%(sFunInfoName,len(f.params),sParam,ChLine)
                sRet += sFunc
        return sRet
