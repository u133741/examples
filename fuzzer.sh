#!/bin/bash

MAX_THREADS=40
ERROR_MSG="does not include a method|server does not expose service|bad argument type for built-in operation" # Kept 'cause could be usefull

function print_help(){
	echo "Usage: $0  [-h token] [-d data] [-t threads] -w word_list URL entry_point"
	echo -e "\t -u URL\t\t IP or hostname."
	echo -e "\t -e entry_point\t Full entry point/symbol. Ex: SimpleApp/LoginUser."
	echo -e "\t -d data\t Data in JSON format."
	echo -e "\t -h token\t Header value of the Cookie/Token."
	echo -e "\t -t threads\t Number of threads to use, default 40."
	echo -e "\t -w word_list\t File path of the wordlist to FUZZ."
	echo -e "\t -c\t\t Encode the wordlist (not implemented, always encodes)"
	echo -e "\t -v\t\t Verbose mode"
	echo -e "\nRemember to use the FUZZ keyword"
	echo -e "\nEXAMPLE:"
	echo './fuzzer.sh -H '"'"'token:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjE2OTAzNjY3NDJ9.JUrSNuANy8PL3VH7NjBXgMUGARHoFJ6B-qc3QlBiVHs'"'"' -d '"'"'{\"id\":\"FUZZ\"}'"'"' -w /usr/share/seclists/Fuzzing/SQLi/sqli-hacktricks.txt -v "10.10.11.214:50051" "SimpleApp.getInfo"'
}

##########################################################################################
cmd_line="grpcurl -plaintext"

while getopts "d:H:vt:w:h" opt #getopts doesn't work inside a function
do
	case $opt in

	d)
		DATA="$OPTARG"
		cmd_line="$cmd_line -d \"$OPTARG\""
		;;

	H)
		TOKEN="$OPTARG"
		cmd_line="$cmd_line -H \"$OPTARG\""
		;;

	t)
		MAX_THREADS="$OPTARG"
		;;

	w)
		WORDLIST="$OPTARG"
		;;
	
	v)
		cmd_line="$cmd_line -vv"
		;;

	h)
		echo "Help asked, help given."
		print_help
		exit 0
		;;

	*)
		print_help
		exit 1
		;;

	esac
done

shift $((OPTIND-1))

if [ "$#" -eq 2 ]; then
	cmd_line="$cmd_line $1 $2"
else
	print_help
	exit 1
fi

if [ -z "$WORDLIST" ]; then
	echo "No wordlist!!!!!"
	exit 1
fi

if ! grep "FUZZ" >/dev/null <<< "$cmd_line"
then
	echo "No FUZZ keyword found."
	exit 1
fi
##########################################################################################

function requests(){
	
	line_helper=$(tr -d "\r" <<< "$1")
	line_helper=$(jq -Rr '@uri' <<< "$line_helper")

	# Splited instead of using sed. Sed was adding single quotes to the output.
	before_fuzz=$(awk 'BEGIN { FS = "FUZZ" } ; { print $1 }' <<< "$cmd_line")
	after_fuzz=$(awk 'BEGIN { FS = "FUZZ" } ; { print $2 }' <<< "$cmd_line")

	FUZZ="$before_fuzz""$line_helper""$after_fuzz"

	out="$(bash -c "$FUZZ" 2>&1 | tr -d '\n' | grep -vP "$ERROR_MSG")"

	if ! [ -z "$out" ]
	then
		echo "$out"
		echo "$1"
	fi
}

function thread_helper(){
	i=0

	while read -r line
	do
		requests "$line"

		i=$((i+1))

		if [ $i -eq $MAX_THREADS ]
		then
			wait
			i=0
		fi
	done < "$WORDLIST"
}

thread_helper


































