#!/usr/bin/env bash

# The aim of this script is to generate missing initial migrations for apps
# distributed with fun-apps.
#
# usage: scripts/migrations.sh [edxapp image tag]
#
# default: dogwood.3-1.1.0
# example: scripts/migrations.sh eucalyptus.3-1.0.0

declare EDXAPP_TAG
declare PROJECT_DIRECTORY
declare SETTINGS

EDXAPP_TAG="${1:-eucalyptus.3-1.0.0}"
PROJECT_DIRECTORY="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit; pwd -P)"

# Terminal colors
declare -r COLOR_INFO='\033[0;36m'
declare -r COLOR_RESET='\033[0m'
declare -r COLOR_WARNING='\033[0;33m'


function usage(){

  echo -e "usage: migrations.sh [edxapp image]\\n"
  exit 10
}


function get_apps(){

  find "${PROJECT_DIRECTORY}" -maxdepth 2 -name "models.py" -exec dirname {} \; | sort
}


function generate_app_tmp_settings(){

  declare apps
  declare tmp_dir
  declare tmp_settings

  # Convert fun-apps applications from an absolute path to their name, e.g.
  # /home/foo/projecs/fun-apps/teachers to teachers, and then convert this name
  # to a python string list item, e.g. "'teachers',"
  #
  # Note that we also exclude the fun_api application as the admin model breaks
  # management command calls.
  apps=$(get_apps | grep -v "fun_api" | xargs -n 1 -I %% sh -c "basename %%" | sed "s/\\(.*\\)/  '\\1',/g")
  tmp_dir="/tmp/fun_apps"
  tmp_settings=$(mkdir -p ${tmp_dir} && mktemp -p "${tmp_dir}" --suffix ".py" "settings_XXXXXXXX")

  echo "from .docker_run_production import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/tmp/db',
    }
}

LANGUAGES = (('fr', 'Fran\xc3\xa7ais'), ('en', 'English'), ('de-de', 'Deutsch'))

INSTALLED_APPS += (
${apps}
)
" > "${tmp_settings}"

  echo "${tmp_settings}"
}

function get_target_image(){

  echo "edxapp:${EDXAPP_TAG}-fun-apps-dev"
}

function build_docker_image() {

  cd "${PROJECT_DIRECTORY}" && \
    docker build \
      --build-arg EDXAPP_TAG="${EDXAPP_TAG}" \
      --build-arg DOCKER_UID="$(id -u)" \
      --build-arg DOCKER_GID="$(id -g)" \
      -t "$(get_target_image)" \
      .
}

function add_app_migrations(){

  declare app
  declare app_path

  app_path="${1}"
  app=$(basename "${app_path}")

  echo -e "${COLOR_INFO}== ${app}${COLOR_RESET}"

  # No models has been defined for this app
  if [[ ! -s "${app_path}/models.py" && ! -d "${app_path}/models" ]]; then
    echo -e "${COLOR_WARNING}SKIPPED: no model defined!${COLOR_RESET}"
    return
  fi

  # Ensure the docker image exists, and compile it if required
  if [[ $(docker images "$(get_target_image)" | wc -l) -eq 1 ]]; then
    build_docker_image
  fi

  docker run --rm -ti \
    -u "$(id -u):$(id -g)" \
    -v "${PROJECT_DIRECTORY}:/edx/app/fun" \
    -v "${SETTINGS}:/edx/app/edxapp/edx-platform/lms/envs/fun/app.py" \
    -v "$(mktemp -d):/edx/var" \
    -e "DJANGO_SETTINGS_MODULE=lms.envs.fun.app" \
    "$(get_target_image)" \
    bash -c "cd /edx/app/fun && \
             pip install -e . && \
             cd /edx/app/edxapp/edx-platform && \
             python manage.py lms makemigrations ${app}"
}

# -- main --
SETTINGS=$(generate_app_tmp_settings)

echo -e "${COLOR_INFO}== SETTINGS${COLOR_RESET}"
cat "${SETTINGS}"

for app in $(get_apps); do
  add_app_migrations "${app}"
done
