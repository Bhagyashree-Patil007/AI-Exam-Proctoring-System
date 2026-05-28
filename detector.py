import cv2
import numpy as np

class YOLODetector:

    def __init__(self):

        self.net = cv2.dnn.readNet(
            "yolov4-tiny.weights",
            "yolov4-tiny.cfg"
        )

        with open("coco.names", "r") as f:
            self.classes = [line.strip() for line in f.readlines()]

        layer_names = self.net.getLayerNames()

        self.output_layers = [
            layer_names[i - 1]
            for i in self.net.getUnconnectedOutLayers()
        ]

    def detect_objects(self, frame):

        height, width, channels = frame.shape

        blob = cv2.dnn.blobFromImage(
            frame,
             1 / 255.0,
            (416, 416),
            swapRB=True,
            crop=False
        )

        self.net.setInput(blob)

        outputs = self.net.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []

        for output in outputs:

            for detection in output:

                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)

                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(
            boxes,
            confidences,
            0.5,
            0.4
        )

        detections = []

        if len(indexes) > 0:

            for i in indexes.flatten():

                x, y, w, h = boxes[i]
                detections.append({
                    "label": self.classes[class_ids[i]],
                    "confidence": confidences[i],
                    "box": (x, y, w, h)
                })

        return detections