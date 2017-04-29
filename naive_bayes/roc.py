from my_classifier.bayes import *
import sys
import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

def plot(real, predicted, name):
    fpr, tpr, _  = roc_curve(real,predicted)
    area = auc(fpr, tpr)
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.2f)' % area)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([-0.05, 1.05])
    plt.ylim([-0.05, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic ' + name)
    plt.legend(loc="lower right")
    plt.savefig(name+".png")
    plt.close()

def diff(prob_good, prob_bad):
    ret = 0.5
    ret += (float(prob_bad)-float(prob_good))/2
    return ret

if len(sys.argv) != 4:
    print("Arguments are")
    print("1 Name of folder1")
    print("2 Name of folder2")
    print("3 name of db")
    exit(1)

c = MyClassifier(sys.argv[3])
f = Fisher(c)
b = NaiveBayes(c)

dir1_name = sys.argv[1]

if not os.path.exists(dir1_name):
        print("Dir1 doesn't exists")
        exit(1)
dir2_name = sys.argv[2]

if not os.path.exists(dir1_name):
        print("Dir2 doesn't exists")
        exit(1)

direct1 = os.listdir(dir1_name)
direct2 = os.listdir(dir2_name)

for n in range(0,len(direct1)):
        direct1[n] = os.path.join(dir1_name, direct1[n])
for n in range(0,len(direct2)):
        direct2[n] = os.path.join(dir2_name, direct2[n])

real=list()
probf=list()
probfg=list()
probb=list()

for fname in direct1:
    fh = open(fname, "rb")
    content = fh.read().decode('utf-8', errors='ignore')

    bad = (b.document_probability(content, "bad"))
    good = (b.document_probability(content, "good"))
    probb.append(diff(good, bad))

    bad = (f.fisher_probability(content, "bad"))
    good = (f.fisher_probability(content, "good"))
    probf.append(diff(good, bad))    

    real.append(1)

for fname in direct2:
    fh = open(fname, "rb")
    content = fh.read().decode('utf-8', errors='ignore')
    bad = (b.document_probability(content, "bad"))
    good = (b.document_probability(content, "good"))
    probb.append(diff(good, bad))
    # probb.append(b.document_probability(content, "bad"))
    # probf.append(f.fisher_probability(content, "bad"))
    bad = (f.fisher_probability(content, "bad"))
    good = (f.fisher_probability(content, "good"))
    probf.append(diff(good, bad))    
    real.append(0)


plot(real, probb, "bayes")
plot(real, probf, "fisher")
