import cv2


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
            im = cv2.resize(im, (width, height))
            out.write(im)

        out.release()


if __name__ == '__main__':
    images_directory = "/Users/administrator/Documents/video/huatuo/math_2018-04-25/output"
    images2video(images_directory, 1, "huatuo-math.mp4")
