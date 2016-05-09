# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 12:39:18 2016

@author: ryankeenan
"""

import pickle
import numpy as np
import pandas as pd
from scipy import optimize

#first step is to read the data in from MySQL database
import MySQLdb as mdb
conn = mdb.Connection(user="root", passwd="rosebud", db="sellwand")
c=conn.cursor()
c.execute("""SELECT c.company_name, op.ordered_qty, o.created_at, 
                  p.product_type, p.unit, p.title, 
                  plp.product_variant_price  
          FROM orders_products op 
          JOIN orders o ON op.order_sid = o.sid 
          JOIN products_variants pv ON op.variant_sid = pv.sid 
          JOIN products p ON pv.product_sid = p.sid 
          JOIN customers c ON o.customer_sid = c.sid
          JOIN customers_price_lists cpl ON cpl.customer_sid = c.sid
          JOIN price_lists pl ON cpl.price_list_sid = pl.sid
          JOIN price_lists_prices plp ON plp.price_list_sid = pl.sid 
          AND plp.product_variant_sid = pv.sid;""")
            
data = c.fetchall()

#now we build a pandas dataframe from the data
cols = ["company_name", "ordered_qty", "created_at", 
                  "product_type", "unit", "product_name",
                  "product_price"]
data = pd.DataFrame(list(data), columns=cols)
pickle.dump(data,open('data.p','wb'),protocol=2)

data = pickle.load(open('data.p','rb'))
companies = list(set(data["company_name"]))
products = list(set(data["product_name"]))
num_companies = len(companies)
num_products = len(products)

#Next we construct the feature matrix based on purchase history
Y = np.zeros((num_products, num_companies))

for idx, row in enumerate(data.itertuples()):

    company = row[1]
    quantity = row[2]
    product = row[6]
    company_idx = companies.index(company)
    product_idx = products.index(product)    
    Y[product_idx, company_idx] += 1 #previously += quantity

#now make a dictionary containing the data we need, and save it
dataDict = {}
dataDict["companies"] = companies
dataDict["products"] = products
dataDict["Y"] = Y
pickle.dump(dataDict,open('dataDict.p','wb'),protocol=2)


#define the collaborative filtering cost function as per Ng course
def cofiCostFunc(params, Y, R, num_users, num_movies, num_features, lamb):
    
    X = params[0:num_movies*num_features].reshape(num_movies, num_features)
    Theta = params[num_movies*num_features:].reshape(num_users, num_features)


    J = np.sum((((X.dot(Theta.T) - Y)*R)**2))/2 \
            + (np.sum(Theta**2) + np.sum(X**2))*lamb/2

    return J

#define the cost function gradient as per Ng course
def cofiCostGrad(params, Y, R, num_users, num_movies, num_features, lamb):
    
    X = params[0:num_movies*num_features].reshape(num_movies, num_features)
    Theta = params[num_movies*num_features:].reshape(num_users, num_features)

    X_grad = ((X.dot(Theta.T) - Y)*R).dot(Theta) + lamb*X
    Theta_grad = ((X.dot(Theta.T) - Y)*R).T.dot(X) + lamb*Theta
    grad = np.append(np.ravel(X_grad),np.ravel(Theta_grad))

    return grad
    
#a function to check if the cost function is calculated correctly
def checkCostFunction(lamb):
    
    X_t = np.random.random((4,3))
    Theta_t = np.random.random((5,3))
    
    Y = X_t.dot(Theta_t.T)
    Y[np.random.random((np.shape(Y))) > 0.5] = 0
    R = np.zeros(np.shape(Y))
    R[Y > 0] = 1

    X = np.random.random(np.shape(X_t))
    Theta = np.random.random(np.shape(Theta_t))
    num_users = np.shape(Y)[1]
    num_movies = np.shape(Y)[0]
    num_features = np.shape(Theta_t)[1]
    params = np.append(np.ravel(X),np.ravel(Theta))
    numgrad = computeNumericalGradient(params, Y, R, 
                    num_users, num_movies, num_features, lamb)
    grad = cofiCostGrad(params, Y, R, 
                    num_users, num_movies, num_features, lamb)

    for idx, elem in enumerate(numgrad):
        print(numgrad[idx], grad[idx])
    
#gradient checking
def computeNumericalGradient(params, Y, R, num_users, num_movies, 
                           num_features, lamb):
    
    numgrad = np.zeros(len(params))
    e = 1e-4
    
    for idx, elem in enumerate(params):
    
        test_up = params.tolist()
        test_down = params.tolist()
#        print(test_up[idx], test_down[idx])
        test_up[idx] += e

        test_down[idx] -= e
#        print(test_up[idx], test_down[idx])
        test_up = np.asarray(test_up)
        test_down = np.asarray(test_down)
        Jup = cofiCostFunc(test_up, Y, R, num_users, num_movies, 
                           num_features, lamb)
        Jdown = cofiCostFunc(test_down, Y, R, num_users, num_movies, 
                           num_features, lamb)
        numgrad[idx] = (Jup - Jdown)/(2*e)
        
    return numgrad

#normalize the ratings as per Ng course.
def normalizeRatings(Y, R):
    
    m, n = np.shape(Y)
    Ymean = np.zeros(m)
    Ynorm = np.zeros(np.shape(Y))
    
    for idx in range(0,m-1):
        
        nonzero = R[idx,:] == 1
        Ymean[idx] = np.mean(Y[idx, nonzero])
        Ynorm[idx, nonzero] = Y[idx, nonzero] - Ymean[idx]
    
    return Ynorm, Ymean
    
    
dataDict = pickle.load(open('dataDict.p','rb'))
companies = dataDict["companies"]
products = dataDict["products"]
Y = dataDict["Y"]

num_companies = len(companies)
num_products = len(products)
R = np.clip(Y, 0, 1)

#iterating through different choices of max_score (the score
#assigned by purchase history order count, number of features,
#and regularization to find the best optimization.)
max_score = [3, 5, 10]
n_features = [10, 50, 100]
regularization = [0.1, 1, 10]

for mscore in max_score:

    for num_features in n_features:

        for lamb in regularization:
            
            suffix = '_'+str(mscore)+'_'+str(num_features)+'_'+str(lamb)

            Y = np.clip(Y, 0, mscore) #rating system will be 1 to 5 based on n_orders
            X = np.random.randn(num_products, num_features)
            Theta = np.random.randn(num_companies, num_features)
            
            X = X[0:num_products, 0:num_features]
            Theta = Theta[0:num_companies, 0:num_features]
            Y = Y[0:num_products, 0:num_companies]
            R = R[0:num_products, 0:num_companies]
            
            params = np.append(np.ravel(X),np.ravel(Theta))
            
            #uncomment the following lines to do gradient checking
            #J = cofiCostFunc(params, Y, R, num_companies, num_products, num_features, lamb)
            #print('J = ',J)
            #checkCostFunction(lamb)
            
            args = (Y, R, num_companies, num_products, num_features, lamb)
            
            print("Doin' some learnin' now!")
            print('max_score =',mscore,'num_features =',num_features,'lambda =',lamb)
            learned = optimize.fmin_cg(cofiCostFunc, params, fprime=cofiCostGrad, args=args,
                                       maxiter=500)
            
            X = learned[0:num_products*num_features].reshape(num_products, num_features)
            Theta = learned[num_products*num_features:].reshape(num_companies, num_features)
            
            pred = X.dot(Theta.T)
            
            
            dataDict["X"] = X
            dataDict["Theta"] = Theta
            dataDict["pred"] = pred
            dataDict["max_score"] = mscore
            dataDict["num_features"] = num_features
            dataDict["lambda"] = lamb
            
            pickle.dump(dataDict,open('dataDict'+suffix+'.p','wb'),protocol=2)
            #


        
    