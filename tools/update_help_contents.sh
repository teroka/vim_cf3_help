#!/bin/bash

# Quickhax to update the help files.

# To use this, you need to have github.com/cfengine/documentation.git
# cloned to local dir. This uses it to check what to crawl and get their
# relevant urls.

# tweak these to suite your needs
cf3funcs="${HOME}/.vim/doc/cf3funcs.txt"
cf3specialvars="${HOME}/.vim/doc/cf3specialvars.txt"
cf3promisetypes="${HOME}/.vim/doc/cf3promisetypes.txt"
# local path to the github.com:cfengine/documentation repo
cf3docs="${HOME}/git/cfengine-documentation"

# Check that we have the docs pulled
[[ -d "${cf3docs}/.git" ]] || exit 1

url_prefix="https://cfengine.com/docs/3.5"

update_functions(){
  # get rid of old helpfile if we have it
  [[ -f "${cf3funcs}" ]] && rm -i ${cf3funcs}

  # This here vomit dumps the functions and tweaks the contents to work with vim.
  for i in $(find ${cf3docs}/reference/functions/ -maxdepth 1 -iname '*.markdown'); do
    file=${i##*/}
    x=${file%%.*}
    echo "Parsing function: ${x}()"
    url_suffix=$(awk '/alias:/ { print $NF}' ${i} )
    url="${url_prefix}/${url_suffix}"
    if [[ ${x} =~ .*intrealstring.* ]]; then
      foo="int real string"
      y=$(echo ${x} | sed -r 's/intrealstring/zzz/')
      z=$(echo ${x} | sed -r 's/intrealstring/\\[int\\|real\\|string\\]/')
      for var in ${foo}; do
        echo ${y} |sed -r "s/zzz/${var}/;s/(.*)/\*\1\*/" >> ${cf3funcs}
      done
      links -dump ${url} |egrep "^\s+${z}$" -A9999|egrep -B9999 '\s+\-\^' >> ${cf3funcs}
    else
      links -dump ${url} |egrep "^\s+${x}$" -A9999|egrep -B9999 '\s+\-\^' |\
         sed -r "s/^\s{30,}\b(${x})\b/\*cf3-\1\*/g" >> ${cf3funcs}
    fi
  done 
}

update_special_vars(){
  # get rid of old helpfile if we have it
  [[ -f "${cf3specialvars}" ]] && rm -i ${cf3specialvars}

  for i in $(find ${cf3docs}/reference/special-variables/ -maxdepth 1 -iname '*.markdown'); do
    file=${i##*/}
    x=${file%%.*}
    echo "Parsing special variable: \"${x}\""
    url_suffix=$(awk '/alias:/ { print $NF}' ${i} )
    url="${url_prefix}/${url_suffix}"
    links -dump ${url} |egrep "^\s+\b${x}$\b" -A9999|egrep -B9999 '\s+\-\^' | \
       sed -r "s/^\s{30,}\b(${x})\b/\*cf3-\1\*/g" >> ${cf3specialvars}
  done 

}

update_promise_types(){
  # get rid of old helpfile if we have it
  [[ -f "${cf3promisetypes}" ]] && rm -i ${cf3promisetypes}

  for i in $(find ${cf3docs}/reference/promise-types/ -maxdepth 1 -iname '*.markdown'); do
    file=${i##*/}
    dir=${i%/*}
    x=${file%%.*}
    [[ -d ${dir}/${x} ]] && continue
    echo "Parsing promise type: \"${x}\""
    url_suffix=$(awk '/alias:/ { print $NF}' ${i} )
    url="${url_prefix}/${url_suffix}"
    links -dump ${url} |egrep "^\s+\b${x}$\b" -A9999|egrep -B9999 '\s+\-\^' | \
      sed -r "s/^\s{30,}\b(${x})\b/\*cf3-\1\*/g" >> ${cf3promisetypes}
  done 

}

update_functions
update_special_vars
update_promise_types



