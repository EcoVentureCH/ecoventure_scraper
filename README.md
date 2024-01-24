# Scraper Test

Simple test to run a scraper in an interval.

# Quick Start

https://github.com/password123456/setup-selenium-with-chrome-driver-on-ubuntu_debian

install chrome wbdriver
```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb
apt update
apt --fix-broken install
```

install miniconda
```
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
conda create -n webscraper python=3.11.5
conda activate webscraper
pip3 install selenium
bash run.sh
```