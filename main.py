import sys
import pygame
import pygame.camera
import BaseHTTPServer
from optparse import OptionParser
from socket import gethostbyname_ex, gethostname
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread

parser = OptionParser()
parser.add_option('-i', '--ip', dest='ip', help='Server IP address')

options, args = parser.parse_args()

if options.ip == None:
  print 'Error: You must give the IP address.\nRun with -h to see usage.\n'
  sys.exit(0)

IP = options.ip
PORT = 9001

HandlerClass = SimpleHTTPRequestHandler
HandlerClass.protocol_version = "HTTP/1.0"
ServerClass = BaseHTTPServer.HTTPServer

server = ServerClass((IP, PORT), HandlerClass)
print "Webcam server running at", (IP,PORT)
try:
  server.serve_forever()
except KeyboardInterrupt:
  print '\nClosing server.'
  server.socket.close()

sys.exit(0)

pygame.init()
pygame.camera.init()

image = pygame.Surface((640, 480))

cam_list = pygame.camera.list_cameras()
print 'Camlist', cam_list
if len(cam_list) == 0:
  print 'No camera found.'
  pygame.quit()
  sys.exit(-1)

webcam = pygame.camera.Camera(cam_list[0], (32,24))
webcam.start()

image = webcam.get_image()
image = pygame.transform.scale(image, (640, 480))
pygame.image.save(image, 'image.png')

webcam.stop()
pygame.quit()

