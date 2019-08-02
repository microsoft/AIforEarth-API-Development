import tensorflow as tf
import numpy as np
import PIL.Image as Image
import PIL.ImageColor as ImageColor
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont


# Core detection functions


def load_model(checkpoint):
    """Load a detection model (i.e., create a graph) from a .pb file.

    Args:
        checkpoint: .pb file of the model.

    Returns: the loaded graph.

    """
    print('tf_detector.py: Loading graph...')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(checkpoint, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
    print('tf_detector.py: Detection graph loaded.')

    return detection_graph


def open_image(image_bytes):
    """ Open an image in binary format using PIL.Image and convert to RGB mode
    Args:
        image_bytes: an image in binary format read from the POST request's body

    Returns:
        an PIL image object in RGB mode
    """
    image = Image.open(image_bytes)
    if image.mode not in ('RGBA', 'RGB'):
        raise AttributeError('Input image not in RGBA or RGB mode and cannot be processed.')
    if image.mode == 'RGBA':
        # Image.convert() returns a converted copy of this image
        image = image.convert(mode='RGB')
    return image


def generate_detections(detection_graph, image):
    """ Generates a set of bounding boxes with confidence and class prediction for one input image file.

    Args:
        detection_graph: an already loaded object detection inference graph.
        image_file: a PIL Image object

    Returns:
        boxes, scores, classes, and the image loaded from the input image_file - for one image
    """
    image_np = np.asarray(image, np.uint8)
    image_np = image_np[:, :, :3] # Remove the alpha channel

    #with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        image_np = np.expand_dims(image_np, axis=0)

        # get the operators
        image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
        box = detection_graph.get_tensor_by_name('detection_boxes:0')
        score = detection_graph.get_tensor_by_name('detection_scores:0')
        clss = detection_graph.get_tensor_by_name('detection_classes:0')
        num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        # performs inference
        (box, score, clss, num_detections) = sess.run(
            [box, score, clss, num_detections],
            feed_dict={image_tensor: image_np})

    return np.squeeze(box), np.squeeze(score), np.squeeze(clss), image  # these are lists of bboxes, scores etc


# Rendering functions


def render_bounding_boxes(boxes, scores, classes, image, label_map={}, confidence_threshold=0.5):
    """Renders bounding boxes, label and confidence on an image if confidence is above the threshold.

    Args:
        boxes, scores, classes:  outputs of generate_detections.
        image: PIL.Image object, output of generate_detections.
        label_map: optional, mapping the numerical label to a string name.
        confidence_threshold: threshold above which the bounding box is rendered.

    image is modified in place!

    """
    display_boxes = []
    display_strs = []  # list of list, one list of strings for each bounding box (to accommodate multiple labels)

    for box, score, clss in zip(boxes, scores, classes):
        if score > confidence_threshold:
            print('Confidence of detection greater than threshold: ', score)
            display_boxes.append(box)
            clss = int(clss)
            label = label_map[clss] if clss in label_map else str(clss)
            displayed_label = '{}: {}%'.format(label, round(100*score))
            display_strs.append([displayed_label])

    display_boxes = np.array(display_boxes)
    if display_boxes.shape == (0,): # no detections are above threshold
        return
    else:
        draw_bounding_boxes_on_image(image, display_boxes, display_str_list_list=display_strs)

# the following two functions are from https://github.com/tensorflow/models/blob/master/research/object_detection/utils/visualization_utils.py

def draw_bounding_boxes_on_image(image,
                                 boxes,
                                 color='LimeGreen',
                                 thickness=4,
                                 display_str_list_list=()):
  """Draws bounding boxes on image.

  Args:
    image: a PIL.Image object.
    boxes: a 2 dimensional numpy array of [N, 4]: (ymin, xmin, ymax, xmax).
           The coordinates are in normalized format between [0, 1].
    color: color to draw bounding box. Default is red.
    thickness: line thickness. Default value is 4.
    display_str_list_list: list of list of strings.
                           a list of strings for each bounding box.
                           The reason to pass a list of strings for a
                           bounding box is that it might contain
                           multiple labels.

  Raises:
    ValueError: if boxes is not a [N, 4] array
  """
  boxes_shape = boxes.shape
  if not boxes_shape:
    return
  if len(boxes_shape) != 2 or boxes_shape[1] != 4:
    raise ValueError('Input must be of size [N, 4]')
  for i in range(boxes_shape[0]):
    display_str_list = ()
    if display_str_list_list:
      display_str_list = display_str_list_list[i]
    draw_bounding_box_on_image(image, boxes[i, 0], boxes[i, 1], boxes[i, 2],
                               boxes[i, 3], color, thickness, display_str_list)


def draw_bounding_box_on_image(image,
                               ymin,
                               xmin,
                               ymax,
                               xmax,
                               color='red',
                               thickness=4,
                               display_str_list=(),
                               use_normalized_coordinates=True):
  """Adds a bounding box to an image.

  Bounding box coordinates can be specified in either absolute (pixel) or
  normalized coordinates by setting the use_normalized_coordinates argument.

  Each string in display_str_list is displayed on a separate line above the
  bounding box in black text on a rectangle filled with the input 'color'.
  If the top of the bounding box extends to the edge of the image, the strings
  are displayed below the bounding box.

  Args:
    image: a PIL.Image object.
    ymin: ymin of bounding box.
    xmin: xmin of bounding box.
    ymax: ymax of bounding box.
    xmax: xmax of bounding box.
    color: color to draw bounding box. Default is red.
    thickness: line thickness. Default value is 4.
    display_str_list: list of strings to display in box
                      (each to be shown on its own line).
    use_normalized_coordinates: If True (default), treat coordinates
      ymin, xmin, ymax, xmax as relative to the image.  Otherwise treat
      coordinates as absolute.
  """
  draw = ImageDraw.Draw(image)
  im_width, im_height = image.size
  if use_normalized_coordinates:
    (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                  ymin * im_height, ymax * im_height)
  else:
    (left, right, top, bottom) = (xmin, xmax, ymin, ymax)
  draw.line([(left, top), (left, bottom), (right, bottom),
             (right, top), (left, top)], width=thickness, fill=color)
  try:
    font = ImageFont.truetype('arial.ttf', 24)
  except IOError:
    font = ImageFont.load_default()

  # If the total height of the display strings added to the top of the bounding
  # box exceeds the top of the image, stack the strings below the bounding box
  # instead of above.
  display_str_heights = [font.getsize(ds)[1] for ds in display_str_list]
  # Each display_str has a top and bottom margin of 0.05x.
  total_display_str_height = (1 + 2 * 0.05) * sum(display_str_heights)

  if top > total_display_str_height:
    text_bottom = top
  else:
    text_bottom = bottom + total_display_str_height
  # Reverse list and print from bottom to top.
  for display_str in display_str_list[::-1]:
    text_width, text_height = font.getsize(display_str)
    margin = np.ceil(0.05 * text_height)
    draw.rectangle(
        [(left, text_bottom - text_height - 2 * margin), (left + text_width,
                                                          text_bottom)],
        fill=color)
    draw.text(
        (left + margin, text_bottom - text_height - margin),
        display_str,
        fill='black',
        font=font)
    text_bottom -= text_height - 2 * margin
