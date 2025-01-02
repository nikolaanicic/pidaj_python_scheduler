#!/bin/bash
source seminarski_venv/bin/activate
mkdir -p results

function call_benchmark(){
	python main.py $1 $2 | python analyzer.py
}
export -f call_benchmark

client_calls=(5 10 15 20 25 30 50)
retries=(1 5 10)

parallel --group --tag --eta 'call_benchmark {}' ::: "${client_calls[@]}" ::: "${retries[@]}"