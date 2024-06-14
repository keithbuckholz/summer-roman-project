#!/bin/bash

# Arguments: environment name, stenv yaml file, hst or jwst
# sh grizli-install.sh testenv ../stenv-macOS-ARM64-py3.12-2024.04.29.yaml jwst 

### Make conda activate as it would in an interactive terminal; specific to me, not generalized
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('/Users/keith/miniconda3/bin/conda' 'shell.zsh' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "/Users/keith/miniconda3/etc/profile.d/conda.sh" ]; then
      . "/Users/keith/miniconda3/etc/profile.d/conda.sh"
    else
      export PATH="/Users/keith/miniconda3/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<

# Create environment with user provided name and .yaml file
conda env create -n $1 --file $2

# DOES NOT ACTIVATE ENVIRONMENT PROPERLY
# Activate environment and install grizli
conda activate $1
pip install grizli

if [[ $3 == "JWST" ]]; then
  pip install "grizli[jwst]"
elif [[ $3 == "HST" ]]; then
  pip install "grizli[HST]"
  conda install hstcal
fi

# Check first-time setup; export zshrc/bashrc lines
lines=( 'export GRIZLI="${HOME}/grizli"' 'export iref="${GRIZLI}/iref/"' 'export jref="${GRIZLI}/jref/"' )

if [[ $SHELL == "/bin/zsh" ]]; then
  for ii in "${lines[@]}"; do
    if ! grep -qi "$ii" "$ZDOTDIR/.zshrc" && ! grep -qi "$ii" "$ZDOTDIR/.zprofile"; then
      if [[ ii == "${lines[1]}" ]]; then
        echo "\n${ii}" >> $ZDOTDIR/.zshrc
      else
        echo $ii >> $ZDOTDIR/.zshrc
      fi
    fi
  done
elif [[ $SHELL == "/bin/bash" ]]; then
  echo "Put these lines in your .bashrc if they're not there already:"
  for ii in "${lines[@]}"; do
    echo "${ii}"
  done
fi

# Check first-time setup; directories grizli needs
directories=( "GRIZLI" "iref" "jref" )
grizli_directories=( "CONF" "templates")

for ii in "${directories[@]}"; do
  if ! find ~ -maxdepth 1 -type d -name $ii 2>/dev/null -print -quit; then
    mkdir ~/$ii
  fi
done

for ii in "${grizli_directories[@]}"; do
  if ! find ~/GRIZLI -maxdepth 1 -name $ii 2>/dev/null -print -quit; then
    mkdir ~/GRIZLI/$ii
  fi
done

# Run python setup lines
python grizli_setup.py $3
