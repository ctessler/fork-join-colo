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


evaldir=$3
graphdir=$4

# selection of graphs
sel=(
     	$graphdir/graphs/sched-by-count-cdf-all.eps
	$graphdir/graphs/schedulability-cache-reuse-pct-all.eps
	$graphdir/graphs/sched-by-count-cdf-approx.eps
)


if [ "$3" == "verify" ] 
then
	sel=(
	     	prov-group-e/graphs/sched-by-count-cdf-all.eps
		prov-group-e/graphs/schedulability-cache-reuse-pct-all.eps
		prov-group-x/graphs/sched-by-count-cdf-approx.eps
	)
fi

if [ "$3" == "simulation_small" ] 
then
	sel=(
	     	all-small/graphs/sched-by-count-cdf-all.eps
		all-small/graphs/schedulability-cache-reuse-pct-all.eps
		all-small/graphs/sched-by-count-cdf-approx.eps
	)
fi

if [ "$3" == "simulation_tiny" ] || [ "$3" == "quick" ]
then
	sel=(
	     	all-tiny/graphs/sched-by-count-cdf-all.eps
		all-tiny/graphs/schedulability-cache-reuse-pct-all.eps
		all-tiny/graphs/sched-by-count-cdf-approx.eps
	)
fi

if [ "$3" == "simulation_set_e" ] 
then
	sel=(
	     	group-e/graphs/sched-by-count-cdf-all.eps
		group-e/graphs/schedulability-cache-reuse-pct-all.eps
		group-egraphs/sched-by-count-cdf-approx.eps
	)
fi

if [ "$3" == "simulation_set_x" ] 
then
	sel=(
	     	group-x/graphs/sched-by-count-cdf-all.eps
		group-x/graphs/schedulability-cache-reuse-pct-all.eps
		group-x/graphs/sched-by-count-cdf-approx.eps
	)
fi

if [ "$3" == "all" ] 
then
	echo all
	sel=(
	     	group-e/graphs/sched-by-count-cdf-all.eps
		group-e/graphs/schedulability-cache-reuse-pct-all.eps
		group-x/graphs/sched-by-count-cdf-approx.eps
	)
fi



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



DDIR=${DDIR}/"$3"/


echo $DDIR
mkdir -p ${DDIR}


for file in ${sel[@]} ; do
	src=$2
	src+="/eval/"
	src+=$file
	dst=${DDIR}/
	dst+=$(basename $file)

	if [ -e ${src} ]
	then
		echo "${src} -> ${dst}"
		cp ${src} ${dst}
	fi
done