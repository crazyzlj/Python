import os
from shutil import rmtree
suffix = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.tex', '.txt']
deldirs = []
for root, dirs, files in os.walk(r"D:\mysync\storage"):
    for i in files:
        for suf in suffix:
            if i.find(suf) < 0:
                continue
            else:
                break
        else:  # Can not find any useful documents.
             deldirs.append(root)
deldirs = list(set(deldirs))
for deldir in deldirs:
    print "deleting %s..." % deldir
    rmtree(deldir)
