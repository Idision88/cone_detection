#!/usr/bin/env python
from net import *

import csv
import cv2
from cv_bridge import CvBridge, CvBridgeError
import os
import numpy as np
from PIL import Image
import tensorflow as tf
from skimage import color
import time

import rospy
from cone_detection.msg import Label

#Init ros.
rospy.init_node('local_network_test')
#Net parameters.
image_width = rospy.get_param('/cone/width_pixel')
image_height = rospy.get_param('/cone/height_pixel')
path_to_candidate = rospy.get_param('/candidate_path')
path_to_model = rospy.get_param('/model_path')
datasets = rospy.get_param('/neural_net/datasets')
datasets_validation = rospy.get_param('/neural_net/datasets_validation')
#Init and saver variable.
keep_prob = tf.placeholder(tf.float32)
input_placeholder = tf.placeholder(tf.float32, [None, image_height, image_width, 3])
output_placeholder = tf.placeholder(tf.float32, [None, 2])
input_placeholder_flat = tf.contrib.layers.flatten(input_placeholder)
y_true = tf.argmax(output_placeholder, dimension=1)
output_layer = fully_connected(input_placeholder_flat, 0.01, keep_prob)
y_pred = tf.argmax(tf.nn.softmax(output_layer), dimension=1)


def deleteFolderContent(path):
    for element in os.listdir(path):
        os.remove(os.path.join(path, element))

class NeuralNet:
    def __init__(self):
        #Init tf session.
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(self.session, path_to_model + getModelName(datasets) + " .cpkt")
        #Init cone list.
        image_list = []
        # Start timer.
        start_time = time.time()
        # Labeling.
        for i in range(0,1000):
            path = path_to_candidate + datasets_validation + "/" + str(i) + ".jpg"
            try:
                img = Image.open(path)
                arr = np.array(img.getdata(),np.uint8)        
                arr = arr.reshape(image_height, image_width, 3)
                image_list.append(self.labeling(arr, i))
                cv2.imwrite(path_to_candidate + "candidates/" + str(i) + ".jpg", arr)
            except:
                continue
        # Stop timer.
        end_time = time.time()
        time_difference = end_time - start_time
        print("Labeling time usage: " + str(time_difference) + " s")
        # Getting labels.
        labeled_list = []
        reader = csv.reader(open(path_to_candidate + datasets_validation + "/" + "labeling.csv"))
        for row in reader:
            image = int(row[0])
            label = int(row[1])
            labeled_list.append([image, label])
        # Accuracy by comparing lists.
        correct = 0.0;
        for element in image_list:
            index = element[0]
            for labeled_element in labeled_list:
                if(index == labeled_element[0] and element[1] == labeled_element[1]):
                    correct += 1.0
                    break
        accuracy = correct / (len(labeled_list) - 1)
        print("Labeling accuracy: " + str(accuracy))

    def labeling(self,msg,index):
        #Get image.
        image = np.zeros((1,image_height, image_width,3))
        image[0][:][:][:] =  color.rgb2lab(msg) / 255.0
        # Labeling.
        label = y_pred.eval(session=self.session,feed_dict={input_placeholder: image, keep_prob: 1.0})
        if(label == [0]):
            cv2.imwrite(path_to_candidate + "cones/" + str(index) + ".jpg", msg)
            return [index, 1]
        else:
            return [index, 0]
#------------------------------------------------------------------------

if __name__ == '__main__':
    #Delete files in candidates and cones order.
    deleteFolderContent(path_to_candidate + "candidates/")
    deleteFolderContent(path_to_candidate + "cones/")
    #Init neural net.
    neural_net = NeuralNet()