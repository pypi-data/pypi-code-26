from thicket.ffmpeg_wrapper.probe import video_length, video_info
from thicket.ffmpeg_wrapper.utils import is_video
from thicket.files import File


class VideoFile(File):

    type = 'video'

    @staticmethod
    def is_video(path):
        return is_video(path)

    def length(self, only_format=True):
        if only_format:
            info = self.video_length()
            if info.get('format_length'):
                return info.get('format_length')
            else:
                return 0
        else:
            return self.video_info()

    @property
    def video_length(self):
        return video_length(self.abspath)

    @property
    def video_info(self):
        return video_info(self.abspath)
