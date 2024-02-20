# Scraper

A scraper that runs in an interval and saves everything in a global csv.

## Usage
run the scraper every 3 minutes
```console
./scraper.py start 180
```
stop the scraper
```console
./scraper.py stop
```
Initially no project gets published! To publish it we need to list all projects that were scraped
```console
./scraper.py list
```
and select project number 3 for example and add with 
```console
./scraper.py add 3
```
To finally make all additions and removals public
```console
./scraper.py publish
```
To remove a project that is public
```console
./scraper.py remove 3
./scraper.py publish
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
