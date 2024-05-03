from ultralytics import YOLO
from PIL import Image
import cv2
import pandas as pd
import time
import os
import threading

Call = False
lock = threading.Lock()
def main():
    rtsp = "rtsp://admin:pass@192.168.1.2:554/cam/realmonitor?channel=1&subtype=0"
    phonenumber = "+84777777777"
    vcap = cv2.VideoCapture(rtsp)
    if(vcap.isOpened()):
        hx = 1920
        hy = 1080
        window_name = "Camera stream"
        my_file = open("coco.txt", "r")
        data = my_file.read()
        class_list = data.split("\n")
        model = YOLO('yolov8n.pt')
        end = time.time()
        start = time.time()
        def CMDStart():
            os.system('cmd.exe /c "adb start-server"')
        def CMD(command):
            return os.system('cmd.exe /c "' + command + '"')
        def Check(frame):
            global Call
            results = model(frame);
            for r in results:
                a=r.boxes.data
                px=pd.DataFrame(a).astype("float")
                for index,row in px.iterrows():
                    x1=int(row[0])
                    y1=int(row[1])
                    x2=int(row[2])
                    y2=int(row[3])
                    d=int(row[5])
                    c=class_list[d]
                    if 'person' in c:
                        phantram = '';
                        vitri = str(x1) + 'x' + str(y1) + '-' + str(x2) + 'x' + str(y2);
                        phantram = str(r.boxes.conf);
                        phantram = phantram.split(',')[0].replace("tensor", "").replace("(", "").replace("[", "").replace(")", "").replace("]", "").replace(" ", "");
                        pt = int(float(phantram) * 100)
                        if(pt >= 40):
                            if Call:
                                return
                            lock.acquire()
                            if Call:
                                return
                            Call = True
                            CMD('adb shell input keyevent KEYCODE_WAKEUP')
                            time.sleep(1)
                            CMD('adb shell am start -a android.intent.action.CALL -d tel:' + phonenumber)
                            time.sleep(50)
                            lock.release()
                            time.sleep(10)
                            Call = False
                            # print(str(pt) + '|' + vitri)
                            # img_arr = r.plot()
                            # im = Image.fromarray(img_arr[..., ::-1])
                            # im.show()
                            # im.save('test.jpg');
        CMDStart()
        while(1):
            ret, frame = vcap.read()
            if ret:
                small_frame = cv2.resize(frame, (hx, hy))
                cv2.imshow(window_name, small_frame)
                end = time.time()
                if end - start >= 2 and not Call:
                    t1 = threading.Thread(target=Check, args=(small_frame,))
                    t1.start()
                    start = time.time()
                try:
                    if cv2.waitKey(1) == 27:
                        raise Exception("exit")
                    cv2.getWindowProperty(window_name, 0)
                except Exception as e:
                    err = str(e)
                    if(err.__contains__('exit') | err.__contains__('NULL window')):
                        vcap.release()
                        cv2.destroyAllWindows()
                        break
if __name__ == '__main__':
    main()

