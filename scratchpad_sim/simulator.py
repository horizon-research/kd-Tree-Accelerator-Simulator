from scratchpad import Scratchpad
import sys

def main():
    print(len(sys.argv))
    print(sys.argv[0])
    print(sys.argv[1])

    s = Scratchpad(8, 3000000)
    trace_file = open(sys.argv[1])
    trace_lines = trace_file.readlines()
    for line in trace_lines:
        if line != "\n":
            line_tokens = line.split()
            if line_tokens[0] == "R":
                address = int(line_tokens[1])
                print(s.read(address))

    
main()