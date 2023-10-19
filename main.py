import cv2 as cv
from cv2 import aruco
import numpy as np
import socket
import threading


shotCar1 = 0
shotEvent = threading.Event()

def server(arg):
    # get the hostname
    host = "192.168.1.18"
    port = 12346  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind((host, port))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(10)
    print("Escutando")
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        shotEvent.set()
        print(":SERVER : shotCar1: " + str(shotCar1))

        #data = input(' -> ')
        #conn.send(data.encode())  # send data to the client

    conn.close()  # close the connection


def drawLine(top, bottom, size, start, color, frame):
    newX = (int)(top[0])

    if (top[0] > bottom[0]):
        newX = (int)(top[0] + size)    
    elif(top[0] < bottom[0]):
        newX = (int)(top[0] - size)

    newY = (int)(top[0] + size)
    if (top[0] != bottom[0]):
        newY = (int)((((bottom[1] - top[1])/(bottom[0] - top[0]))*(newX - top[0])) + top[1])

    cv.line(frame, start, (newX, newY), color, thickness=5)

    return frame

def drawCircle(top, bottom, size, x, color, frame):
    
    if (top[0] > bottom[0]):
        newX = (int)(top[0] + x)    
    elif(top[0] < bottom[0]):
        newX = (int)(top[0] - x)

    newY = (int)(top[0] + size)
    if (top[0] != bottom[0]):
        newY = (int)((((bottom[1] - top[1])/(bottom[0] - top[0]))*(newX - top[0])) + top[1])

    cv.circle(frame, (newX, newY), 25, color, thickness=-1, lineType=8, shift=0)

    return frame

marker_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
param_markers = aruco.DetectorParameters_create()

#muda a camera
cap = cv.VideoCapture(1)

top_midle_past = 0 
bottom_midle_past = 0
arg = 0
max_shot = 800

#serverThread = threading.Thread(target=server, args=(arg,))
#serverThread.start()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    marker_corners, marker_IDs, reject = aruco.detectMarkers(
        gray_frame, marker_dict, parameters=param_markers
    )
    #comenta essa linha
    frame = cv.rectangle(frame, (0, 0), (2000, 2000), color=(0,0,0), thickness=-1)

    cv.rectangle(frame, (0, 0), (100, 100), color=(0, 255, 255), thickness=-1)
    cv.rectangle(frame, (1180, 0), (1280, 100), color=(0, 255, 255), thickness=-1)
    cv.rectangle(frame, (0, 720), (100, 620), color=(0, 255, 255), thickness=-1)

    if marker_corners:
        for ids, corners in zip(marker_IDs, marker_corners):
            
            #cv.polylines(
            #    frame, [corners.astype(np.int32)], True, (0, 255, 255), 4, cv.LINE_AA
            #)
            corners = corners.reshape(4, 2)
            corners = corners.astype(int)
            top_right = corners[0].ravel()
            top_left = corners[1].ravel()
            bottom_right = corners[2].ravel()
            bottom_left = corners[3].ravel()

            yDesl = -100
            top_right[1] = top_right[1] + yDesl
            top_left[1] = top_left[1] + yDesl
            bottom_right[1] = bottom_right[1] + yDesl
            bottom_left[1] = bottom_left[1] + yDesl

            xDesl = 200
            top_right[0] = top_right[0] + xDesl
            top_left[0] = top_left[0] + xDesl
            bottom_right[0] = bottom_right[0] + xDesl
            bottom_left[0] = bottom_left[0] + xDesl

            #circleCenter = ((int)(((bottom_right[0] + bottom_left[0])/2) + 50), (int) (((top_left[1] + bottom_left[1])/2) - 280))  
            #cv.circle(frame, circleCenter, 120, (0, 255, 255), thickness=-1, lineType=8, shift=0)

            top_midle = ((int)((top_right[0]+top_left[0])/2), (int)((top_right[1]+top_left[1])/2))
            bottom_midle = ((int)((bottom_right[0]+bottom_left[0])/2), (int)((bottom_right[1]+bottom_left[1])/2))

            #cv.circle(frame, top_midle, 25, (255, 0, 0), thickness=-1, lineType=8, shift=0)
            #cv.circle(frame, bottom_left, 25, (0, 255, 0), thickness=-1, lineType=8, shift=0)
            #cv.circle(frame, bottom_right, 25, (0, 0, 255), thickness=-1, lineType=8, shift=0)

            triangle_points = np.array([top_midle, bottom_left, bottom_right], np.int32)
            #triangle_points = triangle_points.reshape((-1, 1, 2))
            cv.polylines(frame, [triangle_points], isClosed=True, color=(0, 255, 0), thickness=2)


            drawLine(top_midle,bottom_midle,max_shot,top_midle,(0, 255, 0),frame)
            #cv.line(frame, top_midle, bottom_midle, (0, 255, 0), thickness=2)

            if (top_midle_past == 0):
                top_midle_past = top_midle 
                bottom_midle_past = bottom_midle

            #859,13 -> 1230,50
            #96, 33 -> 50, 670
            #if (shotEvent.is_set()):
            if (shotCar1 < 500):
                print("shotCar1: " + str(shotCar1))
                drawCircle(top_midle_past,bottom_midle_past,max_shot,shotCar1,(255, 255, 255),frame)
                shotCar1 = shotCar1 + 20
                if (shotCar1 > max_shot):
                    shotEvent.clear()
                    shotCar1 = 0
            else:
                shotCar1 = 0
                top_midle_past = top_midle 
                bottom_midle_past = bottom_midle
            
            #print(str(top_right) + ' ' + str(top_left)  + ' ' +  str(bottom_right) + ' ' + str(bottom_left))
            cv.putText(
                frame,
                f"CARRO {ids[0] + 1}",
                (bottom_right[0] - 80, bottom_right[1] + 130),
                cv.FONT_HERSHEY_PLAIN,
                3,
                (0, 255, 0),
                5,
                cv.LINE_AA,
            )

    cv.imshow("frame", frame)
    key = cv.waitKey(1)
    if key == ord("q"):
        break
cap.release()
cv.destroyAllWindows()