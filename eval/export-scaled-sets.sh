#!/bin/bash

# Copy the all alogrithms graphs from a directory to the proper location in
# the document build tree

function usage {
	src=`basename $0`
cat <<EOF
${src} <OUTPUT DIRECTORY> <DOCUMENT ROOT>

Copies the graphs related to the Y task sets into the document build
tree at the correct location. If <DOCUMENT ROOT> is not specified  
a guess is made and interactively verified.
EOF
}

# selection of graphs
sel=( avg-reuse-by-set.eps
      pctsched-count-by-set.eps
    )
      

ODIR=${1}
DDIR=${2:-../../oleaf.git/}

if [ "${ODIR}" == "" ] ; then
	echo "An output directory must be supplied"
	usage
	exit -1
fi

ODIR=${ODIR}/graphs

for file in ${sel[@]} ; do
	path=${ODIR}/${file}
	if [ -f ${path} ] ; then
	   echo $path exists
	fi
done

if [ ! -d ${DDIR} ] ; then
	echo "A document root is required"
	usage
	exit -1
fi
echo ${DDIR} exists

DDIR=${DDIR}/graphs/scaled
mkdir -p ${DDIR}

for file in ${sel[@]} ; do
	src=${ODIR}/${file}
	dst=${DDIR}/${file}

	echo "${src} -> ${dst}"
	cp ${src} ${dst}
done

