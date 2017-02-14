import os

dir = "/opt/odoo"

with open("files.txt", "r") as f:
    data = f.readlines()

for i in data:
    os.system('rm -Rf %s' % i)

#print lista

#for f in listado:
#    os.system("rm -Rf %s" % f)
