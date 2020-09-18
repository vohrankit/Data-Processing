# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 18:36:31 2020

@author: Ankit
"""
#Problem : Given are 2 datasets. 
#	   Dataset1 has 2 columns (unique_id1, text1)
#	   Dataset2 has 4 columns (unique_id2, text2, count)
#	   Match the values of text1 column with text2 column and from the result where match is >=90% extract the maximum value of count from most matching text2.
#	   The final output should have same coulmns as in Dataset1 with additional column of count (like unique_id1, text1, count) in same order.

#Solution : Assuming data is quite large. The idea is to firstly extract the maximum value of count where text1 exactly matches with text2.
#           Then for remaining instances in dataset1, use SequenceMatcher from difflib library and identify the maximum count value corresponding to most matching text2.

#====================================================================================================================================================================================

import pandas as pd										#import the pandas library
data1 = pd.read_excel('dataset1')								#read the dataset1 into data1
data2 = pd.read_excel('dataset2')								#read the dataset2 into data2

df1=data1.copy()										#working copy of data1
df2=data2.copy()										#working copy of data2

df2=df2.rename(columns={df2.columns[1]:df1.columns[1]})						#in case column#2 has different name in both datasets then rename one of them.
df1.iloc[:,1] = df1.iloc[:,1].str.lower()							#convert values of column#2 of df1 into lower case to avoid case-sensitivity of text data.
df2.iloc[:,1] = df2.iloc[:,1].str.lower()							#convert values of column#2 of df2 into lower case to avoid case-sensitivity of text data.

#====================================================================================================================================================================================

#Step1: Extract the maximum value of count where text1 exactly matches with text2

df2.sort_values(by='count',ascending=False, inplace =True)					#sorting df2 in descending order based on count column values.
df2=df2.drop_counts(df2.columns[1],keep='first')						#removing rows with duplicate text2 values from df2 except 1st instance (max count).
df = df1.merge(df2 , how='left' , on = df1.columns[1])						#merging df2 in df1 based on text values.
data1['count'] = df.iloc[:,3]									#create count column in data1 and pipe-in the values from count column of df, to keep letter case same in dataset1.

#====================================================================================================================================================================================

#Step2: For remaining instances in dataset1 for which text1 did not have exact match in text2 in dataset2.
#       Use SequenceMatcher from difflib library and identify the maximum count value corresponding to most matching text2.

from difflib import SequenceMatcher								#import SequenceMatcher from difflib library.

def similar(a, b):										#create function which gives the percentage of match between 2 texts.
    return SequenceMatcher(None, a, b).ratio()

d = data1[data1.count.isnull()]									#creating a new dataframe including those instances in dataset1 for which text1 did not have exact match in text2 in dataset2.
d['text1_lowercase'] = d['text1'].str.lower()							#creating a column to store text1 in lowercase.
df2['Percent_match'] = ""									#create a column to store the percentage value of match between text1 and each text2.

for i in range(len(d)):										#iterate over the entire dataframe 'd'.
    df2.iloc[:,4] = df2.iloc[:,1].apply(similar , b = d.iloc[i,4])				#for text1 value in 'd' calculate the percentage match value with every text2 value and store in 'Percent_Match' column.
    df2.sort_values(by=['Percent_match','count'],ascending=False, inplace =True)		#sorting df2 in descending order based on 'Percent_match' and 'count' column values.
    if df2.iloc[0,4] >= 0.9:									#if the 1st text2 value in sorted dataframe is >=90% match.
        d.iloc[i,2] = df2.iloc[0,2]								#then extract the corresponding count value.

data3 = data1.merge(d , how = 'left' , on = [df.columns[0],df.columns[1]])			#process the final data by merging 'd' and 'data1' based on unique_id1 and text1.
data3[data3.columns[2]] = data3[data3.columns[2]].fillna(data3[data3.columns[3]])		#merging create new columns excluding on which the merging is done. So, impute the count value into missing places in count column of data1.
data3 = data3.drop(data3.iloc[:,3],axis=1)							#drop extra columns resulting from merging except (unique_id1, text1, count).
data3.to_excel('Output.xlsx')									#Export the output file.