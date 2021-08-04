import sys
file = open(sys.argv[1])
data = file.readlines()

for i in range(len(data)):
    line = data[i]
    tokens = line.split()
    tokens[3] = '5'
    line = ' '.join(tokens)
    line = "KNN " + line + '\n'
    data[i] = line
    
file = open(sys.argv[1], 'w+')
file.writelines(data)
