#!/bin/bash

echo $PWD
build_base()
{
docker build \
	--network host \
	-f Dockerfile.base \
	 -t aladdin-cas-base ../../
}

build_init()
{
docker build \
	-f Dockerfile.init \
	 -t aladdin-cas-init ../../
}

build_cas()
{
docker build \
	-f Dockerfile \
	 -t aladdin-cas ../../
}

case $1 in
	base)
		build_base
	;;
	init)
		build_init
	;;
	*)
		build_cas
	;;
esac
#rm -rf Dockerfile
