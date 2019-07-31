import cv2

# Get camera object
cap = cv2.VideoCapture(0)

# Exit if camera failed to open
if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Capture one frame
ret, frame = cap.read()

# ret is True if the capture was executed and the frame has been transfered
if not ret:
    print("Can't receive frame (stream end?). Exiting ...")
    exit()

# write image to disk
cv2.imwrite("test.jpg", frame)

# When everything done, release the capture
cap.release()