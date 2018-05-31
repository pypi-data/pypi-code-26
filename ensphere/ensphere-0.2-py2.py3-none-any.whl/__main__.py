#!/usr/bin/env python

# wants python-xmp-toolkit, PIL
# brew install exempi
import imagesize
from libxmp import XMPFiles, consts
import argparse  as ap
import logging
from ensphere import __version__

GPano="http://ns.google.com/photos/1.0/panorama/"
namespace=["UsePanoramaViewer",
"CaptureSoftware",
"StitchingSoftware",
"ProjectionType",
"PoseHeadingDegrees",
"PosePitchDegrees",
"PoseRollDegrees",
"InitialViewHeadingDegrees",
"InitialViewPitchDegrees",
"InitialViewRollDegrees",
"InitialHorizontalFOVDegrees",
"FirstPhotoDate",
"LastPhotoDate",
"SourcePhotosCount",
"ExposureLockUsed",
"CroppedAreaImageWidthPixels",
"CroppedAreaImageHeightPixels",
"FullPanoWidthPixels",
"FullPanoHeightPixels",
"CroppedAreaLeftPixels",
"CroppedAreaTopPixels",
"InitialCameraDolly",]

def getoptions():
    parser = ap.ArgumentParser(description='Add XMP metadata for PanoSphere in the pictures. (version {0})'.format(__version__), prog='ensphere')
    parser.add_argument('--version', '-V', action='version', version='%(prog)s {0}'.format(__version__))
    parser.add_argument('--set', '-s', nargs = 1, dest='vars', metavar='UsePanoramaViewer=True,ProjectionType=equirectangular', default=[], help="Set metadata for PanSpheres. Available variables: {0}".format(namespace))
    parser.add_argument('filenames', nargs='+',
                       help='File names (JPEG files only)')
    return parser.parse_args()
    



def main():
    options = getoptions()
    logging.basicConfig(level=logging.INFO,
                        format="%(levelname)s %(message)s")
    logger = logging.getLogger()
    vars = {'UsePanoramaViewer': 'True',
            'ProjectionType':    'equirectangular',
            }
    for vstr in options.vars:
        for elem in vstr.split(','):
            key,value = elem.split('=')
            if key in namespace:
                vars[key] = value
            else:
                logger.warn("Key {0} is invalid.".format(key))
    for filename in options.filenames:
        logger.info("Filename: {0}".format(filename))
        xmpfile = XMPFiles( file_path=filename, open_forupdate=True )
        xmp = xmpfile.get_xmp()
        try:
            assert xmp is not None
        except AssertionError:
            logger.warn("Metadata is not available for {0}.".format(filename))
            continue
        xmp.register_namespace(GPano, 'GPano')

        width, height = imagesize.get(filename)
        width  = "{0}".format(width)
        height = "{0}".format(height)
        # width  = xmp.get_property(consts.XMP_NS_EXIF, 'PixelXDimension' )
        # height = xmp.get_property(consts.XMP_NS_EXIF, 'PixelYDimension' )
        # assert width  != '', "No width read."
        # assert height != '', "No height read."
        for name in namespace:
            if name in vars:
                if xmp.does_property_exist(GPano, name):
                    logger.info("Overwrite: {0} {1}->{2}".format(name, xmp.get_property(GPano, name), vars[name]))
                else:
                    logger.info("Set: {0} {1}".format(name, vars[name]))
                xmp.set_property(GPano, name, vars[name])
            elif name in ['FullPanoWidthPixels','CroppedAreaImageWidthPixels']:
                if not xmp.does_property_exist(GPano, name):
                    logger.info("Set default: {0} {1}".format(name, width))
                    xmp.set_property(GPano, name, width)
            elif name in ['FullPanoHeightPixels','CroppedAreaImageHeightPixels']:
                if not xmp.does_property_exist(GPano, name):
                    logger.info("Set default: {0} {1}".format(name, height))
                    xmp.set_property(GPano, name, height)
        xmpfile.put_xmp(xmp)
        xmpfile.close_file()

if __name__ == "__main__":
    main()
