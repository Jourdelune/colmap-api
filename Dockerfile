FROM colmap/colmap:latest

ARG PYTHON_VERSION=3.10

RUN apt-get update -y
RUN apt-get install -y unzip wget software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get -y update && \
    apt-get install -y python${PYTHON_VERSION}
RUN wget https://bootstrap.pypa.io/get-pip.py && python${PYTHON_VERSION} get-pip.py
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1
RUN apt-get install -y git
RUN git clone --recursive https://github.com/Jourdelune/colmap-api.git

WORKDIR /colmap-api

RUN pip3 install --upgrade pip
RUN git submodule update --init --recursive

# Debug: voir le contenu du répertoire
# RUN ls -la
# RUN ls -la Hierarchical-Localization/

# RUN pip3 install ./Hierarchical-Localization
# RUN pip3 install -r pyproject.toml