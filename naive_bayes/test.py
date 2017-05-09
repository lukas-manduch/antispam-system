from my_classifier.bayes import *
import sys
import os
import matplotlib.pyplot as plt

def save_cfm(spam, not_spam, name):
    plt.imshow([[10,1],[8,21]], interpolation='nearest',
               cmap=plt.cm.Blues)
    plt.text(0,0, spam[0], fontsize=17, horizontalalignment='center')
    plt.text(1,0, spam[1], fontsize=17, horizontalalignment='center')
    plt.text(0,1, not_spam[0], fontsize=17, horizontalalignment='center')
    plt.text(1,1, not_spam[1], fontsize=17, horizontalalignment='center')    
    plt.yticks([0, 1], ["Spam", "Nie Spam"])
    plt.xticks([0, 1], ["Spam", "Nie Spam"])
    plt.ylabel('Skutočná hodnota')
    plt.xlabel('Predikovaná hodnota')
    #plt.show()
    name += ".png"
    plt.savefig(name)
    plt.close()


def train(db_name, category, file_list):
        
        c = MyClassifier(db_name)
        for fname in file_list:
                fh = open(fname, "rb")
                c.train(fh.read().decode('utf-8',
                                         errors='ignore'),
                        category)


def test(db_name, file_list):
        c = MyClassifier(db_name)
        f = Fisher(c)
        b = NaiveBayes(c)
        out = [0,0]
        for fname in file_list:
                fh = open(fname, "rb")
                content = fh.read().decode('utf-8', errors='ignore')
                fh.close()
                good = f.fisher_probability(content, "good")
                harm = f.fisher_probability(content, "bad")
                if harm > good*1.05:
                        out[0] += 1

                good = b.document_probability(content, "good")
                harm = b.document_probability(content, "bad")
                
                if harm > good*4.5:
                        out[1] += 1
        return out


if (len(sys.argv) != 4):
        print("Requires 3 args, name of bad folder, name of good"
        " folder and size of k fold")
        exit(1)


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

ifold = int(sys.argv[3])

for i in range(0, ifold):
        try:
                os.remove(str(i))
        except:
                pass

        fold = int(len(direct1)/ifold)
        
        print("training bad")
        print("0 - " + str(fold*i))
        train(str(i), "bad", direct1[0:fold*i])
        print(str(fold*(i+1)) + " - " + str(len(direct1)))
        train(str(i), "bad", direct1[fold*(i+1):])

        print("training good")
        fold = int(len(direct2)/ifold)
        print("0 - " + str(fold*i))
        train(str(i), "good", direct2[0:fold*i])
        print(str(fold*(i+1)) + " - " + str(len(direct2)))
        train(str(i), "good", direct2[fold*(i+1):])
        print("Training of " + str(i) + " finished\n")

        fisher_spam = list()
        fisher_not = list()
        bayes_spam = list()
        bayes_not = list()

        fold = int(len(direct1)/ifold)
        print("Testing on bad fold")
        outs = test(str(i), direct1[fold*i:fold*(i+1)])
        print("       BAD GOOD ("+ str(fold) + ")")
        print("Fisher " + str(outs[0]) + "   "+ str(fold-outs[0]))
        fisher_spam.append(outs[0])
        fisher_spam.append(fold- outs[0])

        print("Bayes " + str(outs[1]) + "   "+ str(fold-outs[1]))
        bayes_spam.append(outs[1])
        bayes_spam.append(fold - outs[1])


        fold = int(len(direct2)/ifold)
        print("Testing on good fold")
        outs = test(str(i), direct2[fold*i:fold*(i+1)])
        
        print("       BAD GOOD ("+ str(fold) + ")")
        
        print("Fisher " + str(outs[0]) + "   "+ str(fold-outs[0]))
        fisher_not.append(outs[0])
        fisher_not.append(fold - outs[0])
        
        print("Bayes " + str(outs[1]) + "   "+ str(fold-outs[1]))
        bayes_not.append(outs[1])
        bayes_not.append(fold - outs[1])
        
        save_cfm(fisher_spam, fisher_not, "fis" + str(i))
        save_cfm(bayes_spam, bayes_not, "bay" + str(i))        

"""
aa = MyClassifier("train.db")
fisher = Fisher(aa)
bayes = NaiveBayes(aa)

harms = list()
nonharms = list()

use_fisher = True

for file in direct:
        op_file = open(os.path.join(dir_name, file), "rb")
        print(file)
        compl = op_file.read().decode('utf-8', errors='ignore')
        if use_fisher:
                good = fisher.fisher_probability(compl, "good")
                harm = fisher.fisher_probability(compl, "harm")
        else:
                good = bayes.document_probability(compl, "good")
                harm = bayes.document_probability(compl, "harm")
        if harm > good:#*4:
                harms.append(file + " difference " + str(harm - good))
        else:
                nonharms.append(file + " difference " + str(good - harm))
        op_file.close()

print('----------------------')
print('----------------------')
print('----------------------')
print('----------------------')
print('----------------------')
print('----------------------')

print("Good " + str(len(nonharms)))
print("Bad " + str(len(harms)))
print("Print bad?")
if sys.stdin.readline().strip() == 'y':
        for f in harms:
                print(f)
"""
