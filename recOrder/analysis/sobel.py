# bchhun, {2019-08-09}
from recOrder.analysis._analyze_base import AnalyzeBase
import cv2
import numpy as np


class Sobel(AnalyzeBase):

    # @AnalyzeBase.bidirectional(receiver_channel=0, emitter_channel=1)
    def rotate_and_sobel(self, image, deg):
        return self.cv2_rotate(self.cv2_sobel_edge_with_binary(image), deg)

    @AnalyzeBase.bidirectional(receiver_channel=0, emitter_channel=1)
    def sobel_only(self, image):
        return self.cv2_sobel_edge_with_binary(image)

    # @AnalyzeBase.bidirectional(receiver_channel=0, emitter_channel=1)
    def image_only(self, image):
        return image

    def cv2_rotate(self,image, degree):
        rows, cols = image.shape
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), degree, 1)
        dest = cv2.warpAffine(image, M, (cols, rows))
        return dest

    def cv2_sobel_edge_with_binary(self, image):
        k = 3
        thresh = 0.8*np.max(image)

        blur = cv2.GaussianBlur(image, (k, k), 0)

        (t, binary) = cv2.threshold(blur, thresh, 65534, cv2.THRESH_BINARY_INV)

        grad_x = cv2.Sobel(binary, cv2.CV_16U, 2, 0)
        grad_y = cv2.Sobel(binary, cv2.CV_16U, 0, 2)

        edge = cv2.bitwise_or(grad_x, grad_y)
        return edge