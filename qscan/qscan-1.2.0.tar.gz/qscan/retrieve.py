from .settings import *

def readspec(spectrum):
 
    filename = spectrum.split('/')[-1]
    datatype = filename.split('.')[-1]
    z = co = sky = None
    if datatype=='fits':
        hdu = fits.open(spectrum)
        specformat = 'nothing'
        for i in range (len(hdu[0].header)):
            if ('UVES' in str(hdu[0].header[i])) or ('POPLER' in str(hdu[0].header[i])):
                specformat = 'UVES'
                break
            elif ('Keck' in str(hdu[0].header[i])) or ('HIRES' in str(hdu[0].header[i])):
                specformat = 'HIRES'
                break
            elif 'SDSS' in str(hdu[0].header[i]):
                specformat = 'SDSS'
                break
        if specformat=='HIRES':
            hd = hdu[0].header
            wa = hd['CRVAL1'] + hd['CDELT1'] * ((hd['CRPIX1']-1)+numpy.arange(hd['NAXIS1']))
            wa = 10**wa if 'DC-FLAG' in hd and float(hd['DC-FLAG'])==1 else wa
            if '_f.fits' in spectrum:
                fl  = hdu[0].data
                hdu = fits.open(spectrum.replace('_f.fits','_e.fits'))
                er  = hdu[0].data                
            elif os.path.exists(spectrum.replace('fits','sig.fits'))==True:
                fl  = hdu[0].data
                hdu = fits.open(spectrum.replace('fits','sig.fits'))
                er  = hdu[0].data
            else:
                fl  = d[0,:]
                er  = d[1,:]
        elif specformat=='UVES':
            hd = hdu[0].header
            wa = hd['CRVAL1'] + hd['CDELT1'] * ((hd['CRPIX1']-1)+numpy.arange(hd['NAXIS1']))
            wa = 10**wa if 'DC-FLAG' in hd and float(hd['DC-FLAG'])==1 else wa
            if os.path.exists(spectrum.replace(filename,'err_'+filename)):
                fl = hdu[0].data
                hdu = fits.open(spectrum.replace(filename,'err_'+filename))
                er  = hdu[0].data
            else:
                fl = hdu[0].data[0,:]
                er = hdu[0].data[1,:]
        elif specformat=='SDSS':
            hdu0 = hdu[0].header
            hdu1 = hdu[1].header
            z    = float(hdu[2].data['Z'])
            wa   = 10.**(hdu0['coeff0'] + hdu0['coeff1'] * numpy.arange(hdu1['naxis2']))
            fl   = hdu[1].data['flux']
            er   = [1/numpy.sqrt(hdu[1].data['ivar'][i]) if hdu[1].data['ivar'][i]!=0 else 10**32 for i in range (len(fl))]
            co   = hdu[1].data['model']
            sky  = hdu[1].data['sky']
        else:
            print 'Spectrum format not recognized...'
            quit()
    else:
        d  = numpy.loadtxt(spectrum,dtype='float')
        wa = d[:,0]
        fl = d[:,1]
        er = d[:,2]

    setup.wa  = wa
    setup.fl  = fl
    setup.er  = er
    
