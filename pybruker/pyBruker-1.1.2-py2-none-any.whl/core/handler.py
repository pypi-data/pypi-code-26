


# def show(self, **kwargs):
#     """ Plotting slice of the object
#     """
#     BrainPlot.slice(self, **kwargs)
#
#
# def mosaic(self, *args, **kwargs):
#     """ Mosaic view for the object
#     """
#     fig = BrainPlot.mosaic(self, *args, **kwargs)
#
#
# def swap_axis(self, axis1, axis2):
#     """ Swap input axis with given axis of the object
#     """
#     swap_axis(self, axis1, axis2)
#
#
# def flip(self, **kwargs):
#     invert = check_invert(kwargs)
#     self._dataobj = apply_invert(self._dataobj, *invert)
#
#
# def crop(self, **kwargs):
#     crop(self, **kwargs)
#
#
# def reslice(self, ac_slice, ac_loc, slice_thickness, total_slice, axis=2):
#     """ Reslice the image with given number of slice and slice thinkness
#
#     :param ac_slice: int
#         Slice location of anterior commissure in original image
#     :param ac_loc: int
#         The slice number of anterior commissure want to be in resliced image
#     :param slice_thickness:
#         Desired slice thickness for re-sliced image
#     :param total_slice:
#         Desired total number of slice for  re-sliced image
#     :param axis:
#         Axis want to be re-sliced
#     :return:
#     """
#     down_reslice(self, ac_slice, ac_loc, slice_thickness, total_slice, axis)

#
# def padding(self, low, high, axis):
#     dataobj = self._dataobj[...]
#     dataobj = np.swapaxes(dataobj, axis, 2)
#     shape = list(dataobj.shape[:])
#     shape[2] = low
#     lower_pad = np.zeros(shape)
#     shape[2] = high
#     higher_pad = np.zeros(shape)
#     dataobj = np.concatenate((lower_pad, dataobj, higher_pad), axis=2)
#     self._dataobj = np.swapaxes(dataobj, axis, 2)
#
#
# @property
# def affine(self):
#     return self._affine

#
# def swap_axis(self, axis1, axis2):
#     if self._atlas:
#         self.atlas_obj.swap_axis(axis1, axis2)
#     self.image.swap_axis(axis1, axis2)
#
#
# def flip(self, **kwargs):
#     if self._atlas:
#         self.atlas_obj.flip(**kwargs)
#     self.image.flip(**kwargs)
#
#
# def crop(self, **kwargs):
#     if self._atlas:
#         self.atlas_obj.crop(**kwargs)
#     self.image.crop(**kwargs)
#
#
# def reslice(self, ac_slice, ac_loc, slice_thickness, total_slice, axis=2):
#     if self._atlas:
#         self.atlas_obj.reslice(self, ac_slice, ac_loc, slice_thickness, total_slice, axis=axis)
#     self.image.reslice(self, ac_slice, ac_loc, slice_thickness, total_slice, axis=axis)


# def reset_orient(imageobj, affine):
#     """ Reset to the original scanner space
#
#     :param imageobj:
#     :param affine:
#     :return:
#     """
#     imageobj.set_qform(affine)
#     imageobj.set_sform(affine)
#     imageobj.header['sform_code'] = 0
#     imageobj.header['qform_code'] = 1
#     imageobj._affine = affine
#
#
# def swap_axis(imageobj, axis1, axis2):
#     """ Swap axis of image object
#
#     :param imageobj:
#     :param axis1:
#     :param axis2:
#     :return:
#     """
#     resol, origin = affines.to_matvec(imageobj.get_affine())
#     resol = np.diag(resol).copy()
#     origin = origin
#     imageobj._dataobj = np.swapaxes(imageobj._dataobj, axis1, axis2)
#     resol[axis1], resol[axis2] = resol[axis2], resol[axis1]
#     origin[axis1], origin[axis2] = origin[axis2], origin[axis1]
#     affine = affines.from_matvec(np.diag(resol), origin)
#     reset_orient(imageobj, affine)
#
#
# def down_reslice(imageobj, ac_slice, ac_loc, slice_thickness, total_slice, axis=2):
#     """ Reslicing
#
#     :param imageobj:
#     :param ac_slice:
#     :param ac_loc:
#     :param slice_thickness:
#     :param total_slice:
#     :param axis:
#     :return:
#     """
#     data = np.asarray(imageobj.dataobj)
#     resol, origin = affines.to_matvec(imageobj.affine)
#     resol = np.diag(resol).copy()
#     scale = float(slice_thickness) / resol[axis]
#     resol[axis] = slice_thickness
#     idx = []
#     for i in range(ac_loc):
#         idx.append(ac_slice - int((ac_loc - i) * scale))
#     for i in range(total_slice - ac_loc):
#         idx.append(ac_slice + int(i * scale))
#     imageobj._dataobj = data[:, :, idx]
#     affine, origin = affines.to_matvec(imageobj.affine[:, :])
#     affine = np.array(np.diag(affine))
#     affine[axis] = slice_thickness
#     affine_mat = affines.from_matvec(np.diag(affine), origin)
#     imageobj._affine = affine_mat
#     imageobj.set_qform(affine_mat)
#     imageobj.set_sform(affine_mat)
#     imageobj.header['sform_code'] = 0
#     imageobj.header['qform_code'] = 1
#
#
# def crop(imageobj, **kwargs):
#     """ Crop
#
#     :param imageobj:
#     :param kwargs:
#     :return:
#     """
#     x = None
#     y = None
#     z = None
#     t = None
#     for arg in kwargs.keys():
#         if arg == 'x':
#             x = kwargs[arg]
#         if arg == 'y':
#             y = kwargs[arg]
#         if arg == 'z':
#             z = kwargs[arg]
#         if arg == 't':
#             t = kwargs[arg]
#         else:
#             pass
#     if x:
#         if (type(x) != list) and (len(x) != 2):
#             raise TypeError
#     else:
#         x = [None, None]
#     if y:
#         if (type(y) != list) and (len(y) != 2):
#             raise TypeError
#     else:
#         y = [None, None]
#     if z:
#         if (type(z) != list) and (len(z) != 2):
#             raise TypeError
#     else:
#         z = [None, None]
#     if t:
#         if (type(t) != list) and (len(t) != 2):
#             raise TypeError
#     else:
#         t = [None, None]
#     if len(imageobj.shape) == 3:
#         imageobj._dataobj = imageobj._dataobj[x[0]:x[1], y[0]:y[1], z[0]:z[1]]
#     if len(imageobj.shape) == 4:
#         imageobj._dataobj = imageobj._dataobj[x[0]:x[1], y[0]:y[1], z[0]:z[1], t[0]:t[1]]
#
#
# def set_center(imageobj, corr):
#     """ Applying center corrdinate to the object
#     """
#     resol, origin = affines.to_matvec(imageobj.affine[:, :])
#     affine = affines.from_matvec(resol, corr)
#     reset_orient(imageobj, affine)