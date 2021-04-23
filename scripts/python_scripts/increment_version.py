v = open(
    f"/home/runner/work/EclipseDiscordBot/EclipseDiscordBot/constants/version.txt",
    'r')
vss = v.read()
print(v.read())
vs = vss.split('.')
newstring = f'{vs[0]}.{vs[1]}.{int(vs[2]) + 1}'
v.close()
vn = open(
    f"/home/runner/work/EclipseDiscordBot/EclipseDiscordBot/constants/version.txt",
    'w')
print(newstring)
vn.truncate(0)
vn.write(newstring)
vn.close()
v = open(
    f"/home/runner/work/EclipseDiscordBot/EclipseDiscordBot/constants/version.txt",
    'r')
print(v.read())
v.close()
