import cv2


def capture_frame(cap, L=0.9, a=1.25):
    success, img = cap.read()
    if success is False:
        print('Failed to connect to camera')

    # reduce noise
    img = cv2.GaussianBlur(img, (5, 5), 1)

    # perform histogram equalization on the luminance channel Y using CLAHE
    cimg = img.copy()
    cimg = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl1 = clahe.apply(cimg[..., 0])
    cimg[..., 0] = cl1
    img = cv2.cvtColor(cimg, cv2.COLOR_YUV2BGR)

    # to more easily distinguish colours
    img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    img_lab[..., 0] = img_lab[..., 0] * L
    img_lab[..., 1] = img_lab[..., 1] * a  # 1.2
    img_lab[..., 2] = img_lab[..., 2] * 1
    img = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)
    return img
