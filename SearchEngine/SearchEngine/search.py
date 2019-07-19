#!/usr/bin/python3

import psycopg2
import re
import string
import sys

_PUNCTUATION = frozenset(string.punctuation)

def _remove_punc(token):
    """Removes punctuation from start/end of token."""
    i = 0
    j = len(token) - 1
    idone = False
    jdone = False
    while i <= j and not (idone and jdone):
        if token[i] in _PUNCTUATION and not idone:
            i += 1
        else:
            idone = True
        if token[j] in _PUNCTUATION and not jdone:
            j -= 1
        else:
            jdone = True
    return "" if i > j else token[i:(j+1)]

def _get_tokens(query):
    rewritten_query = []
    tokens = re.split('[ \n\r]+', query)
    for token in tokens:
        cleaned_token = _remove_punc(token)
        if cleaned_token:
            if "'" in cleaned_token:
                cleaned_token = cleaned_token.replace("'", "''")
            rewritten_query.append(cleaned_token)
    return rewritten_query



def search(query, query_type):
    
    rewritten_query = _get_tokens(query)
    name = query.replace(' ','')
    """TODO
    Your code will go here. Refer to the specification for projects 1A and 1B.
    But your code should do the following:
    1. Connect to the Postgres database.
    2. Graciously handle any errors that may occur (look into try/except/finally).
    3. Close any database connections when you're done.
    4. Write queries so that they are not vulnerable to SQL injections.
    5. The parameters passed to the search function may need to be changed for 1B. 
    """
    rows = []
    a = len(rewritten_query)
    try:
        connection = psycopg2.connect(user="cs143",
                                  password="cs143",
                                  host="localhost",
                                  dbname="searchengine")
        cursor=connection.cursor()
        
        
        if query_type=='or':
            sql='''CREATE MATERIALIZED VIEW IF NOT EXISTS or'''+name+''' AS
                   SELECT L.song_name, M.artist_name, L.page_link  
                   FROM proj1.song L 
                   JOIN proj1.artist M
                   ON L.artist_id = M.artist_id
                   JOIN
                   proj1.tfidf R
                   ON L.song_id = R.song_id
                   WHERE R.token = ANY(%s)
                   GROUP BY L.song_name, L.page_link, M.artist_name
                   ORDER BY SUM(R.score) DESC;
                   SELECT * FROM or'''+name+''';
                   '''
            cursor.execute(sql, ( rewritten_query,))
            connection.commit()
            rows = cursor.fetchall()
        
        if query_type == 'and':
            
            sql='''CREATE MATERIALIZED VIEW IF NOT EXISTS and'''+name+''' AS
                   SELECT L.song_name, M.artist_name, L.page_link    
                   FROM proj1.song L
                   JOIN
                   proj1.artist M
                   ON L.artist_id = M.artist_id
                   JOIN
                   proj1.tfidf R
                   ON L.song_id = R.song_id
                   WHERE R.token = ANY(%s)
                   GROUP BY L.song_id, L.song_name, L.page_link, M.artist_name
                   HAVING COUNT(R.token) = (%s)
                   ORDER BY SUM(R.score) DESC;
                   SELECT * FROM and'''+name+''';
                   '''
            
            cursor.execute(sql, (rewritten_query,a))
            connection.commit()
            rows = cursor.fetchall()    
                                    
    except (Exception,psycopg2.DatabaseError) as error:
        print ("Error while creating PostgreSQL table", error)

    finally:
        if connection is not None:
            connection.close()                                
    return rows[:min(20, len(rows))]

def search_view(query, query_type, page):
  name = query.replace(' ','')
  
  try:
    connection = psycopg2.connect(user="cs143",
                              password="cs143",
                              host="localhost",
                              dbname="searchengine")
    cursor=connection.cursor()
    
    if query_type=='or':
      view_name = 'or' + name
    else:
      view_name = 'and' + name

    offset = (int(page) - 1) * 20

    sql = 'SELECT * FROM ' + view_name + ' LIMIT 20 OFFSET ' + str(offset) + ';'
    
    cursor.execute(sql)
    connection.commit()
    rows = cursor.fetchall()    
                                    
  except (Exception,psycopg2.DatabaseError) as error:
        print ("Error while creating PostgreSQL table", error)

  finally:
      if connection is not None:
          connection.close()                   
  print(len(rows))
  return rows

if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

