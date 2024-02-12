# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2

def recognize_face():
    # Determine faces from encodings.pickle file model created from train_model.py
    encodingsP = "encodings.pickle"

    # load the known faces and embeddings along with OpenCV's Haar
    # cascade for face detection
    
    data = pickle.loads(open(encodingsP, "rb").read())

    # initialize the video stream and allow the camera sensor to warm up
    # Set the ser to the following
    # src = 0 : for the built-in single webcam, could be your laptop webcam
    # src = 2 : I had to set it to 2 in order to use the USB webcam attached to my laptop
    # vs = VideoStream(src=2, framerate=10).start()
    vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

    # start the FPS counter
    fps = FPS().start()

    recognized_face_name = "Unknown"

    # loop over frames from the video file stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to 500px (to speed up processing)
        frame = vs.read()
        frame = imutils.resize(frame, width=500)

        # Detect the face boxes
        boxes = face_recognition.face_locations(frame)

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(frame, boxes)

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"  # if face is not recognized, then print Unknown

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a dictionary to count the total number of times each face was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                # loop over the matched indexes and maintain a count for each recognized face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number of votes
                name = max(counts, key=counts.get)

                # Update the recognized face name
                recognized_face_name = name

        # If a face is recognized, break the loop
        if recognized_face_name != "Unknown":
            break

        # update the FPS counter
        fps.update()

    # stop the timer
    fps.stop()

    # do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()

    return recognized_face_name

if __name__ == "__main__":
    recognized_name = recognize_face()
    print(recognized_name)
