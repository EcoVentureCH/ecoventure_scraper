# ecoventure_scraper

Build docker container including selenium

```console
docker build -t scrapp .
```

Run once in docker container, just runs through all websites and prints it for now.

```console
docker run -it scrapp
```

# Scraper (OLD - TO BE MOVED)

A scraper that runs in an interval and saves everything in a global csv named projects.csv. in scraper_definitions.py every function that is defined will be run as a scraper. For now there is conda() and seedrs().

## Usage
run the scraper every 10 minutes -> it generates projects.csv
```console
./scraper.py start 600
```
stop the scraper
```console
./scraper.py stop
```
Initially no project gets published! To publish it we first need to list all projects that were scraped
```console
./scraper.py list
```
and then select projects number 0, 1, 2 and 6 for example to add with
```console
./scraper.py add 0 1 2 6
```
To finally make all additions and removals public
```console
./scraper.py publish
```
To remove a projects that are public
```console
./scraper.py remove 0 2
./scraper.py publish
./scraper.py list
```
To add then remove all projects
```console
./scraper.py add --all
./scraper.py publish
./scraper.py remove -all
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
pip3 install pandas selenium webdriver-manager woocommerce pillow beautifulsoup4 pyarrow
```
