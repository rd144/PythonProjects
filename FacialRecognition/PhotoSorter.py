import cv2
import glob
import os

class FacialRecognition():

    def __init__(self):
        # Create the haar cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    def ResizeWithAspectRatio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        else:
            r = width / float(w)
            dim = (width, int(h * r))

        return cv2.resize(image, dim, interpolation=inter)

    def recognise_faces(self,image_path):

        # Read the image
        image = cv2.imread(image_path)
        shrink_factor = 0.05
        (h, w) = image.shape[:2]
        face_factor = (round(shrink_factor * h), round(shrink_factor * w))

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.25,
            minNeighbors=5,
            minSize=face_factor,
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        print("Found {0} faces!".format(len(faces)))

        if len(faces) > 0:

            # Draw a rectangle around the faces
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            resize = self.ResizeWithAspectRatio(image,800)
            cv2.imshow("Faces found", resize)
            cv2.waitKey(0)

def main(root_path):

    recogniser = FacialRecognition()

    path_iterator = filter(os.path.isfile, glob.glob(root_path + '/**/*', recursive=True))
    for path in path_iterator:
        recogniser.recognise_faces(path)

if __name__ == '__main__':
    main("C:\\Users\\Ross\\Desktop\\Stuff to keep\\jpg")
