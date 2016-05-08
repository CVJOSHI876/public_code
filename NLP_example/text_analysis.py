#==============================================================================
#NLP implementation to categorize customer complaint text

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from pprint import pprint
from time import time

from sklearn.linear_model import SGDClassifier

from sklearn.grid_search import GridSearchCV
from sklearn.pipeline import Pipeline

df = pd.read_csv('train.csv') # csv now a pandas DataFrame

#==============================================================================
# df.describe()
# Out[12]: 
#                        date                                   issue  \
# count                 51399                                   51399   
# unique                  345                                      90   
# top     2015-07-15 00:00:00  Incorrect information on credit report   
# freq                    282                                    6447   
# first   2015-03-19 00:00:00                                     NaN   
# last    2016-02-26 00:00:00                                     NaN   
# 
#                                                 complaint  state zip_code  
# count                                               51398  51078    51218  
# unique                                              50544     60      903  
# top     This company continues to report on my credit ...     CA    300XX  
# freq                                                   33   7712      774  
# first                                                 NaN    NaN      NaN  
# last                                                  NaN    NaN      NaN  
#==============================================================================

df.fillna('', inplace=True) #get rid of missing values
issues = list(df["issue"])
corpus = list(df["complaint"])
states = list(df["state"])
zipcodes = list(df["zip_code"])

categories = list(set(issues))
catCount = [issues.count(cat) for cat in categories]
goodCats = [cat for cat in categories if issues.count(cat) > 2] #ultimately we'll
#split the dataset into 3 parts, train, test, and cross validate, so at least 3
#valid entries per category are required.

newIssues = []
newCorpus = []

#stepping through and adding states and zipcodes to feature vector
for idx, issue in enumerate(issues):
    
    if issue in goodCats:
        newIssues.append(issue)
        newCorpus.append(corpus[idx]+' '+states[idx]+' '+zipcodes[idx])
print('Number of Categories: ', len(set(newIssues)))
print('Fraction retained: ', (len(newIssues)/len(issues)))
###############################################################################
## a pipeline combining a vectorizer, normalizer, and a simple classifier
pipe = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('tfidfTrans', TfidfTransformer()),
    ('sgdclf', SGDClassifier(loss='modified_huber')),
])
#pipe = Pipeline([
#    ('vectorizer', CountVectorizer()),
#    ('tfidfTrans', TfidfTransformer()),
#    ('tree', DecisionTreeClassifier()),
#])

#Initial grid of parameters to search...
params = {
    'vectorizer__max_df': (0.5, 1.0),
    'vectorizer__ngram_range': ((1, 1), (1, 2)),  # unigrams or bigrams
    'tfidfTrans__use_idf': (True, False),
    'sgdclf__alpha': (0.0001, 0.00001, 0.000001),
}

#parameters yielding the best performance for SGDC...
#params = {
    #    'vectorizer__max_df': [1.0],
    #'vectorizer__max_features': [None],
    #'vectorizer__ngram_range': [(1, 2)],  # unigrams or bigrams
    #'tfidfTrans__use_idf': [True],
    #'tfidfTrans__norm': ['l2'],
    #'sgdclf__alpha': [0.00001],
    #'sgdclf__penalty': ['l2'],
    #'sgdclf__n_iter': [10],

    #}


if __name__ == "__main__":

    grid_s = GridSearchCV(pipe, params, n_jobs=-1, verbose=1, refit=True)

    print("searching over parameters...")
    print("The pipeline steps are:", [name for name, _ in pipe.steps])
    print("The parameters are:")
    pprint(params)
    t0 = time()
    grid_s.fit(newCorpus, newIssues)
    print("done in %0.3fs" % (time() - t0))
    print()

    print("The Best score is: %0.3f" % grid_s.best_score_)
    print("Best parameters set:")
    best_p = grid_s.best_estimator_.get_params()
    for param_name in sorted(params.keys()):
        print("\t%s: %r" % (param_name, best_p[param_name]))

##results of running on the full sample printed below
##==============================================================================
#Number of Categories: 87
#Fraction retained:  0.9998248993171074
#searching over parameters...
#The pipeline steps are: ['vectorizer', 'tfidfTrans', 'sgdclf']
#The parameters are:
#{'sgdclf__alpha': (0.0001, 1e-05, 1e-06),
# 'tfidfTrans__use_idf': (True, False),
# 'vectorizer__max_df': (0.5, 1.0),
# 'vectorizer__ngram_range': ((1, 1), (1, 2))}
#Fitting 3 folds for each of 24 candidates, totalling 72 fits
#[Parallel(n_jobs=-1)]: Done  34 tasks      | elapsed:  3.9min
#[Parallel(n_jobs=-1)]: Done  72 out of  72 | elapsed:  8.4min finished
#done in 555.172s
#
#The Best score is: 0.566
#Best parameters set:
#	sgdclf__alpha: 0.0001
#	tfidfTrans__use_idf: True
#	vectorizer__max_df: 0.5
#	vectorizer__ngram_range: (1, 2)
##==============================================================================


##results of running on only cagtegories with 1000+ complaints printed below
##==============================================================================
#Number of Categories:  15
#Fraction retained:  0.7162201599252904
#searching over parameters...
#The pipeline steps are: ['vectorizer', 'tfidfTrans', 'sgdclf']
#The parameters are:
#{'sgdclf__alpha': (0.0001, 1e-05, 1e-06),
# 'tfidfTrans__use_idf': (True, False),
# 'vectorizer__max_df': (0.5, 1.0),
# 'vectorizer__ngram_range': ((1, 1), (1, 2))}
#Fitting 3 folds for each of 24 candidates, totalling 72 fits
#[Parallel(n_jobs=-1)]: Done  34 tasks      | elapsed:  1.9min
#[Parallel(n_jobs=-1)]: Done  72 out of  72 | elapsed:  4.0min finished
#done in 266.727s
#
#The Best score is: 0.693
#Best parameters set:
#        sgdclf__alpha: 0.0001
#        tfidfTrans__use_idf: True
#        vectorizer__max_df: 0.5
#        vectorizer__ngram_range: (1, 2)


#reading in and preparing the test data for prediction
df2 = pd.read_csv('test.csv')#, index_col=0) # workbook is now a pandas data frame
df2.fillna('', inplace=True)
test_issues = list(df2["issue"])
test_corpus = list(df2["complaint"])
test_states = list(df2["state"])
test_zipcodes = list(df2["zip_code"])

newTestCorpus = []
for idx, comp in enumerate(test_corpus):
    newTestCorpus.append(comp+' '+test_states[idx]+' '+test_zipcodes[idx])

#use the best trained classifier to predict probabilities for all labels
result = grid_s.predict_proba(newTestCorpus)

#create a new DataFrame containing results
output = pd.DataFrame(data=result,index=df2["id"], columns=goodCats)

#write the result to csv
output.to_csv('submit.csv')
