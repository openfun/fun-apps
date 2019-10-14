ARG EDXAPP_TAG=dogwood.3-1.0.0


# === BASE ===
FROM fundocker/edxapp:${EDXAPP_TAG}

ARG DOCKER_UID=1000
ARG DOCKER_GID=1000

USER root:root

# Install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
      libsqlite3-dev \
      mongodb && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${DOCKER_GID} edx || \
      echo "Group with ID ${DOCKER_GID} already exists." && \
    useradd \
      --create-home \
      --home-dir /home/edx \
      --uid ${DOCKER_UID} \
      --gid ${DOCKER_GID} \
      edx

# To prevent permission issues related to the non-priviledged user running in
# development, we will install development dependencies in a python virtual
# environment belonging to that user
RUN pip install virtualenv

# Create the virtualenv directory where we will install python development
# dependencies
RUN mkdir -p /edx/app/edxapp/venv && \
    chown -R ${DOCKER_UID}:${DOCKER_GID} /edx/app/edxapp/venv

# Change edxapp directory owner to allow the development image docker user to
# perform installations from edxapp sources (yeah, I know...)
RUN chown -R ${DOCKER_UID}:${DOCKER_GID} /edx/app/edxapp

# Copy the entrypoint that will activate the virtualenv
COPY ./scripts/entrypoint.sh /usr/local/bin/entrypoint.sh

# Switch to an un-privileged user matching the host user to prevent permission
# issues with volumes (host folders)
USER ${DOCKER_UID}:${DOCKER_GID}

# Create the virtualenv with a non-priviledged user
RUN virtualenv -p python2.7 --system-site-packages /edx/app/edxapp/venv

# Copy fun-apps sources
COPY --chown=${DOCKER_UID}:${DOCKER_GID} . /edx/app/fun

# Install fun-apps in editable mode
RUN cd /edx/app/fun && \
      bash -c "source /edx/app/edxapp/venv/bin/activate && \
               pip install -e . "

ENTRYPOINT [ "/usr/local/bin/entrypoint.sh" ]

