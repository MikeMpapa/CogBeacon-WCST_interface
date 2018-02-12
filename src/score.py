import numpy as np

levels = 5
seconds = 7
trials = 6 #8-2 --> first two dont count when the rule changes


x = range(levels) # possible scores in a trial
y = [float(i) for i in x]

y = np.array(y)
y=y+1

scores = np.zeros((levels,seconds+1))

print y

scores[:,0] = np.array(y)


for i in range(scores.shape[0]):
	for j in range(scores.shape[1]):
		if j == scores.shape[1]-1:
			continue
		scores[i,j] =  float(scores[i,0])/float(j+1) 



print scores*6
