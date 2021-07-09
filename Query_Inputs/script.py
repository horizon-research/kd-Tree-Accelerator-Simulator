file = open("testf")
data = file.readlines()

for i in range(len(data)):
    line = data[i]
    tokens = line.split()
    tokens[3] = '1'
    line = ' '.join(tokens)
    line = "KNN " + line + '\n'
    data[i] = line
    
file = open("testf", 'w+')
file.writelines(data)
