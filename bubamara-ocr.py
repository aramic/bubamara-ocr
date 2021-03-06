# -*- coding: utf-8 -*-

import argparse
import os
import numpy as np
import cv2
#np.set_printoptions(threshold=999999)

abeceda = ['A', 'B', 'C', 'Č', 'Ć', 'D', 'DŽ', 'Đ', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'LJ', 'M', 'N', 'NJ', 'O', 'P', 'R', 'S', 'Š', 'T', 'U', 'V', 'Z', 'Ž']
imgTrain = 'calibration/tablet.jpg'

#pixel size for input image:
xPixels = 100L
yPixels = 100L

def bubamaraGen(trainImage, testImage):

  # Set up the training image.
  # It is an alphabetical tablet of ladybugs.
  trainImage = cv2.imread(trainImage)
  bubamara = cv2.cvtColor(trainImage,cv2.COLOR_BGR2GRAY)

  img2 = cv2.imread(testImage)
  input_name = os.path.basename(testImage)

  input_img = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
  # Make the input image the same size as the training image.
  # input_img = cv2.resize(input_img, (bubamara.shape[0],bubamara.shape[1]), interpolation = cv2.INTER_AREA)

  #compute size of input image:
  print "inputImage Size: " + str(input_img.shape[0]) + "x" + str(input_img.shape[1])
  
  #now figure out how many 30x30 boxes fill the image & crop to that size:
  xCount = input_img.shape[0] / xPixels
  yCount = input_img.shape[1] / yPixels

  input_img = input_img[0:xCount*xPixels, 0:yCount*yPixels] # Crop from x, y, w, h -> 100, 200, 300, 400
                                   # NOTE: its img[y: y + h, x: x + w] and *not* img[x: x + w, y: y + h]
  
  print "inputImage New Size: " + str(input_img.shape[0]) + "x" + str(input_img.shape[1])

  # Now we split the images to 30 cells, each 100x100 in size. (6x5 grid)
  # 30 corresponds to each letter of the Bosnian-Serbian-Croatian alphabet.
  bubamara_cells = [np.hsplit(row,6) for row in np.vsplit(bubamara,5)]
  input_img_cells = [np.hsplit(row,yCount) for row in np.vsplit(input_img,xCount)]

  print "Array Count: " + str(xCount) + "," + str(yCount)
  print str(xCount * yCount) + " letters"

  # Make both into Numpy arrays. Their sizes will be (5,6,100,100)
  # Total area: 300000
  x1 = np.array(bubamara_cells)
  x2 = np.array(input_img_cells)


  # Now we prepare train_data and test_data.
  train = x1[:,:30].reshape(-1,10000).astype(np.float32) # Size = (3000,100)
  test = x2[:,:xCount * yCount].reshape(-1,xPixels * yPixels).astype(np.float32) # Size = (3000,100)

  # Create labels for the first 30 cells.
  k = np.arange(30)
  train_labels = np.repeat(k,1)[:,np.newaxis] # Length of labels will be 30

  # Initiate kNN and train the data.
  knn = cv2.KNearest()
  knn.train(train,train_labels)
  ret,result,neighbours,dist = knn.find_nearest(test,k=2)
  resultVec = result[:,:30].reshape(-1,1).astype(np.int)

  # Turn the result into a Unicode string
  s = ""
  for item in resultVec:
    s += abeceda[item[0]] + " "
  
    #make new directory for images 
  imagesPath = r'output/' + os.path.splitext(input_name)[0]
  if not os.path.exists(imagesPath):
    os.makedirs(imagesPath)
  
  #result2D = np.unravel_index(resultVec,(xCount,yCount))
  result2D = resultVec.reshape(xCount,yCount)

  for index, x in np.ndenumerate(result2D):
    l = abeceda[x]                                       # letter for specific image seg
    xLoc = index[0] * xPixels                            # X pixel of image seg
    yLoc = index[1] * yPixels                            # Y pixel of image seg
    imgSection = img2[xLoc:xLoc+100, yLoc:yLoc+100] # Crop from x, y, w, h -> xLoc, yLoc, 100,100
    imageLocName = imagesPath + '/' + str(index[0] ) + '_' + str(index[1] ) + "_" + l + ".jpg"
    cv2.imwrite(imageLocName, imgSection)


  # Save text to a file
  output_filename = 'output/' + input_name + ".txt"
  output_text = open(output_filename, 'w')
  output_text.write(s)
  output_text.close()



def main():
  # Set up the user's input image to check against.
  ap = argparse.ArgumentParser()
  ap.add_argument("-i", "--image", required = True, help = "Path to the image")
  args = vars(ap.parse_args())
  bubamaraGen(imgTrain,args["image"])


if __name__ == '__main__':
  main()