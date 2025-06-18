import re
import pandas as pd
import os
import argparse # Manter argparse caso o usuário queira rodar para um arquivo específico no futuro, mas não será usado no loop principal

def process_html_and_save_latency_data(html_content, host_name_override=None):
    """
    Processa o conteúdo HTML do log para extrair informações de latência
    e salva-as em um arquivo CSV.

    Args:
        html_content (str): O conteúdo completo do arquivo HTML.
        host_name_override (str, optional): Um nome de host para substituir
                                            o extraído do título HTML. Padrão para None.
    """
    # Extrair nome do host do título HTML
    host_name = "Unknown_Host"
    title_match = re.search(r'<title>Logs do Servidor:\s*(.*?)</title>', html_content, re.IGNORECASE)
    if title_match:
        host_name = title_match.group(1).strip()

    # Se um nome de host de substituição for fornecido, use-o
    if host_name_override:
        host_name = host_name_override

    # Formatar o nome do host para ser seguro para o nome do arquivo
    safe_host_name = host_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    csv_filename = f"{safe_host_name}_latency.csv"

    # Extrair o bloco <pre> do HTML que contém os logs do hardwareEventLog.bin
    html_extract_pattern = re.compile(
        r'<h3>Resultado do comando: <code>strings .*?/hardwareEventLog\.(?:bin|log)</code></h3>\s*<pre>(.*?)</pre>',
        re.IGNORECASE | re.DOTALL
    )
    match_html = html_extract_pattern.search(html_content)
    if not match_html:
        print("❌ Erro: Bloco de log de 'hardwareEventLog.bin' não encontrado no HTML. Verifique o formato do arquivo.")
        return

    log_text = match_html.group(1).strip()

    # Regex para capturar linhas com informações de "Integrated Synchronization status"
    # Campos capturados: data, hora, assinatura, latência, RBA/LRSN do último commit,
    # número de transações abertas, RBA/LRSN da transação aberta mais antiga (opcional),
    # operações de inserção, atualização, exclusão (parsed e aplicadas).
    log_entry_pattern = re.compile(
        r'(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2})\s*.*?Subscription: .*?(?P<subscription>DWA_[A-Z0-9]+)_20.*?'
        r'Latency (?P<latency>\d+) seconds\. Latest commit RBA/LRSN (?P<latest_commit>0x[0-9A-Fa-f]+)\. '
        r'Number of open transactions (?P<open_tx>\d+)(?:, earliest open RBA/LRSN (?P<earliest_open>0x[0-9A-Fa-f]+))?\. '
        r'Parsed source operations: (?P<parsed_insert>\d+) insert, (?P<parsed_update>\d+) update, (?P<parsed_delete>\d+) delete\. '
        r'Applied target operations: (?P<applied_insert>\d+) insert, (?P<applied_delete>\d+) delete\.',
        re.DOTALL
    )

    data_records = []

    # Iterar sobre todas as ocorrências da regex no texto do log
    for match in log_entry_pattern.finditer(log_text):
        # O campo 'earliest_open' é opcional, então verificamos se ele foi capturado
        earliest_open_rba_lrsn = match.group('earliest_open') if match.group('earliest_open') else 'N/A'

        data_records.append({
            "Date": match.group('date'),
            "Time": match.group('time'),
            "Subscription": match.group('subscription'),
            "Latency_Seconds": int(match.group('latency')),
            "Latest_Commit_RBA_LRSN": match.group('latest_commit'),
            "Open_Transactions": int(match.group('open_tx')),
            "Earliest_Open_RBA_LRSN": earliest_open_rba_lrsn,
            "Parsed_Insert": int(match.group('parsed_insert')),
            "Parsed_Update": int(match.group('parsed_update')),
            "Parsed_Delete": int(match.group('parsed_delete')),
            "Applied_Insert": int(match.group('applied_insert')),
            "Applied_Delete": int(match.group('applied_delete')),
            "Host_Name": host_name
        })

    if not data_records:
        print("❌ Nenhuma linha de log de latência com 'Latest' encontrada no bloco especificado do HTML.")
        return

    df = pd.DataFrame(data_records)
    # Ordenar o DataFrame por data e hora para garantir que os dados estejam em ordem cronológica
    df.sort_values(by=["Date", "Time"], inplace=True)

    try:
        # Salvar o DataFrame em um arquivo CSV
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        print(f"✅ Dados de latência salvos com sucesso em '{csv_filename}'")
    except IOError as e:
        print(f"❌ Erro ao salvar o arquivo CSV '{csv_filename}': {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado ao salvar o CSV: {e}")
            
if __name__ == "__main__":
    print("Iniciando o processamento de arquivos HTML de logs para gerar CSVs de latência...")
    processed_files_count = 0
    generated_csv_files = []

    # Iterar sobre todos os arquivos no diretório atual
    for filename in os.listdir('.'):
        # Usar regex para corresponder ao padrão *_logs_*.html
        # O grupo 1 captura o nome do servidor antes de '_logs_'
        match = re.match(r'^(.*?)_logs_.*\.html$', filename)
        if match:
            html_file_path = filename
            # O nome do servidor para usar como host_name_override
            # Isso garante que o nome do servidor seja corretamente derivado para o CSV
            server_name_from_filename = match.group(1) 

            print(f"\n--- Processando arquivo: {html_file_path} ---")
            
            try:
                # Ler o conteúdo do arquivo HTML
                with open(html_file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Chamar a função principal para processar e salvar os dados
                # Usamos server_name_from_filename para garantir o nome correto no CSV
                process_html_and_save_latency_data(html_content, host_name_override=server_name_from_filename)
                processed_files_count += 1

            except Exception as e:
                print(f"❌ Ocorreu um erro ao ler ou processar o arquivo HTML '{html_file_path}': {e}")
    
    if processed_files_count > 0:
        print(f"\nProcessamento concluído. {processed_files_count} arquivo(s) HTML de log processado(s).")
        print("Arquivos CSV de latência correspondentes foram criados no diretório atual.")
        # Você pode listar os arquivos CSV gerados se quiser
        # for csv_file in os.listdir('.'):
        #     if csv_file.endswith('_latency.csv'):
        #         print(f"- {csv_file}")
    else:
        print("\nNenhum arquivo '.*_logs_.*\.html' encontrado no diretório atual para processar.")
