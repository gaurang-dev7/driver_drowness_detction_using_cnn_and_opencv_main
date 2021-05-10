from keras.preprocessing import image as keras_image
from keras.models import model_from_json
from scipy.spatial import distance
from imutils import face_utils
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import dlib
from threading import Thread
import pyglet
import sys

from werkzeug.utils import redirect

def eye_aspect_ratio(eye):
	A = distance.euclidean(eye[1], eye[5])
	B = distance.euclidean(eye[2], eye[4])
	C = distance.euclidean(eye[0], eye[3])
	earcv = (A + B) / (2.0 * C)
	return earcv



def sound_alarm(path):
    # play an alarm sound0
    music = pyglet.resource.media(path)
    music.play()

    pyglet.app.run()



def loadModel(model_path, weight_path):
    json_file = open(model_path, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(weight_path)
    print("Loaded model from disk")
    model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    return model

def predictImage(img, model):
    img = np.dot(np.array(img, dtype='float32'), [[0.2989], [0.5870], [0.1140]]) / 255
    x = keras_image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    images = np.vstack([x])
    classes = model.predict(images, batch_size=20)
    return classes[0][0]

def predictFacialLandmark(img, detector):
    img = imutils.resize(img, width=500)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    return rects



def drawEyes(eye, image):
    (x, y, w, h) = cv2.boundingRect(np.array([eye]))
    h = w
   #  y = y - h / 2
    ri = image[y:y + h, x:x + w]
    ri = imutils.resize(ri, width=24, inter=cv2.INTER_CUBIC)

    return ri

def main():
    COUNTER = 0
    ALARM_ON = False
    MAX_FRAME = 10
    #loade model
    model = loadModel('trained_model/model1.json', "trained_model/weight1.h5")

    # Facial Landmark file
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    #facelandmark
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    print("starting video stream ...")

    vs = VideoStream(src=0).start()
    # vs=cv2.VideoCapture(0)

    counter = 0
    while True:

        #get frame-> resize->grayscale
        frame = vs.read()
        frame = imutils.resize(frame, width=500)

        # detect faces in the grayscale frame
        rects = predictFacialLandmark(img=frame, detector=detector)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detector(gray, 0)

        # loop for face detections

        for rect in rects:

            ################################
            ##########cnn###################
            threshcnn=0.12
            counter += 1
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEyeRatio = shape[lStart:lEnd]
            leftEye = drawEyes(leftEyeRatio, frame)

            rightEyeRatio = shape[rStart:rEnd]
            rightEye = drawEyes(rightEyeRatio, frame)


            classLeft = predictImage(leftEye, model=model)
            classRight = predictImage(rightEye, model=model)

            # print (round((classLeft+classRight),4))
            value=(round((classLeft+classRight),4))
            #(classLeft == 0 and classRight == 0)
            

            ######################################
            ########opencv########################
            threshcv = 0.25
            flag=0
            leftEyecv = shape[lStart:lEnd]
            rightEyecv = shape[rStart:rEnd]
            leftEARcv = eye_aspect_ratio(leftEyecv)
            rightEARcv = eye_aspect_ratio(rightEyecv)
            earcv = (leftEARcv + rightEARcv) / 2.0
            leftEyeHull = cv2.convexHull(leftEyecv)
            rightEyeHull = cv2.convexHull(rightEyecv)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)



            if value>threshcnn or earcv<threshcv:
                COUNTER += 1
                flag += 1


                cv2.putText(frame, "Closing", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Counter: {:.2f}".format(COUNTER), (300, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if COUNTER >= MAX_FRAME or flag>=MAX_FRAME:
                    if not ALARM_ON:
                        ALARM_ON = True
                        t = Thread(target=sound_alarm,
                                   args=('alarm.wav',))
                        t.deamon = True
                        t.start()


                    cv2.putText(frame, "DROWSY!", (100, 300),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            else:
                flag = 0
                COUNTER = 0
                ALARM_ON = False
                cv2.putText(frame, "Opening", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)




        cv2.imshow("dfd", frame)
        key = cv2.waitKey(1) & 0xFF

        # press q for exit
        if key == ord("q"):
            break
    cv2.destroyAllWindows()
    vs.stop()
    sys.exit()
    

if __name__ == "__main__":
    main()
    sys.exit()