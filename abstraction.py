import os
import numpy as np
import scipy
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams["figure.figsize"] = (16,7)
mpl.rcParams["image.origin"] = "lower"
mpl.rcParams["image.interpolation"] = "nearest"

import pysynphot as S
import webbpsf
from grizli.model import GrismFLT
from astropy.io import fits
from astropy.table import Table
from tqdm import tqdm

class grism_sim(GrismFLT):
    """
    This Class inherits from grizli.model.GrismFLT. It's useful for implementing the Roman Grism Simulation Process.
    (I'm implementing it becuase I'm tired of correcting minor issues in 10 different notebooks). It is a Work-In-Progess.

    Parameters:
    ----------
    SED_dir: str
        Local real path to directory containing all relevant SEDs, and bandpass fits.
    fits_dir: str
        Local real path to directory containing direct image and segmentation map files.
    cat_dir: str
        Local real path to directory containing Catalog file.
    bandpass_file: str
        Bandpass filename. Spectra will be renormalized using catalog magnitudes and this bandpass file.
        default: wfirst_wfi_f158_001_syn.fits
    star_spec_file: str
        Star SED filename. All stars assumed to use same SED.
        default: ukg0v.dat
    direct_file: str
        Direct image filename. This direct image is passed into grizli to determine an objects flux distribution on the detector.
        default: ready_direct_GRS_FOV0_roll0_dx0_dy0_SCA1_direct_final.fits
    seg_file: str
        Segmentaion map filename. Segmentation map indicates object locations on detector. Can be an empty map, and produced with
        put_on_seg_map method.
        default: empty_seg.fits
    cat: str
        Catalog filename. Catalog contains object characteristics used for dispersion. Required characteristics/column names:
        NUMBER, X_IMAGE, Y_IMAGE, A_IMAGE, B_IMAGE, THETA_IMAGE, MAG_F1500W, MODIMAGE
    pad: int
        Padding added around model. Allows objects near the edge of the detector to disperse properly. If padding is too small, 
        object traces may begin off the image array causing a failure to disperse.

    Methods:
    ----------
    show_current_model:
        Turns model upright and trims padding. Calls plt.imshow, and passes in kwargs.

    put_on_seg_map:
        Calculate objects location on detector.

        Parameters:
        ----------
        object: astropy.table.row.Row, or other object with similar indexing
            Astropy table Row object containing sinlge object's characteristics. May be a different object (e.g. dictionary)
            using similar indexing methods (i.e. object["NUMBER"]). Minimum required characteristics: NUMBER, MAG_F1500W, 
            X_IMAGE, Y_IMAGE, A_IMAGE, B_IMAGE, THETA_IMAGE, MODIMAGE.
        
        in_place: bool
            Add to segmentation map. If True, single object segmentation is added to the existing segmentation map.
            default: False

        return_seg: bool
            Return single object segmentation map. If False, method returns self.
            default: True
        
    disperse_object:
        Disperses and object. Reads in, and corrects the appropriate SED. Calls GrismFLT.compute_model_orders().
        Returns result.

        Parameters:
        ----------
        object: astropy.table.row.Row, or other object with similar indexing
            Astropy table Row object containing sinlge object's characteristics. May be a different object (e.g. dictionary)
            using similar indexing methods (i.e. object["NUMBER"]). Minimum required characteristics: NUMBER, MAG_F1500W, 
            MODIMAGE, SPECTEMP.
                
        in_place: bool
            Passed directly into GrismFLT.compute_model_orders(). If True, returns boolean indicating success. If False, 
            returns tuple containing OrderedDict (of beams and their Dispersers), and model array.

    """

    def __init__(self, SED_dir, fits_dir, cat_dir, 
                bandpass_file="wfirst_wfi_f158_001_syn.fits", 
                star_spec_file="ukg0v.dat",
                direct_file="ready_direct_GRS_FOV0_roll0_dx0_dy0_SCA1_direct_final.fits", 
                seg_file="empty_seg.fits", 
                cat="MOT_SCA1_roll_0_dither_0x_0y_cut_zcut.txt", 
                pad=100):

        # Save Directories
        self.SED_dir = SED_dir
        self.fits_dir = fits_dir
        self.cat_dir = cat_dir

        # Save filepaths
        self.direct_file = os.path.join(fits_dir, direct_file)
        self.seg_file = os.path.join(fits_dir, seg_file)
        self.cat = os.path.join(cat_dir, cat)

        # Check if direct image was pre-prepared, 
        _DIRECT_OPEN = True
        open_direct = fits.open(self.direct_file)
        if "INSTRUME" in open_direct[0].header.keys():
            _READY_DIRECT =True
        
        if not _READY_DIRECT:
            open_direct = prepare_direct_fits(open_direct)
            open_direct.write_to("/tmp/prepared_{0}".format(direct_file))
            return "FAIL"


        # run Grizli.model.GrismFLT init function
        GrismFLT.__init__(self, direct_file=self.direct_file, seg_file=self.seg_file, pad=pad)

        # Load and sort catalog
        tbl = Table.read(os.path.join(cat_dir, cat), format="ascii")
        self.cat = tbl.group_by("MODIMAGE")
        self.cat.groups[0].sort("MAG_F1500W", reverse=True)
        self.cat.groups[1].sort("MAG_F1500W", reverse=True)
        del tbl

        # Load Bandpass
        df = Table.read(os.path.join(SED_dir, bandpass_file), format="fits")
        self.bp = S.ArrayBandpass(wave=df["WAVELENGTH"], throughput=df["THROUGHPUT"])
        # df not deleted; reused and deleted later

        # Load Star_spec
        df = Table.read(os.path.join(SED_dir, star_spec_file), format="ascii")
        self.star_spec = S.ArraySpectrum(wave=df["col1"], flux=df["col2"], waveunits="angstroms", fluxunits="flam")

        # STAR shape functions
        self.star_radius = lambda mag: max(8, min(4663 * 10**(-0.1587 * mag) + 1.596, 40))
        self.star_circle = lambda x,y,x_0,y_0: (x - x_0) ** 2 + (y - y_0) ** 2

        # GALAXY shape functions
        A = lambda theta, a, b: ((np.sin(theta)**2)/(a**2)) + ((np.cos(theta)**2)/(b**2))
        B = lambda theta, a, b: 2 * np.sin(theta) * np.cos(theta) * ((1/b**2) - (1/a**2))
        C = lambda theta, a, b: ((np.sin(theta)**2)/(b**2)) + ((np.cos(theta)**2)/(a**2))

        self.galaxy_ellipse = lambda x, y, x_0, y_0, ell: ((A(*ell) * (x - x_0)**2) + 
                                                           (B(*ell) * (x - x_0) * (y - y_0)) + 
                                                           (C(*ell) * (y - y_0)**2))

        self.not_on_seg_map = []

        if _DIRECT_OPEN:
            open_direct.close()

    def prepare_direct_fits(self, open_fits, hdr_injection):
        
        for key in hdr_injection.keys():
            try:
                ext, value = hdr_injection[key].split(";") # split "ext;value" into seperate variables
                ext = int(ext)
            except ValueError as err:
                msg = 'Dictionary values must have format "ext;hdr_value"'
                raise err(msg)
            
            open_fits[ext].header[key] = value

        open_fits[1].data = np.rot90(open_fits[1].data, k=3)

        return open_fits

    def show_current_model(self, **kwargs):
        """
        Turns model upright and trims padding. Calls plt.imshow, and passes in kwargs.
        """
        true_model = np.rot90(self.model[self.pad[1]:-self.pad[1], self.pad[0]:-self.pad[0]])
        plt.imshow(true_model, **kwargs)

        return self

    def put_on_seg_map(self, object, in_place=False,  return_seg=True):
        """
        Calculate objects location on detector.

        Parameters:
        ----------
        object: astropy.table.row.Row, or other object with similar indexing
            Astropy table Row object containing sinlge object's characteristics. May be a different object (e.g. dictionary)
            using similar indexing methods (i.e. object["NUMBER"]). Minimum required characteristics: NUMBER, MAG_F1500W, 
            X_IMAGE, Y_IMAGE, A_IMAGE, B_IMAGE, THETA_IMAGE, MODIMAGE.
        
        in_place: bool
            Add to segmentation map. If True, single object segmentation is added to the existing segmentation map.
            default: False

        return_seg: bool
            Return single object segmentation map. If False, method returns self.
            default: True

        """

        # Pull info from object
        id = object["NUMBER"]
        mag = object["MAG_F1500W"]
        x_0 = object["X_IMAGE"] + 100       # +100 accounts for padding
        y_0 = object["Y_IMAGE"] + 100       # +100 accounts for padding
        _is_star = object["MODIMAGE"]

        # Put this item on the seg_map 
        # STAR
        if _is_star:

            radius = self.star_radius(mag) ** 2
            circle = lambda x, y: self.star_circle(x, y, x_0, y_0) <= radius

            x_min = max(0,      int(x_0 - radius - 1))          # int without +1 is floor
            x_max = min(4288,   int(x_0 + radius + 1) + 1)      # +1 of int is ceil
            y_min = max(0,      int(y_0 - radius - 1))
            y_max = min(4288,   int(y_0 + radius + 1) + 1)

            x = np.arange(x_min, x_max)
            y = np.arange(y_min, y_max)
            x_grid, y_grid = np.meshgrid(x, y)

            condition = circle(x_grid, y_grid)

        else:

            theta = object["THETA_IMAGE"]
            a = object["A_IMAGE"]
            b = object["B_IMAGE"]
            ell = (theta, a, b)

            bounds_scalar = 4 ** 2 # semimajor_axis_stddev * bounds_scalar = psuedo_radius

            x_min = max(0,      int(x_0 - (bounds_scalar * a)))
            x_max = min(4288,   int(x_0 + (bounds_scalar * a) + 1))
            y_min = max(0,      int(y_0 - (bounds_scalar * a)))
            y_max = min(4288,   int(y_0 + (bounds_scalar * a) + 1))

            x = np.arange(x_min, x_max)
            y = np.arange(y_min, y_max)
            x_grid, y_grid = np.meshgrid(x, y)

            ellipse = lambda x, y: self.galaxy_ellipse(x, y, x_0, y_0, ell) <= bounds_scalar

            condition = ellipse(x_grid, y_grid)
        
        temp_seg = np.zeros((4288, 4288), dtype="float32")
        temp_seg[y_min:y_max, x_min:x_max] =  np.where(condition, id, 0)
        temp_seg = np.rot90(temp_seg, k=3)

        if not np.any(temp_seg):
            self.not_on_seg_map.append(id)

        if in_place:
            self.seg += temp_seg

        if return_seg:
            return temp_seg

        return self

    def disperse_object(self, object, in_place=True):
        """
        Disperses and object. Reads in, and corrects the appropriate SED. Calls GrismFLT.compute_model_orders().
        Returns result.

        Parameters:
        ----------
        object: astropy.table.row.Row, or other object with similar indexing
            Astropy table Row object containing sinlge object's characteristics. May be a different object (e.g. dictionary)
            using similar indexing methods (i.e. object["NUMBER"]). Minimum required characteristics: NUMBER, MAG_F1500W, 
            MODIMAGE, SPECTEMP.
                
        in_place: bool
            Passed directly into GrismFLT.compute_model_orders(). If True, returns boolean indicating success. If False, 
            returns tuple containing OrderedDict (of beams and their Dispersers), and model array.
        """

        id = object["NUMBER"]
        mag = object["MAG_F1500W"]
        _is_star = object["MODIMAGE"]

        if _is_star:
            spec = self.star_spec.renorm(mag, "abmag", self.bp)

        else:
            sed = "SED:rest:gal.{0}.fits".format(object["SPECTEMP"])
            sed_path = os.path.join(self.SED_dir, sed)
            gal_spec = Table.read(sed_path, format="fits")
            z = object["Z"]

            spec = S.ArraySpectrum(wave=gal_spec["wavelength"], flux=gal_spec["flux"],
                                   waveunits="angstroms", fluxunits="flam").redshift(z)

            spec = spec.renorm(mag, "abmag", self.bp)

        spec.convert("flam")

        return self.compute_model_orders(id, mag=mag, compute_size=False, size=77, in_place=in_place, 
                                         store=False, is_cgs=True, spectrum_1d=[spec.wave, spec.flux])
                                        
    def simple_extract(self):
        print("TODO")
        return 1