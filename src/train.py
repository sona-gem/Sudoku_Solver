
import os
import random
import numpy as np
import cv2
from scipy.ndimage import rotate as ndrotate, zoom
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
from tensorflow.keras.datasets import mnist 
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization)
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


def load_mnist():
    #x_train - trainign images, y_train - training labels
    (x_train, y_train), (x_test , y_test) = mnist.load_data()
    
    #normalize the pixel values from the range of (0 to 255) to (0 to 1)
    x_train = x_train/255.0
    x_test = x_test / 255.0


    x_train = x_train.reshape(-1,28,28,1)   #adds channel dimensions
    x_test  = x_test.reshape(-1, 28, 28, 1)
    
    train_mask = y_train != 0       #eg [0,1,7,0,3] => [False, True, True, False, True]
    test_mask = y_test != 0

    x_train, y_train = x_train[train_mask] , y_train[train_mask]  #remove dig 0 samples
    x_test, y_test = x_test[test_mask], y_test[test_mask]

    print(f"MNIST  — train: {len(x_train)}, test: {len(x_test)}")
    return x_train, y_train, x_test, y_test


def get_system_fonts():
    font_dir = "C:/Windows/Fonts"
    candidates = [
            "arial.ttf", "arialbd.ttf",       # Arial regular + bold
            "times.ttf", "timesbd.ttf",        # Times New Roman
            "cour.ttf",  "courbd.ttf",         # Courier
            "verdana.ttf", "verdanab.ttf",     # Verdana
            "calibri.ttf", "calibrib.ttf",     # Calibri
            "georgia.ttf",                     # Georgia
        ]

    fonts = []
    for f in candidates:
        path = os.path.join(font_dir, f)
        if os.path.exists(path):
            fonts.append(path)
    if not fonts:
        print("  No system fonts found — using PIL default font")

    return fonts


def render_digits(digit, font_path, font_size, canvas_size=28):
    img = Image.new("L", (canvas_size, canvas_size), color =0)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font  = ImageFont.load_default()
    text = str(digit)       #convert dig to text

    #get bounding box and center dig
    bbox = draw.textbbox((0,0), text, font = font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x= (canvas_size - text_w) // 2 -bbox[0]         #conpute center coordinates
    y = (canvas_size - text_h) // 2 - bbox[1]

    draw.text((x,y), text, fill = 255, font = font) #draw white digit
    arr = np.array(img, dtype = "float32")/255.0        #convert PIL image to normalized numpy array

    if arr.max() < 0.1:
        raise ValueError(f"Blank render for digit {digit}")
    return arr          



def generate_synthetic_digits(samples_per_digit =800):
    fonts = get_system_fonts()

    font_sizes = list(range(14,24))

    imgs = []
    labels = []

    for digit in range(1,10):
        count = 0
        attempts = 0

        while count < samples_per_digit and attempts < samples_per_digit*10:
            attempts += 1
            if fonts: 
                font_path = random.choice(fonts)
            else:
                font_path = None
            
            font_size = random.choice(font_sizes)

            try:
                img = render_digits(digit, font_path, font_size)    #crests digit image
            except Exception:
                continue

            if img.max() < 0.1:     #skip if image is blank
                continue

            imgs.append(img.reshape(28,28,1))
            labels.append(digit)
            count += 1

        print(f"   Digit {digit}: {count} synthetic samples")
    
    imgs = np.array(imgs, dtype = "float32")
    labels = np.array(labels, dtype="int32")

    return imgs, labels

#apply random augmentation to 28x28 image  => help make training data resmble suduko photos     
def augment_digits(img_2d, label):
    canvas = img_2d.copy()

    #random rotations +-10 degree
    angle = np.random.uniform(-10,10)  
    canvas = ndrotate(canvas, angle, reshape=False)

    # Random shift +/-2px
    shift_x = np.random.randint(-2, 3)
    shift_y = np.random.randint(-2, 3)
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    canvas = cv2.warpAffine(canvas, M, (28, 28))

    # Random zoom in/out slightly
    factor = np.random.uniform(0.85, 1.15)
    zoomed = zoom(canvas, factor)

    # Crop or pad back to 28x28
    zh, zw = zoomed.shape
    if zh > 28:
        start = (zh - 28) // 2
        zoomed = zoomed[start:start+28, start:start+28]
    else:
        pad_h = (28 - zh) // 2
        pad_w = (28 - zw) // 2
        zoomed = np.pad(zoomed, ((pad_h, 28-zh-pad_h),(pad_w, 28-zw-pad_w)))
    canvas = zoomed

    # Small brightness variation (simulates lighting)
    brightness = np.random.uniform(0.8, 1.2)
    canvas = np.clip(canvas * brightness, 0, 1)

    return canvas.reshape(28, 28, 1).astype("float32")



def augment_dataset(x,y,multiplier=2):
    extra_imgs = []
    extra_labels = []

    for i in range(len(x)):
        img  = x[i].reshape(28,28)
        label = y[i]

        for _ in range(multiplier): #creates multiple augmented versiosn of the same img
            aug = augment_digits(img, label)
            extra_imgs.append(aug)
            extra_labels.append(label)

    extra_imgs = np.array(extra_imgs, dtype = "float32")
    extra_labels = np.array(extra_labels, dtype ="int32")


    x_aug = np.concatenate([x, extra_imgs])
    y_aug = np.concatenate([y, extra_labels])

    idx = np.random.permutation(len(x_aug))     #shiffles the dataset
    return x_aug[idx], y_aug[idx]


#CNN architecture
def build_model():
    model = Sequential([
        #block 1
        Conv2D(32, (3,3), activation ="relu", padding = "same", input_shape=(28,28,1)),
        BatchNormalization(),
        Conv2D(32, (3,3), activation="relu", padding= "same"),
        MaxPooling2D(),
        Dropout(0.25),      #randomly disables 25 neurons

        #block 2
        Conv2D(64, (3,3), activation="relu", padding="same"),
        BatchNormalization(),
        Conv2D(64, (3,3), activation="relu", padding="same"),
        MaxPooling2D(),
        Dropout(0.25),

        #classifier head
        Flatten(),      #converts feature map to vectors
        Dense(256, activation="relu"),
        BatchNormalization(),
        Dropout(0.5),

        #10 o/p (we use indices 1-9 , 0 is unused)
        Dense(10 , activation="softmax")

    ])

    model.compile(optimizer = "adam", loss= "sparse_categorical_crossentropy", metrics = ["accuracy"])

    return model


def train():
    # load MNIST
    x_mnist, y_mnist, x_test, y_test = load_mnist()

    # generate synthetic printed digits
    x_synth, y_synth = generate_synthetic_digits(samples_per_digit=800)

    #combine both
    x_combined = np.concatenate([x_mnist, x_synth])
    y_combined  = np.concatenate([y_mnist, y_synth])
    print(f"Combined size before augmentation: {len(x_combined)}")

    #augment dataset
    x_train, y_train = augment_dataset(x_combined, y_combined, multiplier=2)
    print(f"Final training size: {len(x_train)}")

    #train
    model = build_model()
    model.summary()


    #if validation accuracy doesn't improve fro 3 epochs => stop training
    callbacks = [
        EarlyStopping(
            monitor="val_accuracy",
            patience=3,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            "models/sudoku_digit_model.keras",
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1
        )
    ]

    model.fit(
        x_train, y_train,
        epochs=20,
        batch_size=64,
        validation_split=0.1,
        callbacks=callbacks
    )

    #evaluate
    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"Test accuracy : {acc*100:.2f}%")
    print(f"Model saved   : models/sudoku_digit_model.keras")

    return model


if __name__ == "__main__":
    train()
        



