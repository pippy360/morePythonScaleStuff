import imagehash as ih
from imagehash import ImageHash

def getHash(fragmentImage):
    from PIL import Image
    pythonImageObj = Image.fromarray(fragmentImage.fragmentImage)
    return ih.dhash(pythonImageObj)

def strHashToHashObj(strHash):
    return hex_to_hash(strHash)

def hex_to_hash(hexstr):
    if isinstance(hexstr, ImageHash):
        hexstr = str(hexstr)
            
    l = []

    if len(hexstr) != 8:
        raise ValueError('The hex string has the wrong length')
    for i in range(4):
        h = hexstr[i*2:i*2+2]
        v = int("0x" + h, 16)
        l.append([v & 2**i > 0 for i in range(8)])
    return ImageHash(np.array(l))

    