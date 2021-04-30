# Pippin Doorbell

Pippin Doorbell is a camera-enabled doorbell Python program for Raspberry Pi. Upon ringing the user's doorbell, the camera is activated and an email alert indicating that the doorbell has been rung is sent to the user with a link to a page with the live camera video feed. The user can then view the live feed to see who is at their door, and terminate the camera by closing the window.


## Usage

Download doorbell.py and edit the two global variables at the top with the IP address of your pi and the email you want to receive the alerts. Then, put the program on your raspberry pi and run the command “python3 doorbell.py”. This will constantly wait for a mouse click (we connected a usb mouse for our “doorbell”) and when it’s pressed, you will get an email with the link to the IP address of the pi which is streaming video. When done, refresh the page to expend the requests and the program will go back to waiting.

https://youtu.be/6ygKkVLaAOM for proof of project working

## Contributing

Organizer – Emily
Programmers – William, Emily, Drake
Tester – Drake, William

## Libraries

Pynput
SMPT protocol client
IO
Picamera
Logging
Socketserver
Threading
Http
Email.mime

## License
[MIT](https://choosealicense.com/licenses/mit/)
