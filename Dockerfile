FROM colmap/colmap:latest

ARG PYTHON_VERSION=3.10

RUN apt-get update -y && \
    apt-get install -y unzip wget software-properties-common git && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y python${PYTHON_VERSION} && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python${PYTHON_VERSION} get-pip.py && \
    rm get-pip.py && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN git clone --recursive https://github.com/Jourdelune/colmap-api.git

WORKDIR /colmap-api

RUN git submodule update --init --recursive && \
    pip3 install --upgrade pip && \
    pip3 install ./Hierarchical-Localization && \
    pip3 install . && \
    pip3 cache purge

ENV PYTHONPATH="/colmap-api/Hierarchical-Localization"
ENV PYTHONPATH="/colmap-api/Hierarchical-Localization:${PYTHONPATH}"

EXPOSE 8000

CMD ["fastapi", "run", "api.py"]
