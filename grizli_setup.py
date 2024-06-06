import sys
import grizli.utils

# Download appropriate calibration and config files
grizli.utils.fetch_default_calibs(get_acs=True)

if sys.argv[1] == "jwst":
    jbool = True
else:
    jbool = False
grizli.utils.fetch_config_files(get_acs=True, get_jwst=jbool)

# symlink SED redshift templates
grizli.utils.symlink_templates(force=True)