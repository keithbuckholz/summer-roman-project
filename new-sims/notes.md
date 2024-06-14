# Grizli Notes

## Preparing a fits file

Grizli expects a few things in the header that may not be there or accurate:
INSTRUME
FILTER
EFFEXPTM

I've written a simply script that will put intrument and filter in the header as:
INSTRUME = ROMAN
FILTER = det1

## Config File

IPAC had a great aXe config file, but grizli doesn't know where to find it (or even that it should look, it just throw an error).
I added this couple of lines:
if instrume == 'ROMAN':
        conf_file = "/Users/keith/astr/research_astr/FOV0/Roman.det1.07242020.conf"

at this location:
/Users/keith/miniconda3/envs/stenv/lib/python3.12/site-packages/grizli/grismconf.py: 770


## WIP Issues

# After some number of dispersions, it begins to log this error. It continues calculating, but it seems to stop being successful. Generally, the top-right of the image disperses successfully; This it with exception, particularly bright objects will disperse regardless of # location.

# Printing upon both success and failure reveals intermittent failure from the start, not full failure after some threshold.

\########################################## 
\# ! Exception (2024-06-14 20:53:42.586)
\#
\# !Traceback (most recent call last):
\# !  File "/Users/keith/miniconda3/envs/phot-griz/lib/python3.12/site-packages/grizli/model.py", line 419, in process_config
\# !    self.flat_index = self.idx[dyc + self.x0[0], self.dxpix]
\# !                      ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
\# !IndexError: index 99 is out of bounds for axis 0 with size 52
\# !
\# !During handling of the above exception, another exception occurred:
\# !
\# !Traceback (most recent call last):
\# !  File "/Users/keith/miniconda3/envs/phot-griz/lib/python3.12/site-packages/grizli/model.py", line 3176, in compute_model_orders
\# !    beam = GrismDisperser(id=id,
\# !           ^^^^^^^^^^^^^^^^^^^^^
\# !  File "/Users/keith/miniconda3/envs/phot-griz/lib/python3.12/site-packages/grizli/model.py", line 289, in __init__
\# !    self.process_config()
\# !IndexError
\# !
\######################################### 

# These are some failed values for the variables. self.dxpix and self.x0[0] seem to be constant. Presusmably it's an issue with dyc or idx then.

dyc: [70 70 70 ... 48 48 48] 
self.x0[0]: 25 
self.dxpix: [  25   26   27 ... 1622 1623 1624]

# dyc is set by these lines:
 
 dyc = np.cast[int](self.ytrace_beam+20)-20+1

self.ytrace_beam, self.lam_beam = self.conf.get_beam_trace(
                            x=(self.xc+self.xcenter-self.pad[1])/self.grow,
                            y=(self.yc+self.ycenter-self.pad[0])/self.grow,
                        dx=(self.dx+self.xcenter*0+self.xoffset)/self.grow,
                            beam=self.beam, fwcpos=self.fwcpos)
self.ytrace_beam *= self.grow <--- Grow does not appear in the header and is set to 1 elsewhere
