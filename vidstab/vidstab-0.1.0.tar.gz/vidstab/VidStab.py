"""VidStab: a class for stabilizing video files"""

import cv2
import numpy as np
import pandas as pd
import imutils.feature.factories as kp_factory
from progress.bar import IncrementalBar
import matplotlib.pyplot as plt


class VidStab:
    """A class for stabilizing video files

    The VidStab class can be used to stabilize videos using functionality from OpenCV.
    Input video is read from file, put through stabilization process, and written to
    an output file.

    The process calculates optical flow (cv2.calcOpticalFlowPyrLK) from frame to frame using
    keypoints generated by the keypoint method specified by the user.  The optical flow will
    be used to generate frame to frame transformations (cv2.estimateRigidTransform).
    Transformations will be applied (cv2.warpAffine) to stabilize video.

    This class is based on the work presented by Nghia Ho at: http://nghiaho.com/?p=2093

    Args:
        kp_method (str): String of the type of keypoint detector to use. Available options:
                           ["GFTT", "BRISK", "DENSE", "FAST", "HARRIS",
                            "MSER", "ORB", "SIFT", "SURF", "STAR"]
        args:            The :class:`FileStorage` instance to wrap
        kwargs:          Keyword arguments for keypoint detector

    Attributes:
        kp_method:              a string naming the keypoint detector being used
        kp_detector:            the keypoint detector object being used
        trajectory:             a pandas DataFrame showing the trajectory of the input video
        smoothed_trajectory:    a pandas DataFrame showing the smoothed trajectory of the input video
        transforms:             a 2d numpy array storing the transformations used from frame to frame
    """

    def __init__(self, kp_method='GFTT', *args, **kwargs):
        """instantiate VidStab class

        :param kp_method: String of the type of keypoint detector to use. Available options:
                        ["GFTT", "BRISK", "DENSE", "FAST", "HARRIS",
                         "MSER", "ORB", "SIFT", "SURF", "STAR"]
        :param args: Positional arguments for keypoint detector.
        :param kwargs: Keyword arguments for keypoint detector.
        """
        self.kp_method = kp_method
        # use original defaults in http://nghiaho.com/?p=2093 if GFTT with no additional (kw)args
        if kp_method == 'GFTT' and args == () and kwargs == {}:
            self.kp_detector = kp_factory.FeatureDetector_create('GFTT',
                                                                 maxCorners=200,
                                                                 qualityLevel=0.01,
                                                                 minDistance=30.0,
                                                                 blockSize=3)
        else:
            self.kp_detector = kp_factory.FeatureDetector_create(kp_method, *args, **kwargs)

        self.trajectory = None
        self.smoothed_trajectory = None
        self.transforms = None
        self._raw_transforms = None

    def _gen_trajectory(self, input_path, show_progress=True):
        """Generate frame transformations to apply for stabilization

        :param input_path: Path to input video to stabilize.
        Will be read with cv2.VideoCapture; see opencv documentation for more info.
        :param show_progress: Should a progress bar be displayed to console?
        :return: Nothing is returned.  The result is added as trajectory attribute.
        """

        # set up video capture
        vid_cap = cv2.VideoCapture(input_path)
        frame_count = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # read first frame
        _, prev_frame = vid_cap.read()
        # convert to gray scale
        prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        # initialize storage
        prev_to_cur_transform = []
        if show_progress:
            print('Progress bar is based on cv2.CAP_PROP_FRAME_COUNT which may be inaccurate')
            bar = IncrementalBar('Generating Transforms', max=(frame_count - 1), suffix='%(percent)d%%')
        # iterate through frame count
        for _ in range(frame_count - 1):
            # read current frame
            grabbed_frame, cur_frame = vid_cap.read()
            if not grabbed_frame:
                print('No frame grabbed. Exiting process.')
                break
            # convert to gray
            cur_frame_gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)
            # detect keypoints
            prev_kps = self.kp_detector.detect(prev_frame_gray)
            prev_kps = np.array([kp.pt for kp in prev_kps], dtype='float32').reshape(-1, 1, 2)
            # calc flow of movement
            cur_kps, status, err = cv2.calcOpticalFlowPyrLK(prev_frame_gray, cur_frame_gray, prev_kps, None)
            # storage for keypoints with status 1
            prev_matched_kp = []
            cur_matched_kp = []
            for i, matched in enumerate(status):
                # store coords of keypoints that appear in both
                if matched:
                    prev_matched_kp.append(prev_kps[i])
                    cur_matched_kp.append(cur_kps[i])
            # estimate partial transform
            transform = cv2.estimateRigidTransform(np.array(prev_matched_kp),
                                                   np.array(cur_matched_kp),
                                                   False)
            if transform is not None:
                # translation x
                dx = transform[0, 2]
                # translation y
                dy = transform[1, 2]
                # rotation
                da = np.arctan2(transform[1, 0], transform[0, 0])
            else:
                dx = dy = da = 0

            # store transform
            prev_to_cur_transform.append([dx, dy, da])
            # set current frame to prev frame for use in next iteration
            prev_frame_gray = cur_frame_gray[:]
            if show_progress:
                bar.next()
        bar.finish()

        # convert list of transforms to array
        self._raw_transforms = np.array(prev_to_cur_transform)

        # cumsum of all transforms for trajectory
        trajectory = np.cumsum(prev_to_cur_transform, axis=0)

        # convert trajectory array to df
        self.trajectory = pd.DataFrame(trajectory)

    def gen_transforms(self, input_path, smoothing_window=30, re_calc_trajectory=False, show_progress=True):
        """Generate frame transformations to apply for stabilization

        :param input_path: Path to input video to stabilize.
        Will be read with cv2.VideoCapture; see opencv documentation for more info.
        :param smoothing_window: window size to use when smoothing trajectory
        :param re_calc_trajectory: Force re-calculation of trajectory?
        Trajectory is a deterministic process that requires iterating through every frame of input video.
        It should not need to be recalculated unless using the same VidStab object on multiple videos.
        :param show_progress: Should a progress bar be displayed to console?
        :return: Nothing is returned.  The results are added as attributes: trajectory, smoothed_trajectory, & transforms
        """

        if re_calc_trajectory or self.trajectory is None:
            self._gen_trajectory(input_path=input_path, show_progress=show_progress)

        # rolling mean to smooth
        smoothed_trajectory = self.trajectory.rolling(window=smoothing_window, center=False).mean()
        # back fill nas caused by smoothing and store
        self.smoothed_trajectory = smoothed_trajectory.fillna(method='bfill')
        self.transforms = np.array(self._raw_transforms + (self.smoothed_trajectory - self.trajectory))

    def apply_transforms(self, input_path, output_path, output_fourcc='MJPG',
                         border_type='black', border_size=0, layer_func=None, show_progress=True):
        """Apply frame transformations to apply for stabilization

        :param input_path: Path to input video to stabilize.
        Will be read with cv2.VideoCapture; see opencv documentation for more info.
        :param output_path: Path to save stabilized video.
        Will be written with cv2.VideoWriter; see opencv documentation for more info.
        :param output_fourcc: FourCC is a 4-byte code used to specify the video codec.
        The list of available codes can be found in fourcc.org.  See cv2.VideoWriter_fourcc documentation for more info.
        :param border_type: How to handle border when rotations are needed to stabilize
                           ['black', 'reflect', 'replicate']
        :param border_size: size of border in output
        :param layer_func: Function to layer frames in output.
        The function should accept 2 parameters: foreground & background.
        The current frame of video will be passed as foreground, the previous frame will be passed as the background
        (after the first frame of output the background will be the output of layer_func on the last iteration)
        :param show_progress: Should a progress bar be displayed to console?
        :return: Nothing is returned.  Output is written to `output_path`.
        """
        # initialize transformation matrix
        transform = np.zeros((2, 3))
        # setup video cap
        vid_cap = cv2.VideoCapture(input_path)
        frame_count = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(vid_cap.get(cv2.CAP_PROP_FPS))

        writer = None

        if show_progress:
            bar = IncrementalBar('Applying Transforms', max=(frame_count - 1), suffix='%(percent)d%%')

        if border_type not in ['black', 'reflect', 'replicate', 'trail']:
            raise ValueError('Invalid border type')

        border_modes = {'black': cv2.BORDER_CONSTANT,
                        'reflect': cv2.BORDER_REFLECT,
                        'replicate': cv2.BORDER_REPLICATE}
        border_mode = border_modes[border_type]

        # loop through frame count
        for i in range(self.transforms.shape[0]):
            # read current frame
            _, frame = vid_cap.read()

            if writer is None:
                # set output and working dims
                h, w = frame.shape[:2]

                write_h = h + 2 * border_size
                write_w = w + 2 * border_size

                if border_size < 0:
                    neg_border_size = 100 + abs(border_size)
                    border_size = 100
                else:
                    neg_border_size = 0

                h += 2 * border_size
                w += 2 * border_size
                # setup video writer
                writer = cv2.VideoWriter(output_path,
                                         cv2.VideoWriter_fourcc(*output_fourcc), fps, (write_w, write_h), True)

            # build transformation matrix
            transform[0, 0] = np.cos(self.transforms[i][2])
            transform[0, 1] = -np.sin(self.transforms[i][2])
            transform[1, 0] = np.sin(self.transforms[i][2])
            transform[1, 1] = np.cos(self.transforms[i][2])
            transform[0, 2] = self.transforms[i][0]
            transform[1, 2] = self.transforms[i][1]
            # apply transform
            bordered_frame = cv2.copyMakeBorder(frame,
                                                top=border_size * 2,
                                                bottom=border_size * 2,
                                                left=border_size * 2,
                                                right=border_size * 2,
                                                borderType=border_mode,
                                                value=[0, 0, 0])
            transformed = cv2.warpAffine(bordered_frame,
                                         transform,
                                         (w + border_size * 2, h + border_size * 2),
                                         borderMode=border_mode)

            if layer_func is not None:
                if i > 0:
                    transformed = layer_func(transformed, prev_frame)

                prev_frame = transformed[:]

            buffer = border_size + neg_border_size
            transformed = transformed[buffer:(transformed.shape[0] - buffer),
                                      buffer:(transformed.shape[1] - buffer)]

            # write frame to output video
            writer.write(transformed)
            if show_progress:
                bar.next()
        writer.release()
        bar.finish()

    def stabilize(self, input_path, output_path, output_fourcc='MJPG',
                  border_type='black', border_size=0, layer_func=None, smoothing_window=30, show_progress=True):
        """read video, perform stabilization, & write output to file

        :param input_path: Path to input video to stabilize.
        Will be read with cv2.VideoCapture; see opencv documentation for more info.
        :param output_path: Path to save stabilized video.
        Will be written with cv2.VideoWriter; see opencv documentation for more info.
        :param output_fourcc: FourCC is a 4-byte code used to specify the video codec.
        The list of available codes can be found in fourcc.org.  See cv2.VideoWriter_fourcc documentation for more info.
        :param border_type: how to handle border when rotations are needed to stabilize
                       ['black', 'reflect', 'replicate']
        :param border_size: size of border in output
        :param layer_func: Function to layer frames in output.
        The function should accept 2 parameters: foreground & background.
        The current frame of video will be passed as foreground, the previous frame will be passed as the background
        (after the first frame of output the background will be the output of layer_func on the last iteration)
        :param smoothing_window: window size to use when smoothing trajectory
        :param show_progress: Should a progress bar be displayed to console?
        :return: Nothing is returned.  Output of stabilization is written to `output_path`.

        >>> from vidstab.VidStab import VidStab
        >>> stabilizer = VidStab()
        >>> stabilizer.stabilize(input_path='input_video.mov', output_path='stable_video.avi')

        >>> stabilizer = VidStab(kp_method = 'ORB')
        >>> stabilizer.stabilize(input_path='input_video.mov', output_path='stable_video.avi')
        """

        # generate transforms if needed
        if self.transforms is None:
            self.gen_transforms(input_path=input_path,
                                smoothing_window=smoothing_window,
                                show_progress=True)

        # apply transformations for stabilization
        self.apply_transforms(input_path=input_path,
                              output_path=output_path,
                              output_fourcc=output_fourcc,
                              border_type=border_type,
                              border_size=border_size,
                              layer_func=layer_func,
                              show_progress=show_progress)

    def plot_trajectory(self):
        """Plot video trajectory

        Create a plot of the video's trajectory & smoothed trajectory.
        Separate subplots are used to show the x and y trajectory.

        :return: tuple of matplotlib objects (Figure, (AxesSubplot, AxesSubplot))

        >>> from vidstab import VidStab
        >>> import matplotlib.pyplot as plt
        >>> stabilizer = VidStab()
        >>> stabilizer.gen_transforms(input_path='input_video.mov')
        >>> stabilizer.plot_trajectory()
        >>> plt.show()
        """

        if self.transforms is None:
            raise AttributeError('No trajectory to plot. '
                                 'Use methods: gen_transforms or stabilize to generate the trajectory attributes')

        with plt.style.context('ggplot'):
            fig, (ax1, ax2) = plt.subplots(2, sharex=True)

            # x trajectory
            ax1.plot(self.trajectory[0], label='Trajectory')
            ax1.plot(self.smoothed_trajectory[0], label='Smoothed Trajectory')
            ax1.set_ylabel('dx')

            # y trajectory
            ax2.plot(self.trajectory[1], label='Trajectory')
            ax2.plot(self.smoothed_trajectory[1], label='Smoothed Trajectory')
            ax2.set_ylabel('dy')

            handles, labels = ax2.get_legend_handles_labels()
            fig.legend(handles, labels, loc='upper right')

            plt.xlabel('Frame Number')

            fig.suptitle('Video Trajectory', x=0.15, y=0.96, ha='left')
            fig.canvas.set_window_title('Trajectory')

            return fig, (ax1, ax2)

    def plot_transforms(self):
        """Plot stabilizing transforms

        Create a plot of the transforms used to stabilize the input video.
        Plots x & y transforms (dx & dy) in a separate subplot than angle transforms (da).

        :return: tuple of matplotlib objects (Figure, (AxesSubplot, AxesSubplot))

        >>> from vidstab import VidStab
        >>> import matplotlib.pyplot as plt
        >>> stabilizer = VidStab()
        >>> stabilizer.gen_transforms(input_path='input_video.mov')
        >>> stabilizer.plot_transforms()
        >>> plt.show()
        """
        if self.transforms is None:
            raise AttributeError('No transforms to plot. '
                                 'Use methods: gen_transforms or stabilize to generate the transforms attribute')

        with plt.style.context('ggplot'):
            fig, (ax1, ax2) = plt.subplots(2, sharex=True)

            ax1.plot(self.transforms[:, 0], label='delta x', color='C0')
            ax1.plot(self.transforms[:, 1], label='delta y', color='C1')
            ax1.set_ylabel('Delta Pixels', fontsize=10)

            ax2.plot(self.transforms[:, 2], label='delta angle', color='C2')
            ax2.set_ylabel('Delta Degrees', fontsize=10)

            handles1, labels1 = ax1.get_legend_handles_labels()
            handles2, labels2 = ax2.get_legend_handles_labels()
            fig.legend(handles1 + handles2,
                       labels1 + labels2,
                       loc='upper right',
                       ncol=1)

            plt.xlabel('Frame Number')

            fig.suptitle('Transformations for Stabilizing', x=0.15, y=0.96, ha='left')
            fig.canvas.set_window_title('Transforms')

            return fig, (ax1, ax2)
