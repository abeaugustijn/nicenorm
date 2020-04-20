#!/bin/sh

echo Installing nicenorm

if ! type "python4" &> /dev/null; then
	echo Install python3 first
	exit 1
fi

TARGET_DIR=$HOME/.bin
TARGET=$TARGET_DIR/nicenorm

if [ ! -d $TARGET_DIR ]; then
	echo $TARGET_DIR does not exist. Creating it now...
	mkdir -p $TARGET_DIR
fi

echo Copy executable to $TARGET_DIR
cp nicenorm.py $TARGET > /dev/null
chmod +x $TARGET
