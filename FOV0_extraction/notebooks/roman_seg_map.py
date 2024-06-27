# Segmentation
from astropy.io import fits
from photutils.segmentation import SourceFinder, make_2dgaussian_kernel
from photutils.background import Background2D, MedianBackground
from astropy.convolution import convolve

def produce_seg_map(direct_file, seg_file, ext=1, **kwargs):
    """
    Function that produces and returns a segmentation map of a provided fits.

    Parameters
        ----------
        direct_file: str
            filepath to fits file containing direct image you need a segmentation map for
        ext: int, optional
            extenension of the fits file you would like to access. Default: 1
        
        Returns
        -------
        seg_map: np.array
            Segmentation map of objects in supplied direct image.

    """

    # Parse kwargs
    kwarg_keys = kwargs.keys()

    # Default args for Background2D() and SourceFinder()
    default_bkg_args = {"box_size":    (511, 511),
                        "filter_size": (3, 3)}

    default_finder_args = {"npixels":  7, 
                           "nlevels":  32, 
                           "contrast": 0.001}

    # Background_args
    bwargs = {}
    for arg in default_bkg_args.keys():
        # if argument in kwargs: use kwargs value
        # else: use default values
        if arg in kwarg_keys:
            bwargs[arg] = kwargs[arg]
        else:
            bwargs[arg] = default_bkg_args[arg]

    # Background_args
    sfwargs = {}
    for arg in default_finder_args.keys():
        # if argument in kwargs: use kwargs value
        # else: use default values
        if arg in kwarg_keys:
            sfwargs[arg] = kwargs[arg]
        else:
            sfwargs[arg] = default_finder_args[arg]
    
    # Open image
    direct_fits = fits.open(direct_file)
    data, header = (direct_fits[ext].data, direct_fits[ext].header)

    # Subtract background
    bkg_estimator = MedianBackground()
    bkg = Background2D(data, **bwargs)
    data -= bkg.background

    # Convolve image
    kernel = make_2dgaussian_kernel(3.0, 5)
    convolved_data = convolve(data, kernel)

    # Instantiate the SourceFinder and set threshold
    finder = SourceFinder(**sfwargs)
    threshold = 2 * bkg.background_rms

    seg_map = finder(convolved_data, threshold)

    # Save seg_map as fits
    fits.writeto(seg_file, seg_map, header=header,overwrite=True)
    return seg_map

