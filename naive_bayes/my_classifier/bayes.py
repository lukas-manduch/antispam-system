import re
import sqlite3

"""
Classifier class holds statistics about frequency of words in documents
and then uses some Classifier ( naive bayes or fisher alorithm ) to guess
probability of given text beeing in concrete category

Tables:
CREATE TABLE IF NOT EXISTS
feature_counts (
feature_id INTEGER PRIMARY KEY,
word text,
category_id INTEGER NOT NULL,
count INTEGER NOT NULL DEFAULT(0))

CREATE TABLE IF NOT EXISTS
category_counts (
category_id INTEGER PRIMARY KEY,
name text NOT NULL,
count INTEGER NOT NULL DEFAULT(0))

"""
class MyClassifier:
        def __init__(self, db_name: str):
                self.future_count = {}
                self.classification_used = {}
                self.db_connection = sqlite3.connect(db_name)
                self.db_cursor = self.db_connection.cursor()
                self.db_cursor.execute("CREATE TABLE IF NOT EXISTS"
                                       " feature_counts ("
                                       "feature_id INTEGER PRIMARY KEY,"
                                       "word text,"
                                       "category_id INTEGER NOT NULL,"
                                       "count INTEGER NOT NULL DEFAULT(0))")
                self.db_cursor.execute("CREATE TABLE IF NOT EXISTS "
                                       "category_counts ("
                                       "category_id INTEGER PRIMARY KEY,"
                                       "name text NOT NULL UNIQUE, "
                                       "count INTEGER NOT NULL DEFAULT(0))")


        def __del__(self):
                self.db_connection.commit()


        def increment_feature(self, feature, category):
                cat = self._get_category(category)
                cat_id = int()
                if len(cat) == 0:
                        cat_id = self._create_category(category, 0)
                else:
                        cat_id = cat[0]
                count = self.get_feature_count(feature, category)
                # if count is 0 then entry doesn't exist
                if count == 0:
                        self.db_cursor.execute("INSERT INTO feature_counts "
                                               "(word, category_id, count) "
                                               "VALUES "
                                               "(?, ?, ?) ",
                                               (feature, cat_id, count + 1))
                else:
                        self.db_cursor.execute("UPDATE feature_counts "
                                               "SET count=? WHERE "
                                               "category_id=? AND word=? ",
                                               (count + 1, cat_id, feature))

        def increment_category(self, category):
                count = self.get_category_count(category) + 1
                self.db_cursor.execute("UPDATE category_counts SET "
                                       "count=? WHERE name=? ",
                                               (count, category))


        def get_feature_count(self, feauture, category) -> float:
                self.db_cursor.execute(
                        "SELECT category_id FROM category_counts WHERE"
                        " name=?", (category,))
                id = self.db_cursor.fetchone()
                if id == None:
                        return 0
                self.db_cursor.execute("SELECT count from feature_counts "
                                       "WHERE category_id=? LIMIT 1", (float(
                        id[0]), ))
                count = self.db_cursor.fetchone()
                if count == None:
                        return 0
                return float(count[0])


        def get_category_count(self, category) -> float:
                self.db_cursor.execute(
                        "SELECT count FROM category_counts WHERE"
                        " name=?", (category,))
                id = self.db_cursor.fetchone()
                if id == None:
                        self._create_category(category, 0)
                        return 0
                return float(id[0])


        def total_count(self):
                res = self.db_cursor.execute("SELECT sum(count) FROM "
                                        "category_counts").fetchone()
                if res == None:
                        return 0
                return float(res[0])


        def categories(self):
                cats = self.db_cursor.execute("SELECT name from "
                                              "category_counts")
                return [cat[0] for cat in cats]


        def _get_words(self, content: str):
                splitter = re.compile('\\W*')
                words = [s.lower() for s in splitter.split(content) if
                         len(s) > 2 and len(s) < 20]
                # Return the unique set of words only
                return dict([(w, 1) for w in words]) # Only unique words


        def train(self, content, category):
                cont = self._get_words(content)
                for a in cont:
                        self.increment_feature(a, category)
                self.increment_category(category)


        def _get_category(self, category: str) -> list:
                self.db_cursor.execute(
                        "SELECT * FROM category_counts WHERE"
                        " name=?", (category,))
                row = self.db_cursor.fetchone()
                if row == None:
                        return list()
                return list(row)


        def _create_category(self, category, count) -> int:
                self.db_cursor.execute("INSERT INTO category_counts (name , "
                                       "count) VALUES (?, ?)", (category,
                                                                count ))
                return self.db_cursor.lastrowid


        def _feature_probability(self, feature, category) -> float:
                category_c = self.get_category_count(category)
                feature_c = self.get_feature_count(feature, category)
                if category_c == 0:
                        return 0
                return feature_c/category_c

        def feature_probability(self, feature, category) -> float:
                imaginary_count = 2
                weight = 0.5
                total_occurences = sum(
	                [self.get_feature_count(feature, cat)
	                 for cat in self.categories()])
                return ((imaginary_count * weight) +
                        (total_occurences *
                         self._feature_probability(feature, category))) / (
                total_occurences + imaginary_count)

class NaiveBayes:
        def __init__(self, classifier):
                self.classifier = classifier

        
        def _document_probability(self, document, category) -> float:
                feats = self.classifier._get_words(document)
                prob = 1
                for feat in feats:
                        prob *= self.classifier.feature_probability(feat, category)
                return prob
        
        def document_probability(self, document, category) -> float:
                doc_prob = self._document_probability(document, category)
                cat_prob = (self.classifier.get_category_count(category) /
                            self.classifier.total_count())
                return doc_prob*cat_prob
