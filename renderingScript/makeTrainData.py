import cv2

#tempImage = '../../Data/LegoPiecesBlender/assembly1/assembly1_1.png'

#Crop an image to its bounding box
def cropToBoundingBox(imagePath):
  print(imagePath)
  img = cv2.imread(imagePath,cv2.IMREAD_UNCHANGED)
  #Use the alpha channel as a mask
  threshold = img[:,:,3]
  #Get the bounding box
  min_rec = cv2.boundingRect(threshold)
  #Crop the picture
  img = img[min_rec[1]:min_rec[1]+min_rec[3],min_rec[0]:min_rec[0]+min_rec[2]]
  #Save it
  cv2.imwrite(imagePath,img)
  #cv2.rectangle(img,(min_rec[0],min_rec[1]),(min_rec[0]+min_rec[2],min_rec[1]+min_rec[3]),(0,255,0),2)
  #cv2.imshow('image',img)
  #cv2.waitKey(0)
  
#cropToBoundingBox(tempImage)
