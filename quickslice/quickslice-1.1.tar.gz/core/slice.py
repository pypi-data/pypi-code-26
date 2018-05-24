from PIL import Image
import numpy as np
import math

import colormaps

temporary_transparent_pixel = -1

def read_cct_file(file):
    lines = [line.rstrip('\n') for line in open(file)]
    info = list(map(int, lines.pop(0).split(',')))
    voxels = []
    while len(lines)>0:
        row = np.fromstring(lines.pop(0), dtype=int, sep=',')
        slice = np.reshape(row, (info[1], info[0]))
        voxels.append(slice)
    volume = np.asarray(voxels)
    return volume


def get_slice(volume, plane, threshold, transparency):
    slice = None
    variable = plane[:1]
    value = float(plane[1:])
    if variable == 'x':
        x = int(math.ceil(value*(volume.shape[2]-1)))
        slice = volume[:,:,x]
    elif variable == 'y':
        y = int(math.ceil(value*(volume.shape[1]-1)))
        slice = volume[:,y,:]
    elif variable == 'z':
        z = int(math.ceil(value*(volume.shape[0]-1)))
        slice = volume[z,:,:]
    if threshold is not None:
        if transparency:
            slice[np.where(slice<threshold[0])] = temporary_transparent_pixel
            slice[np.where(slice>threshold[1])] = temporary_transparent_pixel
        else:
            slice = np.clip(slice, threshold[0], threshold[1])
    return slice


def rectify_transparency(slice):
    alpha_slice = np.zeros_like(slice)
    alpha_slice[np.where(slice != temporary_transparent_pixel)] = 255
    slice[np.where(slice == temporary_transparent_pixel)] = 0
    rgba_slice = np.zeros((slice.shape[0], slice.shape[1], 4), 'uint8')
    rgba_slice[..., 0] = slice
    rgba_slice[..., 1] = slice
    rgba_slice[..., 2] = slice
    rgba_slice[..., 3] = alpha_slice
    return rgba_slice


def apply_colormap(slice, threshold, colormap):
    colorscale = colormaps.colorscales.get(colormap)
    if colorscale:
        lerp_range = range(threshold[0], threshold[1] + 1)
        max_index = threshold[1]-threshold[0]
        replacer = []
        reds = np.zeros_like(slice)
        blues = np.zeros_like(slice)
        greens = np.zeros_like(slice)
        alphas = np.zeros_like(slice)
        for i in lerp_range:
            replace_from = i
            replace_to_index = (i-threshold[0])*(len(colorscale)-1)/max_index
            upper_index = int(math.ceil(replace_to_index))
            lower_index = int(math.floor(replace_to_index))
            multiplier = replace_to_index - lower_index
            upper_color = np.asarray(colorscale[upper_index])
            lower_color = np.asarray(colorscale[lower_index])
            this_color = np.rint(lower_color + multiplier*(upper_color-lower_color)).astype(int)
            indices = np.where(slice == i)
            reds[indices[0], indices[1]] = this_color[0]
            greens[indices[0], indices[1]] = this_color[1]
            blues[indices[0], indices[1]] = this_color[2]
        alphas[np.where(slice != temporary_transparent_pixel)] = 255
        rgba_slice = np.zeros((slice.shape[0], slice.shape[1], 4), 'uint8')
        rgba_slice[..., 0] = reds
        rgba_slice[..., 1] = greens
        rgba_slice[..., 2] = blues
        rgba_slice[..., 3] = alphas
        return rgba_slice
    return False


def slice(file, plane, threshold, colormap, transparent):
    volume = read_cct_file(file)
    slice = get_slice(volume, plane, threshold, transparent)
    img = None
    if slice is None:
        return False, 'Cannot generate slice'
    if colormap:
        image_slice = apply_colormap(slice, threshold, colormap)
        if type(image_slice) == bool:
            return False, 'Colormap not found'
        img = Image.fromarray(image_slice, 'RGBA')
    elif transparent:
        image_slice = rectify_transparency(slice)
        img = Image.fromarray(image_slice, 'RGBA')
    else:
        img = Image.fromarray(slice.astype(np.uint8), 'L')
    img.save('output.png')
    img.show()
    return True, 'Finished Slice Generation'
