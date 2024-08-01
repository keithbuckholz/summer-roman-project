I think the most useful/interesting files for getting up to speed from the very beginning are: \
0) tutorial/0_wget_files.ipynb                  \
0) tutorial/1_Install_Grizli.ipynb              \
0) tutorial/3_fits_files.ipynb                  \
3) light_scripts/fits_prep                      \
either:                                         \
    integrated_sim/cutout_sim.ipynb             \
or                                              \
    integrated_sum/integrated_process.ipynb     \



Table of contents:

tutorial
    : Contains notebooks walking through the entire process, with details about how/why some things are done. These notebooks are old and reflect an older process.

grizli-install
    : Installing grizli for the first time takes a few steps. I tried to put all of that into a script for easier installation.

segmentation-practice
    : This is completely Depricated, and should probably be deleted. We were using Photutils to produce a segmentation map. A couple notebooks exploring how to do this are contiained here.

light_scripts
    : A number of short notebooks and misc files are contained here. fits_prep and the associated python script are useful for preparing fits files for grizli. object_finder finds an object in the catalog using its coordinates. region_file_builder builds a DS9 region file; useful for overlaying our seg map onto the direct image in DS9.

FOV0_sims
    : This contains our first attempts at replicating the HLSS Grism Simulation. The only notebook still used is comparisons.ipynb.

all_chips
    : I attempted to use multiprocessing to simulate all FOVs using flat spectra. It crashed my computer.

direct_fits_exploration
    : Could probably be deleted. zero_fits_data is useful for building and saving a completely zero'd fits file (empty_direct.fits).

integrated_sim
    : Rather than building a segmentation map, then dispersing. We are now building a segmentation map for one object, dispersing that one object, then repeating with the next object until done. A few notebooks here explore building a direct image and using that instead of the HLSS Grism Sim direct image, but we have elected not to continue trying to reproduce the direct image. 

predicateble_extract
    : I modified the config file to make dispersions vertical lines with each pixel containing a uniform ~10 angstroms (10000 angstroms divided across 1001 pixels). Notebooks here use that config file. Makes extracting a spectrum very easy. At time of writing, we're using this to check that our dispersions are what we expect them to be.

psf
    : Explores using WebbPSF to build a PSF. Some build a seg_map using PSF, others explore wavelength dependence.

toy_configs
    : Currently holds the config file for predictable_extract. show_trace.ipynb reads in a config file and shows what that dispersion would look like relative to a reference pixel.