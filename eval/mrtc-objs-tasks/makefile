json=../ctxs/mrtc-tasks.json
all: summary.txt


tasks: $(json)
	rm -rf tasks
	gen-tasks.py -c $(json) .

tasks.csv: tasks
	tabulate.py .

summary.txt: data.txt
	cat data.txt | awk '{print $$2}'  | /home/ct/ws/st/script/st > summary.txt
	cat summary.txt

data.txt: tasks.csv
	cat tasks.csv | sed 1d| sed 's/,/ /g' | awk '{print $$1 " " $$3}' > data.txt

clean:
	rm -rf tasks.csv summary.txt tasks
