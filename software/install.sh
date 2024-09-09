#!/bin/sh
#
# Install the sbc code on a client single board computer

sudo apt update
sudo apt dist-upgrade
sudo apt install tmux

curl -fsSL https://tailscale.com/install.sh | sh

for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker $USER
sudo reboot

#Now set up tailscale onto the elec.ac.nz tailcale network. This is done using 

echo "After Reboot, do the following:"
echo "    sudo raspi-config"
echo "    sudo tailscale up   -- enable SPI"
