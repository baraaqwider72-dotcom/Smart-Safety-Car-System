import cv2
import time
import serial

# ربط مع الأردوينو (تأكد من رقم البورت!)
arduino = serial.Serial("com3", 9600)

# تحميل ملفات التعرف على الوجه والعين
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# تفعيل الكاميرا
cam = cv2.VideoCapture(0)
sleep_counter = 0

while True:
    ret, frame = cam.read()
    if not ret:
        print("❌ ما قدرنا نقرأ من الكاميرا")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    eyes_detected = False
    for (x, y, w, h) in faces:
        # نرسم مستطيل على الوجه (للتوضيح في الفيديو)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

        if len(eyes) > 0:
            eyes_detected = True

    if eyes_detected:
        print("🟢 مستيقظ")
        cv2.putText(frame, "Awake", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        arduino.write(b'1')
        sleep_counter = 0
    else:
        sleep_counter += 1
        if sleep_counter > 10:
            print("🔴 نايم")
            cv2.putText(frame, "sleeping", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            arduino.write(b'0')

    # عرض الفيديو مع التعرف على العيون والوجه
    cv2.imshow('Sleep Detection Live', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# تنظيف بعد الإغلاق
cam.release()
cv2.destroyAllWindows()