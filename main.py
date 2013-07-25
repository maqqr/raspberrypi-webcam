# -*- coding: utf-8 -*-
""" Captures images from Raspberry Pi webcam """

import sys
import time
import pygame
import pygame.camera
import platform
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from optparse import OptionParser
#from socket import gethostbyname_ex, gethostname
from threading import Thread

# todo: get IP automatically
IP = ''
PORT = 9001
IMAGEFILE = 'image.png'
TEMPLATE = ''

class CameraThread(Thread):
    """ CameraThread captures images from USB webcam """

    def __init__(self, camera):
        super(CameraThread, self).__init__()
        self.camera = camera
        self.capture = True

    def stop_capture(self):
        """ Stops camera capture """
        self.capture = False
        self.camera.stop()
    
    def run(self):
        """ Camera capture main loop """
        while self.capture:
            image = self.camera.get_image()
            image = pygame.transform.scale(image, (640, 480))
            pygame.image.save(image, IMAGEFILE)
            time.sleep(1.0)


class HTTPHandler(BaseHTTPRequestHandler):
    """ HTTPHandler sends webcam images over HTTP """
    protocol_version = "HTTP/1.0"
    filename = 'image.png'
    
    def do_GET(self):
        """ Handle GET request """
        print self.path
        if self.path.startswith('/webcam_raw'):
            self.send_response(200)
            self.send_header('Content-type', 'image/png')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Cache-Control', 'no-cache, must-revalidate')
            self.end_headers()
            with open(IMAGEFILE, 'rb') as imgfile:
                self.wfile.write(imgfile.read())
        elif self.path.startswith('/webcam'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            addr = IP + ":" + str(PORT)
            self.wfile.write(TEMPLATE % (addr, addr))

        else:
            self.send_error(404, "Path not found: %s" % self.path)


def main():
    global IP, TEMPLATE
    # Parse command-line options
    parser = OptionParser()
    parser.add_option('-i', '--ip', dest='ip', help='Server IP address')
    options, _ = parser.parse_args()
    if options.ip == None:
        print 'Error: You must give the IP address.\nRun with -h to see usage.'
        sys.exit(0)
    IP = options.ip

    # Read template file
    with open('webcam.html') as htmlfile:
        TEMPLATE = htmlfile.read()

    
    # Initialize Pygame and camera
    pygame.init()
    pygame.camera.init()

    cam_list = pygame.camera.list_cameras()
    print 'Camlist', cam_list
    if len(cam_list) == 0:
        print 'No camera found.'
        pygame.quit()
        sys.exit(-1)

    if platform.uname()[0] != 'Windows':
        camera = pygame.camera.Camera(cam_list[0], (32, 24))
        camera.start()

        camthread = CameraThread(camera)
        camthread.start()
    else:
        camthread = None

    # Start server
    server = HTTPServer((IP, PORT), HTTPHandler)
    print "Webcam server running at", (IP, PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print '\nClosing server.'
        server.socket.close()

    if camthread:
        camthread.stop_capture()
    pygame.quit()

if __name__ == '__main__':
    main()
