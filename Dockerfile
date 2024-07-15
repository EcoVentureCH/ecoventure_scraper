FROM selenium/standalone-chrome
WORKDIR /usr/scrapp/

USER root
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN python3 -m pip install selenium
RUN python3 -m pip install beautifulsoup4 webdriver-manager pandas requests

# copy at the end to use caching
COPY . /usr/scrapp/

ENTRYPOINT ["python3", "/usr/scrapp/run_all.py", "/usr/scrapp_volume/"]