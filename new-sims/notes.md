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