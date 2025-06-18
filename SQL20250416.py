import jaydebeapi
import webbrowser
import argparse
# para executar use
# python SQL.py --driver_path "db2jcc4.jar" --jdbc_url "jdbc:db2://GWDB2.BB.COM.BR:50100/BDB2P04" --db_user "userid X" --db_pass "xxxx" --jdbc_driver "com.ibm.db2.jcc.DB2Driver"


parser = argparse.ArgumentParser(description="Executar consultas no DB2 e gerar um relatório HTML.")
parser.add_argument("--driver_path", required=True, help="Caminho para o driver JDBC")
parser.add_argument("--jdbc_url", required=True, help="URL de conexão JDBC")
parser.add_argument("--db_user", required=True, help="Usuário do banco de dados")
parser.add_argument("--db_pass", required=True, help="Senha do banco de dados")
parser.add_argument("--jdbc_driver", required=True, help="Classe do driver JDBC")
args = parser.parse_args()

conn = jaydebeapi.connect(args.jdbc_driver, args.jdbc_url, [args.db_user, args.db_pass], args.driver_path)

def executar_consulta(sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        colunas = [desc[0] for desc in cursor.description]
        resultados = cursor.fetchall()
        cursor.close()
        return colunas, resultados
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
        return [str(e)], []

sqls = {
    "VELOCIDADE DOS LOADs": """
        SELECT 
            DATE(ts_fim_job_crga) AS DATA, 
            RTRIM(ACCELERATORNAME) AS ACCELERATORNAME, 
            SUM(TMP_CRGA) AS LOAD_TIME_SEC,  
            SUM(QTD_REG_CRGO) AS NUMBER_OF_RECORDS,  
            SUM(JOB_CPU_TIME) AS JOB_CPU_TIME,  
            SUM(QTD_TOT_CRGO) / 1024 QTD_GB,  
            COUNT(*) AS COUNT_LOADS 
        FROM DB2DBU.IDAA_LOG_LOAD   
        WHERE DATE(ts_fim_job_crga) = (CURRENT DATE - 4 DAYS)   
        GROUP BY DATE(ts_fim_job_crga), ACCELERATORNAME   
        ORDER BY DATA, ACCELERATORNAME ASC  
    """,
    "QUANTIDADE DO MESMO ERROR NO LOAD POR IDAA": """
        SELECT COUNT(*), RTRIM(ACCELERATORNAME) ACCEL, CD_MSG_RTN MESSAGE, DATE(TS_FIM_JOB_CRGA) TS_FIM_JOB_CRGA 
        FROM DB2DBU.IDAA_LOG_LOAD 
        WHERE CD_MSG_RTN NOT IN ('01', '99', 'AQT20014I', 'AQT10000I') 
        AND DATE(TS_FIM_JOB_CRGA) >= (CURRENT DATE - 1 DAYS) 
        GROUP BY ACCELERATORNAME, CD_MSG_RTN, DATE(TS_FIM_JOB_CRGA) 
        ORDER BY 1
    """,
    "LOAD COM ERRO QUE O TIRAERRO NAO RESOLVEU": """
        SELECT COUNT(*), CREATOR, RTRIM(NM_TABLE) TABLE, RTRIM(ACCELERATORNAME) ACCEL, DATE(TS_FIM_JOB_CRGA) TS_FIM_JOB_CRGA 
        FROM DB2DBU.IDAA_LOG_LOAD 
        WHERE DATE(TS_FIM_JOB_CRGA) >= (CURRENT DATE  - 2 DAYS) 
        AND CD_MSG_RTN = '99' 
        AND TX_MSG_RTN LIKE 'TIRAERRO%' 
        GROUP BY CREATOR, NM_TABLE, ACCELERATORNAME, DATE(TS_FIM_JOB_CRGA) 
        HAVING COUNT(*) > 1 
        ORDER BY 1 DESC
    """,
    "TODOS OS LOADS DE HOJE": """
        SELECT RTRIM(ACCELERATORNAME), rtrim(IND_REPL) REPL, TMP_CRGA AS TMPO, 
        QTD_REG_CRGO, (QTD_TOT_CRGO/1024) AS TAM_GB, TS_SYSCOPY, TS_INCL, 
        time(TS_INC_JOB_CRGA) INICIO, TIME(ts_fim_job_crga) FIM, RTRIM(CREATOR) CREATOR,  
        RTRIM(NM_TABLE) TABLE, JOBNAME, JOBLOAD, JOBID, JOB_CPU_TIME,
           CASE LOAD_STATUS_FIM
           WHEN 'C' THEN 'correct'
           WHEN 'E' THEN 'error'
           ELSE LOAD_STATUS_FIM 
           END CASE,  
        rtrim(CD_MSG_RTN) MESSAGE, TX_MSG_RTN AS XML
        FROM BDB2P04.DB2DBU.IDAA_LOG_LOAD
        WHERE date(ts_fim_job_crga) >= CURRENT_DATE 
        ORDER BY TS_FIM_JOB_CRGA DESC LIMIT 1000
    """
}

html_content = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consulta DB2</title>
    <style>
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        pre { background-color: #eee; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
"""

for titulo, sql in sqls.items():
    html_content += f"<h2>SQL Executado - {titulo}</h2>"
    html_content += f"<pre>{sql}</pre>"
    colunas, dados = executar_consulta(sql)

    if not dados:
        html_content += "<p>Nenhum resultado encontrado.</p>"
        continue

    html_content += f"<h2>Resultados da Consulta - {titulo}</h2>\n<table>\n<tr>\n"

    for coluna in colunas:
        html_content += f"    <th>{coluna}</th>\n"
    html_content += "</tr>\n"

    for row in dados:
        html_content += "<tr>\n"
        for valor in row:
            html_content += f"    <td>{valor}</td>\n"
        html_content += "</tr>\n"

    html_content += "</table>\n"

html_content += "</body>\n</html>"

html_file = "SQL_RESULTADO.html"
with open(html_file, "w", encoding="utf-8") as file:
    file.write(html_content)

webbrowser.open(html_file)
conn.close()

print(f"Arquivo HTML salvo como '{html_file}' e aberto no navegador!")
