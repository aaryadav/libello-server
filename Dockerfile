ARG ROOT_CONTAINER=ubuntu:22.04
ARG PYTHON_VERSION=3.8

FROM $ROOT_CONTAINER

LABEL maintainer="Aaryaman <yadavaaryaman@gmail.com>"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system packages
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    bzip2 \
    ca-certificates \
    locales \
    sudo \
    tini \
    wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

ENV CONDA_DIR=/opt/conda

# Set up Python with mamba
RUN set -x && \
    arch=$(uname -m) && echo "Architecture: $arch" && \
    if [ "${arch}" = "x86_64" ]; then \
        arch="64"; \
    fi && \
    echo "Downloading micromamba for architecture: $arch" && \
    wget --progress=dot:giga -O /tmp/micromamba.tar.bz2 \
        "https://micromamba.snakepit.net/api/micromamba/linux-${arch}/latest"

RUN tar -xvjf /tmp/micromamba.tar.bz2 --strip-components=1 bin/micromamba && \
    rm /tmp/micromamba.tar.bz2

RUN echo "Python Version: ${PYTHON_VERSION}" && \
    echo "Conda Directory: ${CONDA_DIR}" && \
    PYTHON_SPECIFIER="python=${PYTHON_VERSION}" && \
    if [[ "${PYTHON_VERSION}" == "default" ]]; then PYTHON_SPECIFIER="python"; fi && \
    ./micromamba install \
        --root-prefix="${CONDA_DIR}" \
        --prefix="${CONDA_DIR}" \
        --yes \
        --channel conda-forge \
        "${PYTHON_SPECIFIER}" \
        'mamba' \
        'jupyter' \
        'jupyter_server' \
        && rm ./micromamba

ENV PATH="${CONDA_DIR}/bin:$PATH"

RUN mamba list python | grep '^python ' | tr -s ' ' | cut -d ' ' -f 1,2 >> "${CONDA_DIR}/conda-meta/pinned" && \
    mamba clean --all -f -y

# # Add session.py or other necessary files
# ADD session.py ./

# # Configure container startup
# ENTRYPOINT ["tini", "-g", "--"]
# CMD ["python3", "session.py"]

EXPOSE 8888

# Set up environment variables

ENV PROJECT_DEPENDENCIES=""

# Add the script that will create the conda environment
ADD create_env.sh /usr/local/bin/create_env.sh
RUN chmod +x /usr/local/bin/create_env.sh

# Configure container startup
ENTRYPOINT ["tini", "-g", "--"]
CMD ["/usr/local/bin/create_env.sh"]