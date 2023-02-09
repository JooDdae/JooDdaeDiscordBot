async def get_problems(query, number):
  import http, json

  if "sort" not in query :
    query += "&sort=random"

  conn = http.client.HTTPSConnection("solved.ac")
  conn.request("GET", "/api/v3/search/problem?query=" + query, headers={ 'Content-Type': "application/json" })
  
  res = conn.getresponse()
  data = res.read()

  if res.status != 200:
    return [-1]
  
  problems = json.loads(data.decode("utf-8"))
  if problems['count'] == 0:
    return [-2]
    
  return problems['items'][:number]