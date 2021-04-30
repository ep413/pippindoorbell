from pynput.mouse import Listener
import smtplib
import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


piip = "10.90.14.230"
sendToEmail = 'beastlydrake@gmail.com'


#HTML for the camera site
PAGE="""\
<html>
<head>
<style>
body {background-image: url("https://wallpapersfortech.com/wp-content/uploads/2021/03/Aesthetic-Minimalist-Background.png");  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;}
h1   {color: LightSteelBlue;font-family: Gill Sans, sans-serif;}
p    {color: SlateGray;font-family: Georgia, serif;}
</style>
<title>Doorbell Cam Live Feed</title>
</head>
<body>
<center><h1>Doorbell Live Feed</h1></center>
<center><p><i>Live footage from Raspberry Pi camera</i></p></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""


EMAIL="""\
<html>
  <head>
      <style>
body {background-color: LightGray;}
h3   {color: DarkSlateGray;font-family: Arial, Helvetica, sans-serif;}
p    {color: SlateGray;font-family: Arial, Helvetica, sans-serif;}
</style>
  </head>
  <body>
    <table style="background-color: white;">
   <tr><td style="padding:20px;"><h3><center>Someone rang your doorbell!</center></h3></td></tr>
   <tr><td style="padding:20px;"><p align="center">
  <img src="https://cdn.discordapp.com/attachments/830234510124777493/837498952910766131/doorbell.png" width="30%" /></p></td></tr> 
   <tr><td style="padding:20px;"><p>Open this IP address in your browser to see who it is:
    </p></td></tr> 
    <tr><td style="padding:20px;""size: 80%;"><center><a href=\"http://""" + piip + """:8000\">Click here!</a>
    </center><br></td></tr> 
    </table>
  </body>
</html>
"""



# Setting up the camera and stream # ------------------------------------
class StreamingOutput(object):
	def __init__(self):
		self.frame = None
		self.buffer = io.BytesIO()
		self.condition = Condition()

	def write(self, buf):
		if buf.startswith(b'\xff\xd8'):
			# New frame, copy the existing buffer's content and notify all
			# clients it's available
			self.buffer.truncate()
			with self.condition:
				self.frame = self.buffer.getvalue()
				self.condition.notify_all()
			self.buffer.seek(0)
		return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			self.send_response(301)
			self.send_header('Location', '/index.html')
			self.end_headers()
		elif self.path == '/index.html':
			content = PAGE.encode('utf-8')
			self.send_response(200)
			self.send_header('Content-Type', 'text/html')
			self.send_header('Content-Length', len(content))
			self.end_headers()
			self.wfile.write(content)
		elif self.path == '/stream.mjpg':
			self.send_response(200)
			self.send_header('Age', 0)
			self.send_header('Cache-Control', 'no-cache, private')
			self.send_header('Pragma', 'no-cache')
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
			self.end_headers()
			try:
				while True:
					with output.condition:
						output.condition.wait()
						frame = output.frame
					self.wfile.write(b'--FRAME\r\n')
					self.send_header('Content-Type', 'image/jpeg')
					self.send_header('Content-Length', len(frame))
					self.end_headers()
					self.wfile.write(frame)
					self.wfile.write(b'\r\n')
			except Exception as e:
				logging.warning(
					'Removed streaming client %s: %s',
					self.client_address, str(e))
		else:
			self.send_error(404)
			self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
	allow_reuse_address = True
	daemon_threads = True


output = StreamingOutput()
address = ('', 8000)
server = StreamingServer(address, StreamingHandler)

# function that actually does the thing
def runcam():
	print("camera starting")
	with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
		#output = StreamingOutput()
		#Uncomment the next line to change your Pi's Camera rotation (in degrees)
		#camera.rotation = 90
		camera.start_recording(output, format='mjpeg')
		try:
			#server.serve_forever()
			for i in range(4): #refresh to end it
				server.handle_request()
		finally:
			camera.stop_recording()
			print("camera stopped")
#----------------------------------------






# send an email #
Email_Address = 'pippindoorbell@gmail.com'
Email_Pass = 'welovepi'

def sendmail():
	print("sending email")
	with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
			smtp.ehlo()
			smtp.starttls()
			smtp.ehlo()

			smtp.login(Email_Address, Email_Pass)
	
			subject = 'View who is ringing the doorbell'
			body  = 'Open this IP in a browser to view:\nhttp://' + piip + ':8000/'

			html = MIMEText(EMAIL, "html")
			text = MIMEText(body, "plain")

			msg = MIMEMultipart("alternative")
			msg.attach(html)
	
			smtp.sendmail(Email_Address, sendToEmail, msg.as_string()) #send to this email
	print("done sending mail")    
#------



# MAIN #
def main():
	print("waiting for click")
	sendornot = 0
	def on_click (x,y,button,pressed):
		sendornot = 1
		listener.stop()
	
	with Listener(on_click=on_click) as listener:
		listener.join()
	print("clicked")

	sendmail()
	runcam()
#------

def mainfr():
	print("doorbell is running")
	while True:
		main()

if __name__ == '__main__':
	mainfr()
