v = open(
    f"/home/runner/work/EclipseDiscordBot/EclipseDiscordBot/constants/version.txt",
    'r')
vss = v.read()
print(v.read())
vs = vss.split('.')
newstring = f'{vs[0]}.{vs[1]}.{int(vs[2]) + 1}'
print(newstring)
v.seek(0)
v.write(newstring)
v.truncate()
v.close()