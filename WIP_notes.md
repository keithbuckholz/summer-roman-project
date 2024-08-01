# WIP Issues

1) Factor of 2 issue; matching scale/count rate 
2) Wavelength-depedent PSF 

0) Producing direct image? (Minor capability for testing; we don't want to scale this)

# Going forward plans

1) [ ] Track down factor of 2 error.

2) [-] Check brightest and faintest stars to correct star radius function.

3) [-] Check scale of extracted spectra.

4) [p] Apodize wavelength cuts to roll on/off when attempting wavelength-dependent PSF.

5) [x] Where does Grizli get total flux from? Direct Image? Provided Spectrum? Try doubling direct image values and comparing grism sim scale. Does it change? Do it again with provided spectrum.

# Resolutions

5) Built single_object_playground. Grizli seems to get total flux from spectrum. Disperses total flux according to direct image.

# Progress

1) Seg map in integrated sim did not include padding. Added padding, factor of 2 is reduced some. 87 max vs 117 max.

2) Switched to PSF-based seg map. Switched back to uniform circle of radius 40.

3) See single_pix.ipynb. Extracted spectrum from a single pixel object matches expectation (almost perfectly). Expectation is define: (spectrum_template * sensitivity_curve) -> summed in ~10 angstrom bins; binned array contains flux expectations.

4) Apodizing makes a big difference. The window needs to be refined. A principled approach would probably be faster than trial-and-error.

# Quick Notes Space