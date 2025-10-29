import cv2, numpy as np
from cvzone.HandTrackingModule import HandDetector

url = "http://10.104.155.41:4747/videos" 
cap = cv2.VideoCapture(url)
if not cap.isOpened():
    print(f"Error: Tidak bisa membuka stream dari {url}")
    print("Pastikan URL sudah benar dan perangkat terhubung ke jaringan yang sama.")
    exit()

detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1,  detectionCon=0.5, minTrackCon=0.5)

while True:
   ok, img = cap.read()
   if not ok: break
   hands, img  = detector.findHands(img, draw=True, flipType=True)
   if hands:
      hand = hands[0]
      fingers = detector.fingersUp(hand)
      count = sum(fingers)
      cv2.putText(img, f"Fingers: {count} {fingers}", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
   
   cv2.imshow("Hands + Fingers", img)
   if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()



