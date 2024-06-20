# Grizli Notes

## Preparing a fits file

Grizli expects a few things in the header that may not be there or accurate: \
INSTRUME \
FILTER \
EFFEXPTM

I've written a simply script (fix_fits.py) that will put intrument and filter in the header as: \
INSTRUME = ROMAN \
FILTER = det1 \
call: `python fix_fits.py original_filename fixed_filename`

I've also written a simple rotation script: \
call: `python rotate.py original_filename image_extension(optional) new_filename k_number_of_rotations`

## Config File

IPAC has a great aXe config file, but grizli doesn't know where to find it (or even that it should look, it just throws an error).
I added this couple of lines:
```
if instrume == 'ROMAN':
        conf_file = "/Users/keith/astr/research_astr/FOV0/Roman.det1.07242020.conf"
```

at this location in the Grizli code: \
`/Users/keith/miniconda3/envs/stenv/lib/python3.12/site-packages/grizli/grismconf.py: 770`

## Basic sim

Running Basic-sim.ipynb, the built-in photutils_detection method does a decent job. Doing things this way does not encounter the issue with failure to disperse. The is a fair difference between the Grizli sim and the Wang et al sim, but as of now, it's better than creating a seperate segmentation map.

## WIP Issue

When the size is set sufficiently large, anything within 10 pix of the y-axis cannot be found in the segmentation image. This issue only occurs when a segmentation image is produced and provided. If photutils_detection is used instead, no error is thrown becuase those objects are never identified to begin with.

## Retired Issues

Issue was due to insufficent size cutout. Provide the compute_full_model function call with the arguments compute_size=False and size=75 was sufficient to correct for this issue. ts- notebooks deleted; directory cleaned and pruned for other excess files

-----------------------------------

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