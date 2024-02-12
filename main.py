import subprocess
import RPi.GPIO as GPIO
import time
import pyttsx3
from twilio.rest import Client
import pickle

class ChildSafetyRobot:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.client = Client("sid", "secret code")
        self.parent_phone_numbers = {
            "Roopesh": "+xxxxxxx",  # Add parent phone numbers for each child
            "Ashwitha": "+xxxxxx",
            "Siri": "+xxxxxxxx",
            "Prasanna": "+xxxxxx"
        }
        self.unknown_parent_phone = "+9xxxxxx"  # Parent phone number for unknown faces (Roopesh's number)
        self.touch_pins = [17, 27]  # GPIO pins for touch sensors
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.touch_pins[0], GPIO.IN)
        GPIO.setup(self.touch_pins[1], GPIO.IN)

    def speak(self, text, emotion="neutral"):
        self.engine.say(text)
        self.engine.runAndWait()

    def wait_for_touch(self):
        print("Waiting for a touch on any sensor...")
        while True:
            # Check the state of both sensors
            if GPIO.input(self.touch_pins[0]) == GPIO.HIGH or GPIO.input(self.touch_pins[1]) == GPIO.HIGH:
                break
            time.sleep(0.1)  # Adjust sleep duration as needed

        # Determine which sensor was touched
        if GPIO.input(self.touch_pins[0]) == GPIO.HIGH:
            return "good_touch"
        elif GPIO.input(self.touch_pins[1]) == GPIO.HIGH:
            return "bad_touch"

    def recognize_child_face(self):
        # Run the face_req.py script as a subprocess
        process = subprocess.Popen(["python", "face_req.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for the process to finish and capture its output
        stdout, stderr = process.communicate()

        # Decode the output and extract the recognized face name
        output = stdout.decode("utf-8")
        recognized_face_name = output.strip()

        return recognized_face_name

    def practice_touch_recognition(self):
        print("Let's practice recognizing good and bad touches.")
        print("I will ask you about different touches, and you can tell me if they are good or bad.")

        # Check if a child profile is already recognized
        child_name = self.recognize_child_face()
        if child_name!="Unknown":
            print(f"Welcome, {child_name}! Let's practice touch detection.")
            touch_type = self.wait_for_touch()
            if touch_type == "good_touch":
                self.speak(f"That's right!{child_name} Good job! It is a good touch")
                print(f"That's right!{child_name} Good job! It is a good touch")
                time.sleep(2)
                print("Let's try again")
                self.practice_touch_recognition2(child_name)
            elif touch_type == "bad_touch":
                self.speak(f"Hmm, that's not quite right {child_name}. Let's try again.")
                print(f"Hmm, that's not quite right {child_name}. Let's try again.")
                self.send_alert_sms(child_name)
            else:
                print("Unknown touch detected.")
        else:
            print("Unknown face detected.")
            self.parent_phone_numbers["Unknown"] = self.unknown_parent_phone
            touch_type = self.wait_for_touch()
            if touch_type == "good_touch":
                print("Good touch detected from an unknown person.")
            elif touch_type == "bad_touch":
                print("Bad touch detected from an unknown person.")
                self.send_alert_sms("Unknown")
            else:
                print("Unknown touch detected.")
    def practice_touch_recognition2(self,child_name):
        touch_type = self.wait_for_touch()
        if touch_type == "good_touch":
            self.speak(f"That's right!{child_name} Good job! It is a good touch")
            print(f"That's right!{child_name} Good job! It is a good touch")
            time.sleep(2)
            print("Let's try again")
            self.practice_touch_recognition2(child_name)
        elif touch_type == "bad_touch":
            self.speak(f"Hmm, that's not quite right {child_name}. Let's try again.")
            print(f"Hmm, that's not quite right {child_name}. Let's try again.")
            self.send_alert_sms(child_name)
        else:
            print("Unknown touch detected.")

    def send_alert_sms(self, child_name):
        if child_name in self.parent_phone_numbers:
            parent_phone = self.parent_phone_numbers[child_name]
            twilio = "+12138163726"
            message = self.client.messages.create(
                from_=twilio,
                body=f"⚠️Your child {child_name} might have experienced an unsafe touch❌. Please check in with them.",
                to=parent_phone
            )
            print("Alert SMS sent to parent number."parent_phone)
        else:
            self.send_alert_sms("Roopesh")
            print("Alert sent to the default number")

    def interact(self):
        self.practice_touch_recognition()

if __name__ == "__main__":
    robot = ChildSafetyRobot()
    robot.interact()
