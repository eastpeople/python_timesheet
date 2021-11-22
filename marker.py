import pymysql
import sys, re, csv

argument = sys.argv
print(argument)

yearmonth = argument[1] + "-" + argument[2].rjust(2, '0')

# MySQL Connection 연결
conn = pymysql.connect(host='192.168.0.110', port=3306, user='clinomics', password='uiop7890', db='lims_v2', charset='utf8')
 
# Connection 으로부터 Cursor 생성
curs = conn.cursor()
 
# SQL문 실행
sql = "SELECT distinct JSON_KEYS(s.data) AS marker" \
        " FROM sample s" \
        " WHERE s.is_last_version = 1" \
        " AND (s.data is not null or s.data = '[]')" \
        " AND s.is_test = 0" \
        " AND s.created_date BETWEEN '" + yearmonth + "-01 00:00:00' and '" + yearmonth + "-31 23:59:59'"
curs.execute(sql)
# 데이타 Fetch
rows = curs.fetchall()

arrMarker = []

for idx, row in enumerate(rows):
    temp = re.sub('[\[\]]', '', row[0])
    arrMarker.extend(temp.split(","))


setMarker = set(arrMarker)
sorted(setMarker)

col_marker = ""
for sm in setMarker:
    temp = re.sub('[\"|\s]', '', sm)
    if temp:
        col_marker += " ,REPLACE(JSON_EXTRACT(s.data, '$.\"" + temp + "\"'), '\"', '') AS " + temp

sql = "SELECT" \
        " s.created_date," \
        " s.laboratory_id" \
        + col_marker + \
        " FROM sample s" \
        " WHERE s.is_last_version = 1" \
        " AND (s.data is not null or s.data = '[]')" \
        " AND s.is_test = 0" \
        " AND s.created_date BETWEEN '" + yearmonth + "-01 00:00:00' and '" + yearmonth + "-31 23:59:59'"

curs.execute(sql)
rows = curs.fetchall()

column_names = [i[0] for i in curs.description]
fp = open('temp.csv', 'w')
myFile = csv.writer(fp, lineterminator = '\n') #use lineterminator for windows
myFile.writerow(column_names)
myFile.writerows(rows)
fp.close()

# Connection 닫기
conn.close()