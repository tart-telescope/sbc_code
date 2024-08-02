#!/bin/sh
#
# Install the sbc code on a client single board computer

sudo apt update
sudo apt dist-upgrade

curl -fsSL https://tailscale.com/install.sh | sh

curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker $USER
sudo reboot

#Now set up tailscale onto the elec.ac.nz tailcale network. This is done using 

# sudo raspi-config
# sudo tailscale up
