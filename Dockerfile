FROM selenium/standalone-chrome
WORKDIR /usr/scrapp/

USER root

RUN apt-get update
RUN apt-get install -y python3-pip
RUN apt-get install -y python3-full
RUN python3 -m pip install webdriver-manager --break-system-packages
RUN apt-get install -y python3-selenium
RUN apt-get install -y python3-bs4
RUN apt-get install -y python3-requests
RUN apt-get install -y python3-pandas

COPY . /usr/scrapp/

ENTRYPOINT ["python3", "/usr/scrapp/run_all.py", "/usr/scrapp_volume/"]