# -*- coding: utf-8 -*-
"""Neural_Style_Transfer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Oe06tLamPZMWJSkHfdhcehuLA_DrVW51
"""

# Commented out IPython magic to ensure Python compatibility.
import os
import tensorflow as tf
tf.executing_eagerly()
from tensorflow.python.keras.applications.vgg19 import VGG19
from tensorflow.python.keras.preprocessing.image import load_img, img_to_array
from tensorflow.python.keras.applications.vgg19 import preprocess_input
from tensorflow.python.keras.models import Model

import numpy as np
import matplotlib.pyplot as plt
# %matplotlib inline

from google.colab import drive
drive.mount('/content/drive')

os.chdir("/content/drive/My Drive/Neural Style Transfer")

os.listdir()

model = VGG19(
    include_top = False,
    weights = 'imagenet'
)

model.trainable = False
model.summary()

def load_and_process_image(path):
    img = load_img(path)
    img = img_to_array(img)
    img = preprocess_input(img)
    img = np.expand_dims(img, axis = 0)
    return img

def deprocess(w):
    ''' perform the inverse of the preprocessiing step 
    '''
    w[:, :, 0] += 103.939
    w[:, :, 1] += 116.779
    w[:, :, 2] += 123.68
    w = w[:, :, ::-1]

    w = np.clip(w, 0, 255).astype('uint8')
    return w

def display_image(image):
    if len(image.shape) == 4:
        img = np.squeeze(image, axis = 0)

    img = deprocess(img)
    
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(img)
    return

img = load_and_process_image('Style1.jpg')
img1 = load_and_process_image('style2.jpg')
img2 = load_and_process_image('style3.jpg')
display_image(img)

display_image(img2)

display_image(img1)

img = load_and_process_image('IMG_20200528_122818_725.jpg')
display_image(img)

#content and style models
s_layers = [
    'block1_conv1', 
    'block3_conv1', 
    'block5_conv1'
]

c_layer = 'block5_conv2'

# intermediate models
c_model = Model(
    inputs = model.input, 
    outputs = model.get_layer(content_layer).output
)

s_models = [Model(inputs = model.input, outputs = model.get_layer(layer).output) for layer in style_layers]

# Content Cost
def content_cost(content, generated):
    a_C = c_model(content)
    a_G = c_model(generated)
    cost = tf.reduce_mean(tf.square(a_C - a_G))
    return cost

def gram_matrix(X):
    channels = int(X.shape[-1])
    a = tf.reshape(X, [-1, channels])
    n = tf.shape(a)[0]
    gram = tf.matmul(a, a, transpose_a = True)
    return gram / tf.cast(n, tf.float32)

#Style cost
l = 1. / len(style_models)

def style_cost(style, generated):
    s = 0
    
    for style_model in s_models:
        a_S = style_model(style)
        a_G = style_model(generated)
        GS = gram_matrix(a_S)
        GG = gram_matrix(a_G)
        current_cost = tf.reduce_mean(tf.square(GS - GG))
        s += current_cost * l
    
    return s

#Training
import time

generated_images = []

def training_loop(content_img_path, style_img_path, iterations = 200, a = 15., b = 25.):
    # initialise
    content = load_and_process_image(content_img_path)
    style = load_and_process_image(style_img_path)
    generated = tf.Variable(content, dtype = tf.float32)
    
    opt = tf.optimizers.Adam(learning_rate = 7.)
    
    best_cost = 1e12+0.1
    best_image = None
    
    start_time = time.time()
    
    for i in range(iterations):
        
        with tf.GradientTape() as tape:
            c = content_cost(content, generated)
            s = style_cost(style, generated)
            total = a * c + b * s
        
        grads = tape.gradient(total, generated)
        opt.apply_gradients([(grads, generated)])
        
        if total < best_cost:
            best_cost = total
            best_image = generated.numpy()
        
        if i % int(iterations/10) == 0:
            time_taken = time.time() - start_time
            print('Cost at {}: {}. Time elapsed: {}'.format(i, total, time_taken))
            generated_images.append(generated.numpy())
        
    return best_image

final = training_loop('IMG_20200528_122818_725.jpg','Style1.jpg')

#plot the result
plt.figure(figsize = (12, 12))

for i in range(10):
    plt.subplot(5, 2, i + 1)
    display_image(generated_images[i])
plt.show()

display_image(final)

