import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from inception import Inception3
from PIL import Image

use_gpu = True
dtype = torch.float32

device = torch.device('cuda') if use_gpu and torch.cuda.is_available() else torch.device('cpu')
print('Using device: ', device)


def load_model(model_path, device=device):
    print('pytorch_classifier.py: Loading model...')
    num_classes = 8142

    checkpoint = torch.load(model_path, map_location=device)

    # reference: https://github.com/macaodha/inat_comp_2018/blob/master/train_inat.py
    model = Inception3(transform_input=True)
    model.fc = nn.Linear(2048, num_classes)
    model.aux_logits = False

    model.load_state_dict(checkpoint['state_dict'])
    model = model.to(device=device, dtype=dtype)
    model.eval()  # set model to evaluation mode
    print('pytorch_classifier.py: model loaded.')
    return model


def classify(model, image_bytes):
    img = Image.open(image_bytes)

    image_np = np.asarray(img, np.uint8)

    # swap color axis because numpy image is H x W x C, torch image is C X H X W
    image_np = image_np.transpose((2, 0, 1))
    image_np = image_np[:3, :, :] # Remove the alpha channel
    image_np = np.expand_dims(image_np, axis=0)  # add a batch dimension
    img_input = torch.from_numpy(image_np).type(torch.float32).to(device=device, dtype=dtype)

    with torch.no_grad():
        scores = model(img_input)

    scores = scores.cpu().data.numpy()
    clss = np.argmax(scores[0])
    return 'Most likely category is {}'.format(str(clss))
