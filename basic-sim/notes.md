#### Basic-Sim.ipynb notes

git clone https://github.com/astropy/photutils.git
git checkout 9a1c1e9 <- checkout final 1.3 commit: https://github.com/astropy/photutils/commits/1.3.0/
pip install . <- install photutils=1.3 to use deprecated source_properties in Grizli (deleted on next commit)

use .value to keep the astropy.quantity object dimensionless

`sim_g102.object_dispersers[id]['A'] ---> list has a dictionary in the [2] index: sim_g102.object_dispersers[id][2]['A']`

grizli/grizli/data/template/erb2010.dat ---> commit id 8428343

find ~ -type f -name wfc3_ir_secondary_001_syn.fits

cell failed to find file wfc3...File deep in GRIZLI. Created symlink to wfc3_ir_secondary_001_syn.fits at ~/GRIZLI/comp/wfc3/wf3c...

Not critical, but I also symlinked a directory with extinction files. This resolved a non-fatal warning.