#!/bin/bash

# Copy the all alogrithms graphs from a directory to the proper location in
# the document build tree

function usage {
	src=`basename $0`
cat <<EOF
${src} <OUTPUT DIRECTORY> <DOCUMENT ROOT>

Copies the graphs related to the proof of context into the
document build tree at the correct location. If <DOCUMENT ROOT> is not
specified a guess is made and interactively verified.
EOF
}

# selection of graphs
sel=(
	all-tiny/graphs/sched-by-count-cdf-all.eps
	all-tiny/graphs/schedulability-cache-reuse-count-all.eps
    )

ODIR=${1}
DDIR=${2:-../../oleaf.git/}

if [ "${ODIR}" == "" ] ; then
	echo "An output directory must be supplied"
	usage
	exit -1
fi

ODIR=${ODIR}/
for file in ${sel[@]} ; do
	path=${ODIR}/${file}
	if [ -f ${path} ] ; then  
	   echo $path exists
	fi
done

echo $DDIR

if [ ! -d ${DDIR} ] ; then
	echo "A document root is required [$DDIR]"
	usage
	exit -1
fi
echo ${DDIR} exists

DDIR=${DDIR}/graphs/
echo $DDIR
mkdir -p ${DDIR}


for file in ${sel[@]} ; do
	src=$2
	src+="/eval/"
	src+=$file
	dst=${DDIR}/
	dst+=$(basename $file)


	echo "${src} -> ${dst}"
	cp ${src} ${dst}
done
