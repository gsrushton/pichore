#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------

FROM ubuntu:20.04

ARG USER=user
ARG UID=1000
ARG GID=$UID
ARG USER_SHELL=zsh

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN    apt-get update \
    && apt-get -y install apt-utils \
                          build-essential \
                          cmake \
                          curl \
                          dialog \
                          git \
                          iproute2 \
                          language-pack-en \
                          libssl-dev \
                          lsb-release \
                          pkg-config \
                          python3 \
                          python3-dev \
                          python3-venv \
                          sudo \
                          $USER_SHELL 2>&1 \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to use if preferred - see https://aka.ms/vscode-remote/containers/non-root-user.
RUN    groupadd --gid $GID $USER \
    && useradd -m -s /bin/$USER_SHELL --uid $UID --gid $GID $USER \
    # Add sudo support for the non-root user
    && echo $USER ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USER\
    && chmod 0440 /etc/sudoers.d/$USER

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=

# Install poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.0.10
RUN    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 \
    && chmod a+x /opt/poetry/bin/poetry
ENV PATH=$PATH:/opt/poetry/bin

# Install Node
ARG NODE_VERSION=12.18.3
RUN curl https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz | tar xJ -C /opt
ENV PATH=$PATH:/opt/node-v$NODE_VERSION-linux-x64/bin

# Install Yarn
ARG YARN_VERSION=1.22.4
RUN curl -L https://github.com/yarnpkg/yarn/releases/download/v$YARN_VERSION/yarn-v$YARN_VERSION.tar.gz | tar xz -C /opt
ENV PATH=$PATH:/opt/yarn-v1.22.4/bin

USER $USER

WORKDIR /home/$USER

CMD ["tail", "-f", "/dev/null"]
