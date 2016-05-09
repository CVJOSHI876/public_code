This code is an example of a collaborative filtering (matrix factorization) implementation in Python.

I translated the heart of the code from the Matlab/Octave implementation presented in Andrew Ng's course "Machine Learning" as presented on Coursera.  In this case, we read in the initial data from a SQL database containing purchase histories among retailers past purchases of products from a wholesaler.  

This code won't work without the database to query from (can't provide that here because its proprietary) but it should serve as a nice template for anyone wanting to build a recommender system in Python using collaborative filtering.  
