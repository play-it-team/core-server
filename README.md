# play.it

[![Build Status](https://travis-ci.org/play-it-team/core-server.svg?branch=master)](https://travis-ci.org/play-it-team/core-server) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/0a713482e3e846c9ae6d664a1945b0d2)](https://www.codacy.com/app/abhi1693/core-server?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=play-it-team/core-server&amp;utm_campaign=Badge_Grade)

# Requirements

Install the required libraries

```
sudo apt install gdal-bin libgdal-dev python3-gdal binutils libproj-dev
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt xenial-pgdg main" >> /etc/apt/sources.list'
wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install postgresql-10
sudo apt install postgresql-10-postgis-2.4
sudo apt install postgresql-10-postgis-scripts
sudo apt install postgis
sudo apt install postgresql-10-pgrouting
```