import numpy as np
import cv2
import time, os, imutils
import matplotlib.pyplot as plt

def check_distance(a,b):
  dist = ((a[0]-b[0])**2 + 550 /((a[1]+b[1])/2)*(a[1]-b[1])**2)**0.5
  calibration = (a[1]+b[1])/2
  if 0<dist<0.25*calibration:
    return True
  else:
    return False

weights = 'yolov3.weights'
config = 'yolov3.cfg'
labelsPath = 'coco.names'

filename = 'test.mp4'

create= None
frameno = 0

cap = cv2.VideoCapture(0)
time1 = time.time()
while(True):
  ret, frame = cap.read()
  if not ret:
    break



  current_img = frame.copy()
  current_img = imutils.resize(current_img,width=480)
  video = current_img.shape
  frameno+=1

  if frameno%2==0 or frameno == 1:
    net = cv2.dnn.readNetFromDarknet(config,weights)

    labels = open(labelsPath).read().strip().split("\n")

    ln = net.getLayerNames()




    ln = [ln[i[0]-1] for i in net.getUnconnectedOutLayers() ]

    (H, W) = (None, None)
    if W is None or H is None:
        (H, W) = current_img.shape[:2]
    
    blob = cv2.dnn.blobFromImage(current_img, 1/255.0,(416,416),swapRB=True,crop=False)
    net.setInput(blob)
    starttime = time.time()
    layerOutputs = net.forward(ln)
    stoptime = time.time()
    print("Video is getting processed a t {:.4f} seconds per frame".format((stoptime-starttime)))
    confidences = []
    outline = []

    for output in layerOutputs:
      for detection in output:
  
        scores = detection[5:]
        maxi_class = np.argmax(scores)
        confidence = scores[maxi_class]
        if labels[maxi_class] == "person":
          if confidence>0.5:
            box = detection[0:4] * np.array([W,H,W,H])
            (centerX, centerY, width, height) = box.astype("int")
            x = int(centerX-(width/2))
            y = int(centerY-(height/2))
            outline.append([x,y,int(width),int(height)])
            confidences.append(float(confidence))


    box_line = cv2.dnn.NMSBoxes(outline,confidences,0.5,0.3)

    if len(box_line)>0:
      flat_box = box_line.flatten()
      pairs = []
      center = []
      status = []

      for i in flat_box:
        (x,y) = (outline[i][0], outline[i][1])
        (w,h) = (outline[i][2], outline[i][3])
        center.append([int(x+w/2),int(y+h/2)])
        status.append(False)

      for i in range(len(center)):
        for j in range(len(center)):
          close = check_distance(center[i],center[j])

          if close:
            pairs.append([center[i],center[j]])
            status[i]= True
            status[j] = True

  
      index = 0

      for i in flat_box:
        (x,y) = (outline[i][0], outline[i][1])
        (w,h) = (outline[i][2], outline[i][3])
        if status[index] == True:
          cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,150),2)
        elif status[index] == False:
          cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        index+=1
      for h in pairs:
        cv2.line(frame,tuple(h[0]),tuple(h[1]),(0,0,255),2)
    processedImg = frame.copy()


    Frame = processedImg

#     if create is None:
#       fourcc = cv2.VideoWriter_fourcc(*'XVID')
#       create = cv2.VideoWriter(opname,fourcc,30,(Frame.shape[1],Frame.shape[1],Frame.shape[0]))
#   create.write(Frame)
    cv2.imshow('Test video',Frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
time2 = time.time()
print(time2-time1)
cap.release()
cv2.destroyAllWindows()

