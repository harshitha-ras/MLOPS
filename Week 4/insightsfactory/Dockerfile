FROM apache/airflow:2.10.5

# Switch to root to install system dependencies
USER root

# Install Git, Git LFS, and other necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Git LFS
RUN wget https://packagecloud.io/github/git-lfs/packages/debian/bullseye/git-lfs_3.2.0_amd64.deb/download -O git-lfs.deb && \
    dpkg -i git-lfs.deb && \
    rm git-lfs.deb && \
    git lfs install

# Ensure proper permissions for dags directory
RUN mkdir -p /opt/airflow/dags && \
    chown -R airflow:root /opt/airflow/dags

# Create repo directory with proper permissions
RUN mkdir -p /opt/airflow/repo && \
    chown -R airflow:root /opt/airflow/repo

# Switch back to the airflow user
USER airflow

# Initialize Git LFS for the airflow user
RUN git lfs install