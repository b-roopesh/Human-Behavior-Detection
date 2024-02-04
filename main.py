import pyttsx3
import time
import sqlite3
from twilio.rest import Client
import RPi.GPIO as GPIO
import face_recognition 
import cv2
import numpy as np

class ChildSafetyRobot:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.client = Client("AC8322e7390ddcff879f38bbe6b2557aa3", "9bdf4f0e0c604661406c1ea5df59a8b3")
        self.parent_phone = None
        self.conn = sqlite3.connect('child_safety.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS child_profiles (
                id INTEGER PRIMARY KEY,
                child_name TEXT,
                parent_phone TEXT,
                face_encoding BLOB, -- Add the new column for face encoding
                incident INTEGER DEFAULT 0
            )
        ''')

        self.child_profiles = {}
        self.touch_pins = [2, 3]  # GPIO pins for touch sensors
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.touch_pins[0], GPIO.IN)
        GPIO.setup(self.touch_pins[1], GPIO.IN)

    def add_child_profile(self, child_name, parent_phone, face_encoding):
        self.cursor.execute('INSERT INTO child_profiles (child_name, parent_phone, face_encoding) VALUES (?, ?, ?)', (child_name, parent_phone, face_encoding))
        self.conn.commit()
        self.child_profiles[child_name] = {"parent_phone": parent_phone, "face_encoding": face_encoding}

    def speak(self, text, emotion="neutral"):
        self.engine.say(text)
        self.engine.runAndWait()

    def greet(self):
        self.speak("Hello! I'm your Child Safety Robot. Let's learn about good touch and bad touch.")
        print("Hello! I'm your Child Safety Robot. Let's learn about good touch and bad touch.")

    def introduce_lesson(self):
        self.speak("In this lesson, we'll learn about different types of touches.")
        self.speak("Good touch can be friendly, like a high-five. Bad touch can make you uncomfortable.")
        print("In this lesson, we'll learn about different types of touches.")
        print("Good touch can be friendly, like a high-five. Bad touch can make you uncomfortable.")

    def explain_good_touch(self):
        self.speak("Good touch feels nice, like a hug from someone you trust.")
        self.speak("Can you think of other examples of good touch?")
        print("Good touch feels nice, like a hug from someone you trust.")
        print("Can you think of other examples of good touch?")

    def explain_bad_touch(self):
        self.speak("Bad touch is not okay. It can be someone touching your private parts.")
        self.speak("Remember, you can say 'no' to bad touch and tell a grown-up.")
        print("Bad touch is not okay. It can be someone touching your private parts.")
        print("Remember, you can say 'no' to bad touch and tell a grown-up.")

    def practice_touch_recognition(self):
        self.speak("Let's practice recognizing good and bad touches.")
        self.speak("I will ask you about different touches, and you can tell me if they are good or bad.")
        print("Let's practice recognizing good and bad touches.")
        print("I will ask you about different touches, and you can tell me if they are good or bad.")

        # Check if a child profile is already registered
        child_name = self.recognize_child_face()
        if child_name:
            # If child recognized, continue with touch recognition
            good_touch_pin = self.touch_pins[0]  # Assuming the first pin is for good touch
            bad_touch_pin = self.touch_pins[1]   # Assuming the second pin is for bad touch
            print("Face recognized welcome ",child_name)
            # Read the state of the pins to determine if they are touched
            good_touch_state = GPIO.input(good_touch_pin)
            bad_touch_state = GPIO.input(bad_touch_pin)

            # Check if the sensor for good touch is activated
            if good_touch_state == GPIO.HIGH:
                self.provide_feedback(True)  # Respond as good touch
            # Check if the sensor for bad touch is activated
            elif bad_touch_state == GPIO.HIGH:
                self.provide_feedback(False)  # Respond as bad touch
                self.send_alert_sms()

            self.speak("Well done! You've practiced recognizing touches.")
        else:
            # If child not recognized, register the face and add parent phone number
            self.register_child_face()

    def recognize_child_face(self):
        # Initialize the camera
        camera = cv2.VideoCapture(0)

        # Capture a frame from the camera
        ret, frame = camera.read()

        # Convert the image from BGR color to RGB color (required by face_recognition library)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations in the frame
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            # Extract face encoding for the first face found
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            # Compare the face encoding with known child profiles
            for profile_name, profile in self.child_profiles.items():
                known_face_encoding = np.frombuffer(profile["face_encoding"])
                distance = face_recognition.face_distance([known_face_encoding], face_encoding)

                # If distance is below a threshold, consider it a match
                if distance < 0.6:
                    return profile_name

        # Release the camera
        camera.release()

        return None

    def register_child_face(self):
        # Initialize the camera
        camera = cv2.VideoCapture(0)

        # Capture a frame from the camera
        ret, frame = camera.read()

        # Convert the image from BGR color to RGB color (required by face_recognition library)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations in the frame
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            # Extract face encoding for the first face found
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            # Prompt the user to enter child details
            child_name = input("Enter child's name: ")
            parent_phone = input("Enter parent's phone number: ")

            # Add the child profile to the database
            self.add_child_profile(child_name, parent_phone, face_encoding)

            print(f"Child profile for {child_name} has been registered.")

        else:
            print("No face detected. Unable to register child profile.")

        # Release the camera
        camera.release()

    def provide_feedback(self, correct):
        if correct:
            self.speak("That's right! Good job!")
        else:
            self.speak("Hmm, that's not quite right. Let's try again.")

    def conclude_lesson(self):
        self.speak("Remember, if you experience bad touch, tell a trusted adult immediately.")
        self.speak("Thank you for learning about good touch and bad touch!")
        print("Remember, if you experience bad touch, tell a trusted adult immediately.")
        print("Thank you for learning about good touch and bad touch!")

    def send_alert_sms(self):
        if self.parent_phone:
            message = self.client.messages.create(
                body="Your child might have experienced an unsafe touch. Please check in with them.",
                from_="+12512449702",
                to=self.parent_phone
            )
            print("Alert SMS sent to parent.")
        else:
            print("Parent's phone number is not provided. Alert not sent.")

    def close_database(self):
        self.conn.close()

    def interact(self):
        self.greet()
        time.sleep(1)
        self.introduce_lesson()
        time.sleep(1)
        self.explain_good_touch()
        time.sleep(1)
        self.explain_bad_touch()
        time.sleep(1)
        self.practice_touch_recognition()
        time.sleep(1)
        self.conclude_lesson()

if __name__ == "__main__":
    robot = ChildSafetyRobot()
    robot.interact()
    robot.close_database()
