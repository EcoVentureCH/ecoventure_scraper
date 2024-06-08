FROM selenium/standalone-chrome
WORKDIR /usr/scrapp/

COPY . /usr/scrapp/

USER root
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install selenium
RUN python3 -m pip install beautifulsoup4 webdriver-manager

ENTRYPOINT ["python3", "/usr/scrapp/run_all.py"]