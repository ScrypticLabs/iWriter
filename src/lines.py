import glob
# 4,451 lines of code

countLines = 0
countWords = 0
files = glob.glob("*.py")
files.remove("lines.py")

for x in range(len(files)):
	fileLine = open(files[x]).read().split("\n")
	countLines += len(fileLine)
	for word in fileLine:
		word = word.split()
		countWords += len(word)


print("Lines: %d" % countLines)
print("Words: %d" % countWords)
