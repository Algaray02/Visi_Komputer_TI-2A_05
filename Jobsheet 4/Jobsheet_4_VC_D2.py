import cv2
from cvzone.PoseModule import PoseDetector

# Ganti dengan URL stream Anda
url = "http://192.168.1.7:4747/videos" 
cap = cv2.VideoCapture(url)

detector = PoseDetector(staticMode=False, modelComplexity=1, enableSegmentation=False, detectionCon=0.5, trackCon=0.5)

# Cek apakah kamera berhasil terbuka
if not cap.isOpened():
    print(f"Error: Tidak bisa membuka stream dari {url}")
    print("Pastikan URL sudah benar dan perangkat terhubung ke jaringan yang sama.")
    exit()

print("Membuka stream... Tekan 'q' untuk keluar.")

while True:
    # Baca frame dari video stream
    ok, img = cap.read()
    img = detector.findPose(img)

    imList, bboxInfo = detector.findPosition(img, draw=True, bboxWithHands=False)
    if imList:
        center = bboxInfo["center"]
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
        length, img, info = detector.findDistance(
            imList[11][0:2],
            imList[15][0:2],
            img=img,
            color=(255,0,0),
            scale=10
        )
        angle, img = detector.findAngle(
            imList[11][0:2],
            imList[13][0:2],
            imList[15][0:2],
            img=img,
            color=(0, 0, 255),
            scale=10
        )
        isCloseAngle50 = detector.angleCheck(myAngle=angle,
                                             targetAngle=50,
                                             offset=10)
        print(isCloseAngle50)
    if not ok:
        print("Error: Gagal membaca frame dari stream. Mungkin koneksi terputus.")
        break
    # Tampilkan frame

    cv2.imshow("Pose + Angle", img)

    # Cek jika tombol 'q' ditekan untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()