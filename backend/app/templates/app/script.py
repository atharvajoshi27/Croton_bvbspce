file_name = input('Enter file name: ')
lines = []
exists = False
load_static = "{% load static %}\n"
with open(file_name, 'r') as fr:
    while True:
        line = fr.readline()
        line_prev = line
        if not line:
            break
        if line == load_static:
            exists = True

        breaklist = line.split("=")
        for i in range(len(breaklist)):
            if breaklist[i].startswith('"assets/') or breaklist[i].startswith('"forms/'):
                index = 1 + breaklist[i][1:].find('"')
                breaklist[i] = "{% static 'app/" + f"{breaklist[i][1:index]}" + "' %}" + breaklist[i][index+1:]
                # breaklist_2[0] = "{% static 'backend/" + f"{breaklist_2[0][1:-1]}" + "' %}"
                # breaklist[i] = " ".join(breaklist_2)
                line_prev = "=".join(breaklist)
        lines.append(line_prev)

with open(file_name, 'w+') as fw:
    # print("here")
    # print(f"lines are\n : {lines}")
    if not exists:
        fw.write(load_static)
    for line in lines:
        if line.endswith('\n'):
            fw.write(line)
        else:
            fw.write(f"{line}\n")