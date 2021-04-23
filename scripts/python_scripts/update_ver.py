open_file = open('constants/version.txt', 'r+')
prev_ver = str(open_file.read())
prev_ver_split = prev_ver.split('.')
new_ver = f'{prev_ver_split[0]}.{prev_ver_split[1]}.{str(int(prev_ver_split[2]) + 1)}'
open_file.seek(0)
open_file.truncate(0)
open_file.write(new_ver)
open_file.close()