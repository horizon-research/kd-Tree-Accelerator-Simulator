lines = open("frame_30").readlines()
shorten_factor = 0.125
out = open("frame_30" + str(shorten_factor), "w+")
length = int(shorten_factor * len(lines))
new_lines = lines[0:length+1]
out.writelines(new_lines)