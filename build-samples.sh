#!/bin/bash
pushd samples
ls -d */ | while read line; do
pushd $line
zip "${line%/}.zip" *
mv -f "${line%/}.zip" ../
popd
done
popd
