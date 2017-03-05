import re


class MyClassifier:
	def __init__(self):
		self.future_count = {}
		self.classification_used = {}

	def increment_feauture(self, feauture, category):
		self.future_count.setdefault(feauture, {})
		self.future_count[feauture].setdefault(category, 0)
		self.future_count[feauture][category] += 1

	def increment_category(self, category):
		self.classification_used.setdefault(category, 0)
		self.classification_used[category] += 1

	def get_feauture_count(self, feauture, category) -> float:
		if feauture in self.future_count \
			and category in self.future_count[feauture]:
			return float(self.future_count[feauture][category])
		return float(0)

	def get_category_count(self, category) -> float:
		if category in self.classification_used:
			return self.classification_used[category]
		return float(0)

	def total_count(self):
		return sum(self.classification_used.values())

	def categories(self):
		return self.classification_used.keys()

fl = open("input.txt", "r")
compl = str()
for line in fl:
	compl += line


def get_words(content: str):
	splitter = re.compile('\\W*')
	words = [s.lower() for s in splitter.split(content) if
		 len(s) > 2 and len(s) < 20]
	# Return the unique set of words only
	return dict([(w, 1) for w in words])


print(get_words(compl))
