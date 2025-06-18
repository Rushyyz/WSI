import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import os
from datetime import datetime, timedelta
import shutil
import webbrowser

def plot_and_alert_latency(host_name, alert_threshold=3600):
    """
    Reads detailed latency data from a CSV, generates line graphs for latency and
    applied operations, and emits alerts based on latency threshold.
    Generates one graph per subscription, filtering for the last 10 days,
    and returns a list of alerts and generated graph filenames.
    This function expects the CSV file to be named '{host_name}_latency_data.csv'.
    """
    safe_host_name = host_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    csv_filename = f"{safe_host_name}_latency_data.csv" # Expected file name by this function
    
    generated_graph_files = []
    alerts = []

    if not os.path.isfile(csv_filename):
        print(f"Erro: Arquivo CSV '{csv_filename}' não encontrado para o servidor '{host_name}'.")
        print("Por favor, certifique-se de que o arquivo de dados foi preparado.")
        return generated_graph_files, alerts

    try:
        print(f"Carregando dados de '{csv_filename}' para gerar gráficos e verificar alertas para o servidor '{host_name}'...")
        df = pd.read_csv(csv_filename)

        # Combinar 'Date' e 'Time' em uma nova coluna 'Timestamp' se existirem
        if 'Date' in df.columns and 'Time' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            df.drop(columns=['Date', 'Time'], inplace=True)
        
        # Garantir que as colunas essenciais existam
        required_columns = [
            "Timestamp", "Subscription", "Latency_Seconds", "Host_Name",
            "Applied_Insert", "Applied_Delete"
        ]
        if not all(col in df.columns for col in required_columns):
            print(f"Erro: O arquivo CSV '{csv_filename}' está faltando uma ou mais colunas necessárias: {required_columns}.")
            return generated_graph_files, alerts

        # Converter 'Timestamp' para objetos datetime (redundante se já criado acima, mas garante)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        
        # --- Filtrar dados para os últimos 10 dias ---
        current_time = datetime.now()
        start_date_filter = current_time - timedelta(days=10)
        df = df[df['Timestamp'] >= start_date_filter].copy()

        # Filtrar dados para o host_name específico
        df_filtered = df[df["Host_Name"].str.contains(host_name, case=False, na=False)].copy()

        if df_filtered.empty:
            print(f"Nenhum dado encontrado para o servidor '{host_name}' em '{csv_filename}' nos últimos 10 dias.")
            return generated_graph_files, alerts

        df_filtered.sort_values(by="Timestamp", inplace=True)

        # --- 1. Emitir alertas (Latência) ---
        for _, row in df_filtered.iterrows():
            if row["Latency_Seconds"] > alert_threshold:
                alert_msg = (f"🚨 ALERTA para {row['Host_Name']} (Inscrição: {row['Subscription']}) "
                             f"em {row['Timestamp']}: Latência de {row['Latency_Seconds']} segundos "
                             f"(limite: {alert_threshold} segundos)!")
                print(alert_msg)
                alerts.append(alert_msg)

        # --- Iterar sobre as assinaturas únicas para gerar gráficos individuais ---
        date_form = DateFormatter('%Y-%m-%d %H:%M')

        for subscription_name in df_filtered["Subscription"].unique():
            sub_df = df_filtered[df_filtered["Subscription"] == subscription_name].copy()
            
            # --- 2. Gerar o Gráfico de Latência para a assinatura atual ---
            plt.figure(figsize=(14, 7))
            plt.plot(sub_df["Timestamp"], sub_df["Latency_Seconds"], marker="o", linestyle='-', label=f'{subscription_name} Latência')

            plt.axhline(y=alert_threshold, color='r', linestyle='--', label=f'Limite de Alerta ({alert_threshold}s)')

            plt.gca().xaxis.set_major_formatter(date_form)

            plt.xlabel("Data e Hora")
            plt.ylabel("Latência (segundos)")
            plt.title(f"Latência da Inscrição para {subscription_name} no Servidor {host_name} (Últimos 10 Dias)")
            plt.legend(loc='upper left')
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout(rect=[0, 0, 1, 1])

            latency_png_filename = f"{safe_host_name}_{subscription_name.replace(' ', '_')}_latency_graph_last_10_days.png"
            plt.savefig(latency_png_filename)
            generated_graph_files.append(latency_png_filename)
            print(f"Gráfico de latência para {subscription_name} salvo como '{latency_png_filename}'")
            plt.close()

            # --- 3. Gerar o Gráfico de Operações Aplicadas no Alvo para a assinatura atual ---
            plt.figure(figsize=(14, 7))
            plt.plot(sub_df["Timestamp"], sub_df["Applied_Insert"],
                     marker="o", linestyle='-', label=f'{subscription_name} - Inserções')
            
            plt.plot(sub_df["Timestamp"], sub_df["Applied_Delete"],
                     marker="x", linestyle='--', label=f'{subscription_name} - Exclusões')

            plt.gca().xaxis.set_major_formatter(date_form)
            plt.xlabel("Data e Hora")
            plt.ylabel("Número de Operações")
            plt.title(f"Operações Aplicadas no Alvo para {subscription_name} no Servidor {host_name} (Últimos 10 Dias)")
            plt.legend(loc='upper left')
            plt.xticks(rotation=45, ha='right', fontsize=9)
            plt.yticks(fontsize=9)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.ticklabel_format(style='plain', axis='y')
            plt.tight_layout(rect=[0, 0, 1, 1])

            applied_ops_png_filename = f"{safe_host_name}_{subscription_name.replace(' ', '_')}_applied_operations_graph_last_10_days.png"
            plt.savefig(applied_ops_png_filename)
            generated_graph_files.append(applied_ops_png_filename)
            print(f"Gráfico de operações aplicadas para {subscription_name} salvo como '{applied_ops_png_filename}'")
            plt.close()
        
        return generated_graph_files, alerts


    except pd.errors.EmptyDataError:
        print(f"Erro: O arquivo CSV '{csv_filename}' está vazio ou malformado.")
        return generated_graph_files, alerts
    except Exception as e:
        print(f"Erro inesperado ao plotar ou alertar para {host_name}: {e}")
        return generated_graph_files, alerts


if __name__ == "__main__":
    latency_alert_threshold = 3600 # 1 hora em segundos
    
    # Lista para armazenar todos os arquivos HTML gerados para abertura posterior
    all_generated_html_files = []

    # Iterar sobre todos os arquivos no diretório atual
    for filename in os.listdir('.'):
        if filename.endswith('_latency.csv'):
            original_csv_name = filename
            
            # Extrair o nome do servidor do nome do arquivo (ex: 'CEC2C' de 'CEC2C_latency.csv')
            host_name = original_csv_name.replace('_latency.csv', '')
            safe_host_name = host_name.replace(" ", "_").replace("/", "_").replace("\\", "_")

            # Nome do arquivo temporário que a função plot_and_alert_latency espera
            temp_detailed_csv_name = f"{safe_host_name}_latency_data.csv"

            print(f"\n--- Processando arquivo: {original_csv_name} (Servidor: {host_name}) ---")

            # Renomear o arquivo original para o nome temporário esperado pela função
            try:
                shutil.move(original_csv_name, temp_detailed_csv_name)
                print(f"Temporariamente renomeado '{original_csv_name}' para '{temp_detailed_csv_name}'.")
            except Exception as e:
                print(f"Erro ao renomear o arquivo {original_csv_name}: {e}")
                continue # Pular para o próximo arquivo se houver um erro de renomeação

            # --- Executar a função de plotagem e alerta para o arquivo atual ---
            generated_graph_files, alerts = plot_and_alert_latency(
                host_name,
                latency_alert_threshold
            )

            # --- Gerar o arquivo HTML para o arquivo atual ---
            html_filename = f"{safe_host_name}_relatorio_latencia_operacoes.html"
            html_body_content = ""

            if not generated_graph_files:
                html_body_content += "<p>Nenhum gráfico gerado. Verifique os dados e as configurações.</p>"
            else:
                subscriptions_processed = set()
                for graph_file in generated_graph_files:
                    # Extrai o nome da assinatura para agrupamento
                    parts = graph_file.split('_')
                    subscription_name_index = 1 # Índice para DWA_BDB2P04 ou DWA_B4DB2G2
                    
                    if len(parts) > subscription_name_index:
                        subscription_name = parts[subscription_name_index]
                    else:
                        subscription_name = "Unknown_Subscription"
                    
                    if subscription_name not in subscriptions_processed:
                        html_body_content += f"<h3>Inscrição: {subscription_name}</h3>\n"
                        subscriptions_processed.add(subscription_name)

                    graph_type = "Latência" if "latency" in graph_file else "Operações Aplicadas"
                    html_body_content += f"""
                    <div class="graph-container">
                        <h4>Gráfico de {graph_type} (Últimos 10 Dias)</h4>
                        <img src="{graph_file}" alt="Gráfico de {graph_type} - {subscription_name}">
                    </div>
                    """

            alert_html_content = ""
            if alerts:
                alert_html_content = "<p class='alert'>" + "<br>\n".join(alerts) + "</p>"
            else:
                alert_html_content = "<p>Nenhum alerta de latência nos últimos 10 dias.</p>"

            full_html_content = f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Relatório de Latência e Operações de Replicação para {host_name}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
                    h1 {{ color: #333; text-align: center; }}
                    h2 {{ color: #555; border-bottom: 2px solid #ccc; padding-bottom: 5px; margin-top: 40px; text-align: center; }}
                    h3 {{ color: #007bff; margin-top: 30px; text-align: center; }}
                    h4 {{ color: #666; margin-top: 15px; text-align: center; }}
                    .graph-container {{ 
                        margin: 20px auto; 
                        padding: 15px; 
                        border: 1px solid #ddd; 
                        border-radius: 8px; 
                        background-color: #fff;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        max-width: 900px;
                    }}
                    img {{ max-width: 100%; height: auto; display: block; margin: 0 auto; border: 1px solid #eee; border-radius: 4px; }}
                    .alert-section {{
                        background-color: #ffe0e0;
                        border: 1px solid #ff9999;
                        padding: 15px;
                        margin: 20px auto;
                        border-radius: 8px;
                        max-width: 900px;
                    }}
                    .alert {{ color: red; font-weight: bold; line-height: 1.6; }}
                    .alert-section p {{ margin: 0; }}
                </style>
            </head>
            <body>
                <h1>Relatório de Latência e Operações de Replicação para {host_name}</h1>

                <h2>Gráficos dos Últimos 10 Dias</h2>
                {html_body_content}

                <h2>Alertas de Latência (Últimos 10 Dias)</h2>
                <div class="alert-section">
                    {alert_html_content}
                </div>

            </body>
            </html>
            """

            # Salvar o conteúdo HTML em um arquivo
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(full_html_content)

            print(f"Arquivo HTML '{html_filename}' gerado com sucesso.")
            all_generated_html_files.append(os.path.abspath(html_filename)) # Adiciona à lista para abertura

            # Renomear o arquivo de volta ao nome original
            try:
                shutil.move(temp_detailed_csv_name, original_csv_name)
                print(f"Renomeado de volta '{temp_detailed_csv_name}' para '{original_csv_name}'.")
            except Exception as e:
                print(f"Erro ao renomear o arquivo {temp_detailed_csv_name} de volta: {e}")

    # --- Abrir todos os arquivos HTML gerados no navegador padrão ---
    if all_generated_html_files:
        print("\n--- Abrindo todos os relatórios HTML no navegador ---")
        for html_file_path in all_generated_html_files:
            try:
                webbrowser.open_new_tab(html_file_path)
                print(f"Abrindo '{html_file_path}' no navegador padrão...")
            except Exception as e:
                print(f"Não foi possível abrir o arquivo HTML '{html_file_path}' automaticamente: {e}")
                print(f"Por favor, abra-o manualmente no seu navegador.")
