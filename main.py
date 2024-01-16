import pyttsx3
import time
import cv2
import sqlite3
from twilio.rest import Client
import RPi.GPIO as GPIO

class ChildSafetyRobot:
    def _init_(self):
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
                incident INTEGER DEFAULT 0
            )
        ''')

        self.child_profiles = {}
        self.touch_pins = [2, 3, 4]  # GPIO pins for touch sensors

    def add_child_profile(self, child_name, parent_phone):
        self.cursor.execute('INSERT INTO child_profiles (child_name, parent_phone) VALUES (?, ?)', (child_name, parent_phone))
        self.conn.commit()
        self.child_profiles[child_name] = {"parent_phone": parent_phone}

    def speak(self, text, emotion="neutral"):
        self.display_expression(emotion)  # Display appropriate facial expression based on emotion
        self.engine.say(text)
        self.engine.runAndWait()

    def greet(self):
        self.speak("Hello! I'm your Child Safety Robot. Let's learn about good touch and bad touch.")

    def introduce_lesson(self):
        self.speak("In this lesson, we'll learn about different types of touches.")
        self.speak("Good touch can be friendly, like a high-five. Bad touch can make you uncomfortable.")

    def explain_good_touch(self):
        self.speak("Good touch feels nice, like a hug from someone you trust.")
        self.speak("Can you think of other examples of good touch?")

    def explain_bad_touch(self):
        self.speak("Bad touch is not okay. It can be someone touching your private parts.")
        self.speak("Remember, you can say 'no' to bad touch and tell a grown-up.")

    def ask_example(self, touch_type):
        self.speak(f"Can you give me an example of {touch_type} touch?")

    def provide_feedback(self, correct):
        if correct:
            self.speak("That's right! Good job!")
        else:
            self.speak("Hmm, that's not quite right. Let's try again.")

    def conclude_lesson(self):
        self.speak("Remember, if you experience bad touch, tell a trusted adult immediately.")
        self.speak("Thank you for learning about good touch and bad touch!")

    def read_touch_sensor(self, pin):
        # Implement logic to read touch sensor
        pass

    def practice_touch_recognition(self):
        self.speak("Let's practice recognizing good and bad touches.")
        self.speak("I will ask you about different touches, and you can tell me if they are good or bad.")

        for idx, touch_pin in enumerate(self.touch_pins):
            touch_type = self.read_touch_sensor(touch_pin)
            if touch_type == "good":
                self.provide_feedback(True)
            else:
                self.provide_feedback(False)
                self.send_alert_sms()

        self.speak("Well done! You've practiced recognizing touches on different parts of your body.")

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

        self.practice_touch_recognition()
        time.sleep(1)

        self.explain_bad_touch()
        time.sleep(1)

        self.practice_touch_recognition()
        time.sleep(1)

        self.conclude_lesson()

if _name_ == "_main_":
    robot = ChildSafetyRobot()
    robot.interact()
    robot.close_database()