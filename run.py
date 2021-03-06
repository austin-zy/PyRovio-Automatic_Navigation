from lib import Rovio
import cv2
import numpy as np
import winsound, sys, time

from skimage import filter, img_as_ubyte


class rovioControl(object):
    def __init__(self, url, username, password, port=80):
        self.rovio = Rovio(url, username=username, password=password,
                           port=port)
        self.last = None
        self.key = 0

    def night_vision(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.equalizeHist(frame)
        return frame

    def show_battery(self, frame):
        sh = frame.shape
        m, n = sh[0], sh[1]
        battery, charging = self.rovio.battery()
        battery = 100 * battery / 130.
        bs = "Battery: %0.1f" % battery
        cs = "Status: Roaming"
        if charging == 80:
            cs = "Status: Charging"
        cv2.putText(frame, bs, (20, 20),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))

        cv2.putText(frame, cs, (300, 20),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0))

        return frame

    def resize(self, frame, size=(640, 480)):
        frame = cv2.resize(frame, size)
        return frame

    def face_detection(self):
        # Stop Rovio so that it can stop down to recognize
        self.rovio.stop()
        self.rovio.head_up()
        flag = False

        frame = self.rovio.camera.get_frame()
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow(frame)

        if faces == ():
            pass
        else:
            flag = True
            winsound.PlaySound('%s.wav' % 'humandetected', winsound.SND_FILENAME)
        return flag


    def floor_finder(self):
        frame = self.rovio.camera.get_frame()
        im_gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gaussian = cv2.GaussianBlur(im_gray,(5,5),0)
        edges = cv2.Canny(gaussian,100,200)
        ##############################
        # Make the line more obvious #
        ##############################
        # Kernel
        kernel = np.ones((2, 2), np.uint8)
        dilate = cv2.dilate(edges, kernel, iterations=1)
        # Perform matrix function
        im = np.asarray(dilate)
        h= np.size(im, 0)
        w= np.size(im, 1)
        y = 0
        line = []
        for j in range(h-1,0,-1):
            for i in range(w):
                if not im[j][i] == 0:
                    y = j
                    break
            cv2.rectangle(frame,(0,y),(w,h),(245,252,0),2)
        cv2.imshow("FloorFinder", frame)
        return h-y

    def main(self):
        # self.rovio.head_middle()
        frame = self.rovio.camera.get_frame()
        if not isinstance(frame, np.ndarray):
            return
        frame = self.night_vision(frame)
        # frame = filter.sobel(frame)
        # frame = img_as_ubyte(frame)
        frame = self.resize(frame)

        frame = cv2.merge([frame, frame, frame])

        frame = self.show_battery(frame)

        if self.floor_finder() > 50:
            if (not self.rovio.ir()):
                self.rovio.api.set_ir(1)
            if (not self.rovio.obstacle()):
                self.rovio.forward(speed=7)
            else:
                self.rovio.rotate_right(angle=20, speed=2)
        else:
            self.rovio.rotate_right(angle=20, speed=2)


        self.key = cv2.waitKey(20)
        if self.key > 0:
            # print self.key
            pass
        if self.key == 114:  # r
            self.rovio.turn_around()
        elif self.key == 63233 or self.key == 115:  # down or s
            self.rovio.backward(speed=1)
        elif self.key == 63232 or self.key == 119:  # up or w
            self.rovio.forward(speed=1)
        elif self.key == 63234 or self.key == 113:  # left or a
            self.rovio.rotate_left(angle=12, speed=5)
        elif self.key == 63235 or self.key == 101:  # right or d
            self.rovio.rotate_right(angle=12, speed=5)
        elif self.key == 97:  # left or a
            self.rovio.left(speed=1)
        elif self.key == 100:  # right or d
            self.rovio.right(speed=1)
        elif self.key == 44:  # comma
            self.rovio.head_down()
        elif self.key == 46:  # period
            self.rovio.head_middle()
        elif self.key == 47:  # slash
            self.rovio.head_up()

        elif self.key == 32:  # Space Bar
            flag = False
            self.rovio.stop()
            while not flag:
                flag = self.face_detection()
                print flag

if __name__ == "__main__":
    url = '192.168.10.18'
    user = 'myname'
    password = "12345"
    app = rovioControl(url, user, password)
while True:
    app.main()
    if app.key == 27:
        app.rovio.head_down()
        break