import cv2
import numpy as np


def find_outer_corner(thresholding_img):
    """
    :param thresholding_img: thresholding image
    :return: four corners of image area that is not zero, top, right, bottom, left
    """
    rows, cols, _ = np.nonzero(thresholding_img)

    min_x_idx = np.argmin(cols)
    min_y_idx = np.argmin(rows)
    max_x_idx = np.argmax(cols)
    max_y_idx = np.argmax(rows)

    top_pnt = [cols[min_y_idx], rows[min_y_idx]]
    left_pnt = [cols[min_x_idx], rows[min_x_idx]]
    right_pnt = [cols[max_x_idx], rows[max_x_idx]]
    bottom_pnt = [cols[max_y_idx], rows[max_y_idx]]

    return top_pnt, right_pnt, bottom_pnt, left_pnt


def put_text(image, txt, position=(30, 30), font_face=cv2.FONT_HERSHEY_SIMPLEX,
             font_scale=0.65, color=(0, 255, 0), thickness=2):
    """
    :param image:       image to draw
    :param txt:         text to put on image
    :param position:    bottom-left of the text on the image
    :param font_face:   font type
    :param font_scale:  font scale factor that is multiplied by the font-specific base size
    :param color:       font colour
    :param thickness:   thickness of the lines used to draw a text
    :return:
    """
    cv2.putText(image, txt, position, font_face, font_scale, color, thickness)
    return image


def images2video(images_dir, fps, output_video_path):
    from img_utils.files import images_in_dir
    image_files = images_in_dir(images_dir)
    if len(image_files) > 0:
        im = cv2.imread(image_files[0])
        height, width, _ = im.shape
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        for im_f in image_files:
            im = cv2.imread(im_f)
            out.write(im)

        out.release()
