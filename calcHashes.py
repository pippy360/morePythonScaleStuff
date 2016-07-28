from PIL import Image
import imagehash as ih

hash1 = ih.average_hash(Image.open('output_extreme.jpg'))
print "hash"
print hash1

hash2 = ih.average_hash(Image.open('output_testImage1.jpg'))
print "hash"
print hash2

hash3 = ih.average_hash(Image.open('orginalFrag_testImage2.jpg'))
print "hash"
print hash3

hash4 = ih.average_hash(Image.open('g.jpg'))
print "hash"
print hash3


print "hash1 - hash2"
print hash1 - hash2
print "hash1 - hash3"
print hash1 - hash3

print "hash2 - hash1"
print hash2 - hash1
print "hash2 - hash3"
print hash2 - hash3

print "hash3 - hash1"
print hash3 - hash1
print "hash3 - hash2"
print hash3 - hash2

print "hash1 - hash4"
print hash1 - hash4

print "hash2 - hash4"
print hash2 - hash4

print "hash3 - hash4"
print hash3 - hash4

