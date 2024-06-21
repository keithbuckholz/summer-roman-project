# Grizli Notes

## Preparing a fits file

Grizli expects a few things in the header that may not be there or accurate: \
INSTRUME \
FILTER \
CONFFILE \
EFFEXPTM

I've written a simply script (fix_fits.py) that will put intrument, filter, and config file location in the header as: \
INSTRUME = "ROMAN" \
FILTER = "det1" \
CONFFILE = "/Users/keith/astr/research_astr/FOV0/Roman.det1.07242020.conf" \
Command-Line Input: `python fix_fits.py original_filename fixed_filename`

I've also written a simple rotation script since Roman disperses in y and aXeSim disperses in x: \
Command-Line Input: `python rotate.py original_filename image_extension(optional) new_filename k_number_of_rotations`

## Config File

IPAC has a great aXe config file, but grizli doesn't know where to find it by defaut. The config filepath can be included in the header data and grizli can sort it out from there. Details on how to do this are above.

## Two methods: Basic-sim, Full-sim

I've got two notebooks that differ by one line:
```
roman_sim.photutils_detection(detect_thresh=2, grow_seg=0, gauss_fwhm=2., verbose=True, save_detection=True, use_seg=True)
```
They return very similar results. The tables comtain the same number of objects and the images are very similar.
This line takes ~7 seconds per run and doesn't seem to make a meaningful difference.

I attempted running basic-sim, but providing no segmentation map. That produces an image with significant noise and background. It winds up a bit closer to the original slitless image Wang et al produced. Similar backgrounds, and slightly better alignment between dispersions.

## WIP Issues

### Inconsistencies between Wang et al and Grizli image
##### Problem
The baseline and grizli model images are misaligned. Additionally, there is generally a fairly large difference between the Wang et al image and the Grizli image. They do not cancel out very well when subtracted from one another.

##### Working Solution
Misalginment and doubling effect seem to be because we rotated our images opposite directions (Wang et al went counterslockwise; I went clockwise). Rotating the opposite direction minimizes misalignment and doubling. Unclear on the causes of the other differences.

### Generalized solution to max dy and cutout problem.
##### Problem
The grizli cutout sizes are determined by the object size. The Roman grism has a larger dy than many default cutout sizes have room for. At current, this can be overcome by setting `compute_size=False, size=76` in the `compute_full_model()` function call. Note that size changed from 75 to 76 when I started rotating counterclockwise before modelling. This change from 75 to 76 and the fact that other detectors use other config files points to a need to generalize the size calculation. That is, when modeling, the max dy for the chip should be computed once, then the size should be set large enough for that max dy for all dispersions on that chip. Increased cutout size means increased compute times, so a blanket excessive size for all chips should not be used instead.

##### Working Solution
First, the global extrema can be found. Then, if the extrema is not within the bound, Langrange multipliers should be applied to determine the local extrema.

## Retired Issues

### Objects y_flt<10 are not found in seg image - pad
##### Solution
The problem explanation was pretty far off. The issue of objects too close to the edge not being found is resolved by padding. pad=100 is sufficient for detector 1. When I used photutils_detections, I was setting that pad; so, no error was occured. The default pad [64, 256] is not sufficient in the x-direction; thus an error occured with objects on the edge.

##### Problem
When the size is set sufficiently large, anything within 10 pix of the y-axis cannot be found in the segmentation image. This issue only occurs when a segmentation image is produced and provided. If photutils_detection is used instead, no error is thrown becuase those objects are never identified to begin with.

### self.idx[] IndexError - cutout size
##### Solution
Issue was due to insufficent size cutout. Provide the compute_full_model function call with the arguments compute_size=False and size=75 was sufficient to correct for this issue. ts- notebooks deleted; directory cleaned and pruned for other excess files

##### Problem: 

In troubleshooting this issue, I've created some notebooks with names beggining with ts-.... These notebooks compare differents ways to produce/demonstrate this issue. i.e. rotating the image causes this issue for different galaxies, cropping the image before modelling causes the issue.

ts-full-sim_crop.ipynb - If the image is cropped before calculation, objects cannot be dispersed.
ts-full-sim_rotated.ipynb - If image is rotated, different objects are dispsered. Far from origin (top-right), is dispered more successfully.
ts-cutout-sim_mask-by-origin - If your cutout is by origin instead of away from it, your cutout cannot be dispersed.

Working theories:
Low indicies cause an issue
Too many objects # Unlikely
dyc definition flaw

After some number of dispersions, it begins to log this error. It continues calculating, but it seems to stop being successful. Generally, the top-right of the image disperses successfully; This it with exception, particularly bright objects will disperse regardless of # location.

Printing upon both success and failure reveals intermittent failure from the start, not full failure after some threshold.

```
########################################## 
# ! Exception (2024-06-14 20:53:42.586)
#
# !Traceback (most recent call last):
# !  File "/Users/keith/miniconda3/envs/phot-griz/lib/python3.12/site-packages/grizli/model.py", line 419, in process_config
# !    self.flat_index = self.idx[dyc + self.x0[0], self.dxpix]
# !                      ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# !IndexError: index 99 is out of bounds for axis 0 with size 52
# !
# !During handling of the above exception, another exception occurred:
# !
# !Traceback (most recent call last):
# !  File "/Users/keith/miniconda3/envs/phot-griz/lib/python3.12/site-packages/grizli/model.py", line 3176, in compute_model_orders
# !    beam = GrismDisperser(id=id,
# !           ^^^^^^^^^^^^^^^^^^^^^
# !  File "/Users/keith/miniconda3/envs/phot-griz/lib/python3.12/site-packages/grizli/model.py", line 289, in __init__
# !    self.process_config()
# !IndexError
# !
######################################### 
```

These are the relevant variables that are leading up to the error in question. self.dxpix and self.x0[0] seem to be constant for failed values. Presusmably it's an issue with dyc or idx then.

```
dyc: [70 70 70 ... 48 48 48] 
self.x0[0]: 25 
self.dxpix: [  25   26   27 ... 1622 1623 1624]
```

dyc is set by these lines:
 
 ```
 dyc = np.cast[int](self.ytrace_beam+20)-20+1

self.ytrace_beam, self.lam_beam = self.conf.get_beam_trace(
                            x=(self.xc+self.xcenter-self.pad[1])/self.grow,
                            y=(self.yc+self.ycenter-self.pad[0])/self.grow,
                        dx=(self.dx+self.xcenter*0+self.xoffset)/self.grow,
                            beam=self.beam, fwcpos=self.fwcpos)
self.ytrace_beam *= self.grow <--- Grow does not appear in the header and is set to 1 by another method
```