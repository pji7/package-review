#!/bin/bash
# ================= Configuration =================
SOURCE_LIST="/home/data/pack_list.txt"
INPUT_DIR="/home/input"
TEMP_DIR="/home/temp"

# ==================================================
cd "$TEMP_DIR" || exit 1

while read -r package; do
  echo "===== Processing $package ====="

  if ! apt source "$package"; then
    echo "Failed to download source for $package"
    continue
  fi

  patched_src_dir=$(find . -maxdepth 1 -type d -name "${package}-*" | sort | head -n 1)
  if [[ ! -d "$patched_src_dir" ]]; then
    echo "Cannot find unpacked directory for $package"
    continue
  fi

  patched_name="${patched_src_dir}_patched"
  mv "$patched_src_dir" "$patched_name"
  mv "$patched_name" "$INPUT_DIR/"

  orig_tar=$(ls ${package}_*.orig.tar.* 2>/dev/null | head -n 1)
  if [[ -z "$orig_tar" ]]; then
    echo "No .orig.tar.* file found for $package"
    continue
  fi

  echo "Found original source: $orig_tar"

  before_dirs=($(find . -maxdepth 1 -type d))

  case "$orig_tar" in
    *.tar.gz)  tar -xzf "$orig_tar" ;;
    *.tar.bz2) tar -xjf "$orig_tar" ;;
    *.tar.xz)  tar -xJf "$orig_tar" ;;
    *)
      echo "Unsupported archive format: $orig_tar"
      continue
      ;;
  esac

  after_dirs=($(find . -maxdepth 1 -type d))
  for dir in "${after_dirs[@]}"; do
    skip=false
    for old in "${before_dirs[@]}"; do
      [[ "$dir" == "$old" ]] && skip=true && break
    done
    [[ "$skip" == false ]] && pure_dir="$dir"
  done

  if [[ -d "$pure_dir" ]]; then
    pure_name="${pure_dir}_pure"
    mv "$pure_dir" "$pure_name"
    mv "$pure_name" "$INPUT_DIR/"
  else
    echo "Failed to detect pure source directory for $package"
    continue
  fi

  echo "Done with $package"
  echo

  echo "Cleaning up temp directory..."
  rm -rf "$TEMP_DIR"/*
done < "$SOURCE_LIST"

echo "ALL done. Patched and pure source trees are in $INPUT_DIR"
