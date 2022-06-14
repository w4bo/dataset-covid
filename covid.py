#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import sys
from sqlalchemy import create_engine
import os.path
import cx_Oracle
import sqlalchemy as sa
from dotenv import load_dotenv

load_dotenv()
# print(os.environ)

connstring = "oracle://{}:{}@{}:{}/{}".format(os.getenv('ORACLE_USER'), os.getenv('ORACLE_PWD'), os.getenv('ORACLE_IP'), os.getenv('ORACLE_PORT'), os.getenv('ORACLE_DB'))
oracle_db = sa.create_engine(connstring)
cx_Oracle.init_oracle_client(lib_dir=os.getenv('ORACLE_PATH'))
engine = oracle_db.connect()
df = pd.read_csv("datasets/dataset_weekly-20220614.csv", delimiter=",") #, nrows=1000
df = df[["country", "continent", "country_code", "population", "indicator", "weekly_count", "year_week"]]
df


# Drop duplicates / null

# In[2]:


df = df[~df["country"].str.contains("(total)")]
df = df[["country", "continent", "population", "indicator", "weekly_count", "year_week"]].drop_duplicates().dropna()
df


# Do some manual value mapping

# In[3]:


df["year"] = df["year_week"].apply(lambda x: x.split("-")[0])
def pick_month(x):
    return x 

def replace_month(x):
    month = int(x.split("-")[1])-1
    year = x.split("-")[0]
    if month < 5:
        month='01'
        # month='JAN'
    elif month < 9:
        month='02'
        # month='FEB'
    elif month < 14:
        month='03'
        # month='MAR'
    elif month < 18:
        month='04'
        # month='APR'
    elif month < 23:
        month='05'
        # month='MAY'
    elif month < 27:
        month='06'
        # month='JUN'
    elif month < 32:
        month='07'
        # month='JUL'
    elif month < 37:
        month='08'
        # month='AUG'
    elif month < 41:
        month='09'
        # month='SEP'
    elif month < 45:
        month='10'
        # month='OCT'
    elif month < 49:
        month='11'
        # month='NOV'
    elif month < 53:
        month='12'
        # month='DEC'
    else:
        print(x)
        sys.exit(1)
    return year + "-" + month

df["month"] = df["year_week"].apply(lambda x: replace_month(pick_month(x)))
df["year_week"] = df.apply(lambda x: x["month"] + "-" + x["year_week"].split("-")[1], axis=1)
df = df.rename(columns={'year_week': 'week'})

df


# Flatten indicator to deaths and cases

# In[4]:


def df_to_row(x):
    cases = x[x["indicator"] == "cases"]["weekly_count"].tolist()[0]
    deaths = x[x["indicator"] == "deaths"]["weekly_count"].tolist()[0]
    df = pd.DataFrame(columns = ["deaths", "cases"])
    df.loc[0] = [deaths, cases]
    return df
    
df = df.groupby(["country", "continent", "population", "week", "year", "month"]).apply(lambda x: df_to_row(x)).reset_index()
df


# In[5]:


df.drop(labels=["level_6"], inplace=True, axis=1)
ft = df[["country", "deaths", "cases", "week"]].drop_duplicates()
ft.to_csv("generated/ft.csv", index=False)
dt1 = df[["country", "continent", "population"]].drop_duplicates()
dt1.to_csv("generated/dt_space.csv", index=False)
dt2 = df[["year", "month", "week"]].drop_duplicates()
dt2.to_csv("generated/dt_time.csv", index=False)


# Write the dataframe to oracle (if needed)
# 
# Note that this writes strings as Oracle CLOB, which are a mess to join. An ugly workaround is
# 
# ```
# create table foo (country varchar2(255), continent varchar2(255), population varchar2(255));
# insert into foo select country, continent, population from dt_space;
# drop table dt_space;
# rename foo to dt_space;
# 
# create table foo (week varchar2(255), year varchar2(255), month varchar2(255));
# insert into foo select week, year, month from dt_time;
# drop table dt_time;
# rename foo to dt_time;
# 
# create table foo (week varchar2(255), country varchar2(255), deaths int, cases int);
# insert into foo select week, country, deaths, cases from ft;
# drop table ft;
# rename foo to ft;
# 
# alter table ft add primary key(week, country);
# alter table dt_space add primary key(country);
# alter table dt_time add primary key(week);
# alter table ft ADD CONSTRAINT fk_time foreign key (week) references dt_time(week);
# alter table ft ADD CONSTRAINT fk_space foreign key (country) references dt_space(country);
# 
# select * from dt_time where month = '2020-AUG';
# select count(*) from (select* from ft, dt_time where ft.week = dt_time.week);
# ALTER TABLE ft DROP CONSTRAINT fk_time;
# alter table ft ADD CONSTRAINT fk_time foreign key (week) references dt_time(week);
# UPDATE ft t  SET week = REPLACE(t.week, 'AGO', 'AUG');
# UPDATE dt_time t  SET week = REPLACE(t.week, 'AGO', 'AUG');
# select * from "MEMBER" where member_name like '%AUG%';
# UPDATE "MEMBER" t  SET member_name = REPLACE(t.member_name, 'AGO', 'AUG');
# ```

# In[6]:


g = dt1.groupby("country").count().reset_index()
g[g["continent"] > 1]


# In[7]:


statements = [
    "drop table ft",
    "drop table dt_space",
    "drop table dt_time",
]

for statement in statements:
    try:
        print(statement)
        engine.execute(statement)
    except:
        pass


# In[8]:


# df.to_sql('covid_raw_data', engine, if_exists='replace', index=False)
ft.to_sql('ft', engine,  index=False, chunksize=10000) # if_exists='replace', # , method='multi'
print("Done ft")
dt1.to_sql('dt_space', engine, index=False, chunksize=10000) # if_exists='replace', # , method='multi'
print("Done dt_space")
dt2.to_sql('dt_time', engine, index=False, chunksize=10000) # if_exists='replace', # , method='multi'
print("Done dt_time")


# In[9]:


statements = [
    "create table foo (country varchar2(255), continent varchar2(255), population varchar2(255))",
    "insert into foo select country, continent, population from dt_space",
    "drop table dt_space",
    "rename foo to dt_space",
    "create table foo (week varchar2(255), year varchar2(255), month varchar2(255))",
    "insert into foo select week, year, month from dt_time",
    "drop table dt_time",
    "rename foo to dt_time",
    "create table foo (week varchar2(255), country varchar2(255), deaths int, cases int)",
    "insert into foo select week, country, deaths, cases from ft",
    "drop table ft",
    "rename foo to ft",
    "alter table ft add primary key(week, country)",
    "alter table dt_space add primary key(country)",
    "alter table dt_time add primary key(week)",
    "alter table ft ADD CONSTRAINT fk_time foreign key (week) references dt_time(week)",
    "alter table ft ADD CONSTRAINT fk_space foreign key (country) references dt_space(country)",
    "select * from dt_time where month = '2020-AUG'",
    "select count(*) from (select* from ft, dt_time where ft.week = dt_time.week)",
    "ALTER TABLE ft DROP CONSTRAINT fk_time",
    "alter table ft ADD CONSTRAINT fk_time foreign key (week) references dt_time(week)"]

for statement in statements:
    print(statement)
    engine.execute(statement)

