
from my_classifier.bayes import MyClassifier


fl = open("input.txt", "r")
compl = str()
for line in fl:
	compl += line

aa = MyClassifier()

aa.train(compl, "spam")


print(aa._get_words(compl))
