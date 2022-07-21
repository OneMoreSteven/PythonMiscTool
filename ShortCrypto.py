"""
    Author: Steven Wu
    This is used only for short content and you don't want to increase its length
    not safe enough
    ex:
        c = ShortCrypt("key")
        print(c.encrypt(b"my secret"))
"""

import hashlib



class ShortCrypt:
    blk_size = 32
    def __init__(self,key):
        self.key = key.decode("ascii") if type(key) == bytes else key
    def GetHash(self,length):
        if length == 0: return b""
        count = (length-1)//self.blk_size + 1
        hash = b""
        for a in range(count):
            hash += hashlib.sha256((self.key + str(a)).encode("ascii")).digest()
        return hash[:length]
    def encrypt(self,input):
        l = len(input)
        if l == 0: return b""
        input = input.encode("ascii") if type(input) == str else input
        out = bytearray()
        buf,hbuf = input,self.GetHash(l)
        for a in range(l):
            out.append(buf[a] ^ hbuf[a])
        return bytes(out)
    def decrypt(self,input):
        return self.encrypt(input)


def new(key):
    return ShortCrypt(key)

