# WIP Issues

1) Factor of 2 issue; matching scale/count rate 
2) Wavelength-depedent PSF 
3) 
0) Producing direct image? (Minor capability for testing; we don't want to scale this)

# Going forward plans

1) Check medians and maxes to compare scale.
2) Check brightest and faintest stars to correct star radius function.
3) Check scale of extracted spectra.
4) Apodize wavelength cuts to roll on/off when attempting wavelength-dependent PSF.
5) [x] Where does Grizli get total flux from? Direct Image? Provided Spectrum? Try doubling direct image values and comparing grism sim scale. Does it change? Do it again with provided spectrum.

# Resolution/Progress

4) Apodizing makes a big difference. The window needs to be refined. A principled approach would probably be faster than trial-and-error.
5) Built single_object_playground. Grizli seems to get total flux from spectrum. Disperses total flux according to direct image.

# Quick Notes Space