#!/bin/bash

# Edit the content of this section to install your dependencies.
# These commands run as root, but the attack/profiling do not! (and they do not
# have network access).
# The setup/ directory of your submission is accessible as setup/
apt-get -y update
apt-get -y install python3-minimal python3-venv python3-pip
# Root package install is generally not recommended with pip, but here its fine
# (single-purpose isolated container).
cd /setup
pip install -r /setup/requirements.txt
# We can run arbitrary code here.

