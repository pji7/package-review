# Description:
#   This dockerfile is written to create a basic testing environment for debian linux packages.
#   This environment should cinlude basic binary packages, input packages, SAST tools.

# Pull Debian 11.
FROM debian:bullseye

# Update /etc/apt/sources.list file in the image to include deb-src line
RUN echo "deb-src http://deb.debian.org/debian bullseye main" >> /etc/apt/sources.list

# Fix locale
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

# Apt update && upgrade
RUN apt update -y
RUN apt upgrade -y

# Install essential tools
# Basic: dpkg-dev, git, nano, quilt,
# SASTT: python3, python3-pip, flawfinder, cppcheck, clang-tools, semgrep. (TODO - infer, sonarqube)
RUN apt install -y \
  dpkg-dev \
  devscripts \
  # debconf \
  # fakeroot \
  # lintian \
  # mc \
  # piuparts \
  # apt-rdepends \
  # cpanminus \
  quilt \
  cloc \
  git \
  nano \
  python3-pip \
  flawfinder \
  cppcheck \
  clang-tools 
#  tree
#  vim 


# WORKDIR /root

RUN python3 -m pip install semgrep

RUN mkdir -p \
  /home/temp \
  /home/input \
  /home/output \
  /home/semgrep \
  /home/sourcelist 

