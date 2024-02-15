# Scraper

A scraper that runs in an interval and saves everything in a global csv.

## Usage
run the scraper every 3 minutes
```shell
./scraper.py start 180
```
stop the scraper
```shell
./scraper.py stop
```
🚧 TODO

## Installation

install chrome wbdriver (Ubuntu 22.04)
```shell
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt update
sudo apt --fix-broken -y install
```
(adapted from this website: https://github.com/password123456/setup-selenium-with-chrome-driver-on-ubuntu_debian)

install other dependencies with pip3 globally
```shell
pip3 install pandas selenium webdriver-manager woocommerce pillow
```
or install dependencies in environement using miniconda 
```shell
mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
~/miniconda3/bin/conda init bash
conda create -n webscraper python=3.11.5
conda activate webscraper
conda install selenium pandas
pip install webdriver-manager woocommerce pillow
```

