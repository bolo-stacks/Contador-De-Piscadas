import cv2
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
import math
import numpy as np

def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def main():
    mp_face_mesh = mp.solutions.face_mesh

    # cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture('example.mp4')

    cap.set(cv2.CAP_PROP_FPS, 25.0)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height  = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    ratios = []
    
    piscando = False
    blinkCount = 0
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                break

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(image)

            # Draw the face mesh annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            face_landmarks = results.multi_face_landmarks[0].landmark
                
            cord1 = _normalized_to_pixel_coordinates(face_landmarks[159].x, face_landmarks[159].y, width, height)
            cord2 = _normalized_to_pixel_coordinates(face_landmarks[145].x, face_landmarks[145].y, width, height)
            cord3 = _normalized_to_pixel_coordinates(face_landmarks[33].x, face_landmarks[33].y, width, height)
            cord4 = _normalized_to_pixel_coordinates(face_landmarks[133].x, face_landmarks[133].y, width, height)
            
            cv2.line(image, cord1, cord2, (255, 0, 0), 4)
            cv2.line(image, cord3, cord4, (0, 0, 255), 4)

            dist = math.sqrt((cord1[0] - cord2[0])**2 + (cord1[1] - cord2[1])**2)
            dist2 = math.sqrt((cord4[0] - cord3[0])**2 + (cord4[1] - cord3[1])**2)

            ratio = (dist2 / dist)
            ratios.append(ratio)

            if len(ratios) == 5:
                ratios.pop(0)

            mediaRatio =  np.mean(ratios)

            ratioMapped = _map(mediaRatio, 0, 40, 40, 0)

            if(ratioMapped < 15 and piscando == False):
                blinkCount += 1
                piscando = True

            if(ratioMapped >= 18 and piscando == True):
                piscando = False
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, str(blinkCount), (100, 300), font, 10, (100, 0, 255), 5, cv2.LINE_AA)

            cv2.imshow('MediaPipe Face Mesh', image)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
        
    cap.release()

main()
