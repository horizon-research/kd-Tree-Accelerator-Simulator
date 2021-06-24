lines = open("stat_queries").readlines()
shorten_factor = 0.5
out = open("stat_queries" + str(shorten_factor), "w+")
length = int(shorten_factor * len(lines))
new_lines = lines[0:length+1]
out.writelines(new_lines)