from ultralytics import YOLO
#from PIL import Image
import cv2
import pandas as pd
import time
import threading
import ctypes
import subprocess

rtsp = "rtsp://admin:pass@192.168.1.2:554/cam/realmonitor?channel=1&subtype=0"
phonenumber = "+84777777777"
all_devices = []
class_list = []
Call = False
lock = threading.Lock()
model = YOLO('yolov8n.pt')
def CMD(command):
    return subprocess.check_output('cmd.exe /c "' + command + '"', shell=True, encoding='utf-8')
def CMDStart():
    CMD('adb start-server')
def GetDevices():
    cm = CMD('adb devices')
    datau = cm.split("\n")
    dv = []
    for mn in datau:
        if(mn.__contains__("devices")):
            continue
        if(mn.__contains__("device")):
            cachedv = mn.split("device")
            dv.append(cachedv[0].replace(" ", "").replace("\t", ""))
    return dv
def Check(frame):
    global Call
    global phonenumber
    global all_devices
    global model
    global class_list
    results = model(frame);
    for r in results:
        a = r.boxes.data
        px = pd.DataFrame(a).astype("float")
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
                    CMD('adb -s ' + all_devices[0] + ' shell input keyevent KEYCODE_WAKEUP')
                    time.sleep(2)
                    CMD('adb -s ' + all_devices[0] + ' shell am start -a android.intent.action.CALL -d tel:' + phonenumber)
                    time.sleep(50)
                    lock.release()
                    time.sleep(10)
                    Call = False
                    # print(str(pt) + '|' + vitri)
                    # img_arr = r.plot()
                    # im = Image.fromarray(img_arr[..., ::-1])
                    # im.show()
                    # im.save('test.jpg');
def main():
    global Call
    global phonenumber
    global all_devices
    global model
    global class_list
    my_rtsp = open("rtsp.txt", "r")
    data_rtsp = my_rtsp.read()
    class_rtsp = data_rtsp.split("\n")
    rtsp = class_rtsp[0]
    vcap = cv2.VideoCapture(rtsp)
    if(vcap.isOpened()):
        hx = 1920
        hy = 1080
        window_name = "Camera stream"
        my_file = open("coco.txt", "r")
        data = my_file.read()
        class_list = data.split("\n")
        my_phone = open("phone.txt", "r")
        data_phone = my_phone.read()
        class_phone = data_phone.split("\n")
        phonenumber = class_phone[0]
        end = time.time()
        start = time.time()
        CMDStart()
        all_devices = GetDevices()
        if(len(all_devices) == 0):
            ctypes.windll.user32.MessageBoxW(0, "Check connection to phone!", "", 16)
            while(1):
                time.sleep(5)
                all_devices = GetDevices()
                if(len(all_devices) == 0):
                    ctypes.windll.user32.MessageBoxW(0, "Check connection to phone!", "", 16)
                else:
                    break
        vcap.read()
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
    else:
        ctypes.windll.user32.MessageBoxW(0, "Connection to rtsp failed", "Error!", 16)
    return
if __name__ == '__main__':
    main()

