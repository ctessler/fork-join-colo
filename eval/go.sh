#!/bin/bash

# Get the directory of this script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Set the PATHS
PATH=${PATH}:${SCRIPT_DIR}/bin
if [ "$PYTHONPATH" != "" ] ; then
	PYTHONPATH=${PYTHONPATH}:
fi
PYTHONPATH=${PYTHONPATH}${SCRIPT_DIR}/python-libs
export PYTHONPATH

function usage {
	src=`basename $0`
	echo "$src [options] <CONTEXT>.json <CONTEXT_DIR>"
	echo "OPTIONS:"
	echo "	-M|--cores	The maxiumum number of cores to explore"
	echo "	-T|--timeout	Timeout (in seconds) for exact methods BROKEN"
	echo "	-X|--no-exact	Do not execute the exact methods"
	echo "	-U|--bucket-n	Size of the task buckets"
	exit 1
}

short_opts="M:,T:,X,U:"
long_opts="cores:,timeout:,no-exact,bucket-n:"
args=`getopt -o ${short_opts} -l ${long_opts} -- "$@"`
eval set -- ${args}

CORES=""
TIMEOUT=""
NOEXACT=""
BUCKET=""
while true
do
	case "$1" in
		-M)
		;&
		--cores)
			CORES="-M $2"
			shift 2
			;;
		-T)
			;&
		--timeout)
			TIMEOUT="-T $2"
			shift 2
			;;
		-U)
			;&
		--bucket-n)
			BUCKET="-U $2"
			shift 2
			;;
		-X)
			;&
		--no-exact)
			NOEXACT="-X"
			shift 1
			;;
		--)
			shift
			break
			;;
	esac
done


CTX=${@:$OPTIND:1}
shift
DIR=${@:$OPTIND:1}

if [ "$DIR" == "" ]
then
	usage
fi

function error_check() {
	status=$1
	str=$2

	if [ $1 -eq 0 ] ; then
		return 0
	fi

	echo "error: $str"
	exit 1   
}

SKIPGEN=0
if [ -d ${DIR} ] ; then
	echo "${DIR} exists, skipping generation"
	SKIPGEN=1
fi

# Generate tasks
if [ ${SKIPGEN} -eq 0 ] ; then 
	gen-objects.py -c ${CTX} ${DIR}
	error_check $? 'gen-objects.py'

	gen-tasks-par.py -c ${CTX} ${DIR}
	error_check $? 'gen-tasks.py'

	filter-tasks.py ${DIR} 
	error_check $? 'filter-tasks.py'

	trim-tasks-to-bucket.py ${DIR} ${BUCKET}
	error_check $? 'trim-tasks-to-bucket.py'
fi

display-buckets.py ${DIR}
while false
do
      read -r -p "Continue? [Y/n] " input
      case $input in
	      [yY][eE][sS]|[yY])
		      echo "Continuing ... "
		      break
		      ;;
	      [nN][oO]|[nN])
		      echo "Aborting!"
		      exit 1
		      ;;
	      *)
		      echo "Invalid input..."
		      ;;
      esac
done


if [ "${NOEXACT}" == "" ] ; then
	for TASK in ${DIR}/tasks/*.json
	do
		opt-task-no-colo.py ${CORES} ${TASK} ${TIMEOUT}
		error_check $? 'opt-task-no-colo.py'

		opt-task-colo.py ${CORES} ${TASK} ${TIMEOUT}
		error_check $? 'opt-task-colo.py'
	done
fi

# Let the DAG methods set the core limit for the heuristics
dag-m-par.py ${DIR}
error_check $? 'dag-m-par.py'

dag-gb-par.py ${DIR}
error_check $? 'dag-gb-par.py'

dag-lp-par.py ${DIR}
error_check $? 'dag-lp-par.py'

3-parm-par.py ${DIR} ${CORES}
error_check $? '3-parm-par.py'

3-parm-hd-par.py ${DIR} ${CORES}
error_check $? '3-parm-hd-par.py'

2-gram-par.py ${DIR} ${CORES}
error_check $? '2-gram-par.py'

tabulate.py ${DIR} ${NOEXACT}
error_check $? 'tabulate.py'

graph.py ${DIR} ${NOEXACT}
error_check $? 'graph.py'

echo "DAG methods calculate cores without concern for limitations"
N=$(max-cores.py ${DIR} | tail -n 1 | sed 's/ //g')
max-cores.py ${DIR}

echo "Generating PDF"
make GRAPHDIR=${DIR}
