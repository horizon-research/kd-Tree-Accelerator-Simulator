file = open("stat_queries")
data = file.readlines()

for i in range(len(data)):
    line = data[i]
    tokens = line.split()
    tokens[3] = '3'
    line = ' '.join(tokens)
    line = "KNN " + line + '\n'
    data[i] = line
    
file = open("stat_queries", 'w+')
file.writelines(data)
