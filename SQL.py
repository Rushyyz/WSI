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
    "APPLYMON_QASN4": """
    SELECT  ROWS_PROCESSED AS LINHAS_PROCESSADAS,
    MONITOR_TIME AS ULTIMO_TIMESTAMP,
    RECVQ as FILA_RECVQ,
    TRANS_SERIALIZED as TRANS_SERIALIZED,
    ROWS_APPLIED as ROWS_APPLIED,
    APPLY_SLEEP_TIME as APPLY_SLEEP_TIME,
    DEADLOCK_RETRIES as DEADLOCK_RETRIES,
    HEARTBEAT_LATENCY AS HEARTBEAT_LATENCY_MS,
    QDEPTH as QDEPTH,
    VARCHAR(TIMESTAMPDIFF(2, CHAR((CURRENT_TIMESTAMP - OLDEST_TRANS))))	AS QUEUE_DELAY_SEGS,
    END2END_LATENCY AS END2END_LATENCY,
    QLATENCY AS QLATENCY,
    CAPTURE_LATENCY AS CAPTURE_LATENCY,
    Q_PERCENT_FULL AS Q_PERCENT_FULL,
    APPLY_LATENCY AS APPLY_LATENCY
FROM QASN4.IBMQREP_APPLYMON
WHERE MONITOR_TIME > '2025-06-17 09:39:03.947'
ORDER BY MONITOR_TIME DESC
         
    """,
    
    "APPLYMON_QASN3": """
         SELECT  ROWS_PROCESSED AS LINHAS_PROCESSADAS,
    MONITOR_TIME AS ULTIMO_TIMESTAMP,
    RECVQ as FILA_RECVQ,
    TRANS_SERIALIZED as TRANS_SERIALIZED,
    ROWS_APPLIED as ROWS_APPLIED,
    APPLY_SLEEP_TIME as APPLY_SLEEP_TIME,
    DEADLOCK_RETRIES as DEADLOCK_RETRIES,
    HEARTBEAT_LATENCY AS HEARTBEAT_LATENCY_MS,
    QDEPTH as QDEPTH,
    VARCHAR(TIMESTAMPDIFF(2, CHAR((CURRENT_TIMESTAMP - OLDEST_TRANS))))	AS QUEUE_DELAY_SEGS,
    END2END_LATENCY AS END2END_LATENCY,
    QLATENCY AS QLATENCY,
    CAPTURE_LATENCY AS CAPTURE_LATENCY,
    Q_PERCENT_FULL AS Q_PERCENT_FULL,
    APPLY_LATENCY AS APPLY_LATENCY
FROM QASN3.IBMQREP_APPLYMON
WHERE MONITOR_TIME > '2025-06-17 09:39:03.947'
ORDER BY MONITOR_TIME DESC

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
