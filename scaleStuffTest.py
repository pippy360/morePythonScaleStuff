import cv2
import numpy as np
import basicImageOperations as BIO


def main(name):
  img = cv2.imread("./upload02.jpg")
  img = BIO.getTheGreenPointsImage_easy(img)

  cv2.imshow('cornerTest_.jpg',img)
  if cv2.waitKey(0) & 0xff == 27:
      cv2.destroyAllWindows()
#  filename = name
#  img = cv2.imread(filename)
#  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#
#  junk,g2mask = cv2.threshold(gray,125,255,cv2.THRESH_BINARY)
#
#  cv2.imwrite('cornerTest_'+name+'.jpg',g2mask)
#  #if cv2.waitKey(0) & 0xff == 27:
#  #    cv2.destroyAllWindows()
  


#  gray = np.float32(gray)
#  dst = cv2.cornerHarris(gray,2,3,0.04)
#
#  #result is dilated for marking the corners, not important
#  dst = cv2.dilate(dst,None)
#
#  # Threshold for an optimal value, it may vary depending on the image.
#  img[dst>0.01*dst.max()]=[0,0,255]
#

main("extreme.jpg")
