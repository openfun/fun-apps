#!/usr/bin/env bash

declare REPOSITORY_ROOT="${1:-.}"

echo -e "include LICENSE\\ninclude README.md"

# For every python module from the repository root
for module_init in $(find "${REPOSITORY_ROOT}" -maxdepth 2 -type f -name '__init__.py'); do

	module=$(dirname "${module_init}")
	non_py_files=$(find "${module}" ! \( -name "*.py" -o -name "*.pyc" \) -type f)

	# This module only contains python sources
	if [[ -z "${non_py_files}" ]]; then
		continue
	fi

	# Prepare the MANIFEST.in line for this module
	echo -n "recursive-include $(echo "${module} " | sed 's/^\.\///')"

	# Get all distinct extensions from non pythonic files in this module
	# Edge case: the VERSION file (files without extension are not
	# supported yet).
	echo "${non_py_files}" | \
		xargs -n 1 basename | \
		awk -F "." '{print $NF}' | \
		grep -v VERSION | \
		sort | \
		uniq | \
		sed "s/^\\(.*\\)$/\\*\\.\\1/g" | \
		xargs
done | sort
