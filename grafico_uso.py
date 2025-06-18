import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import argparse # Importe o módulo argparse
import os # Para usar os.path.isfile

def grafico_uso(host_name):
    """
    Gera um gráfico de uso de disco a partir de um arquivo CSV específico.
    """
    # Tratamento para nomes de arquivo válidos no caso de espaços ou barras
    csv_filename = host_name.replace(" ", "_").replace("/", "_") + "_uso_disco.csv"
    png_filename = host_name.replace(" ", "_").replace("/", "_") + "_uso_disco.png" # Nome para o arquivo de imagem

    if not os.path.isfile(csv_filename):
        print(f"Erro: Arquivo CSV '{csv_filename}' não encontrado para o servidor '{host_name}'.")
        print("Certifique-se de que o script de coleta de dados SSH foi executado para este servidor.")
        return

    try:
        print(f"Carregando dados de '{csv_filename}' para gerar o gráfico...")
        # Carregar os dados do CSV
        df = pd.read_csv(csv_filename)

        # Verificar se as colunas essenciais existem
        if "Data" not in df.columns or "Uso%" not in df.columns or "Servidor" not in df.columns:
            print(f"Erro: O arquivo CSV '{csv_filename}' não contém as colunas 'Data', 'Uso%' ou 'Servidor'.")
            return

        # Converter a coluna "Data" para datetime
        df["Data"] = pd.to_datetime(df["Data"], format="%Y-%m-%d %H:%M:%S")
        
        # Remover '%' e converter "Uso%" para numérico
        # Adicionado tratamento para valores não numéricos após remover '%'
        df["Uso%"] = df["Uso%"].astype(str).str.replace('%', '', regex=False)
        # Tentar converter para float, coercing erros para NaN
        df["Uso%"] = pd.to_numeric(df["Uso%"], errors='coerce')
        # Remover linhas com valores NaN em 'Uso%' (se houver dados inválidos)
        df.dropna(subset=['Uso%'], inplace=True)

        if df.empty:
            print(f"Não há dados válidos de uso de disco para '{host_name}' após o pré-processamento.")
            return

        # Ordenar os dados pela data
        df = df.sort_values(by="Data")

        # Criar o gráfico
        plt.figure(figsize=(12, 6)) # Aumentei um pouco o tamanho para melhor visualização
        
        # Filtra os dados apenas para o servidor especificado no host_name
        # Isso é importante para que o gráfico mostre apenas o servidor desejado
        dados_servidor = df[df["Servidor"].str.contains(host_name, case=False, na=False)]
        
        if dados_servidor.empty:
            print(f"Nenhum dado encontrado para o servidor '{host_name}' no arquivo '{csv_filename}'.")
            return

        plt.plot(dados_servidor["Data"], dados_servidor["Uso%"], marker="o", linestyle='-', label=host_name)

        # Definir o formato da data no eixo X
        date_form = DateFormatter('%Y-%m-%d %H:%M') # Mostra data e hora
        plt.gca().xaxis.set_major_formatter(date_form)

        plt.xlabel("Data e Hora")
        plt.ylabel("Uso de Disco (%)")
        plt.title(f"Uso de Disco para {host_name}")
        plt.legend()
        plt.xticks(rotation=45, ha='right', fontsize=9)
        plt.yticks(fontsize=9)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout() # Ajusta o layout para evitar sobreposição

        # Salvar o gráfico
        plt.savefig(png_filename)
        print(f"Gráfico salvo como '{png_filename}'")
        #plt.show() # Descomente esta linha se quiser que o gráfico apareça em uma janela

    except pd.errors.EmptyDataError:
        print(f"Erro: O arquivo CSV '{csv_filename}' está vazio ou mal formatado.")
    except Exception as e:
        print(f"Erro ao gerar gráfico para '{host_name}': {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analisa a Latency de Subscriptions em logs SSH e gera um gráfico, com alertas."
    )

    parser.add_argument(
        "--servidor_nome",
        type=str,
        required=True,
        help="Nome do servidor para a conexão SSH (ex: meu_servidor_web)"
    )

    args = parser.parse_args()

    grafico_uso(
        args.servidor_nome
    )
#    python gerar_grafico.py --servidor_nome "CEC2C"  
#    python gerar_grafico.py --servidor_nome "HOM-IDAA0002"  
#    python gerar_grafico.py --servidor_nome "IDAA0001-node01-CEC1B"  
#    python gerar_grafico.py --servidor_nome "IDAA0002-node01-CEC2B"  
#    python gerar_grafico.py --servidor_nome "IDAA0003-onZ-D2G1-LP1036" 
#    python gerar_grafico.py --servidor_nome "IDAA0003-onZ-D3G1-LP1031" 
#    python gerar_grafico.py --servidor_nome "IDAA0003-onZ-D3G4-LP1032" 
#    python gerar_grafico.py --servidor_nome "IDAA0003-onZ-D8G1-LP1037" 
#    python gerar_grafico.py --servidor_nome "IDAA0004-onZ-D0G1-LP2037" 
#    python gerar_grafico.py --servidor_nome "IDAA0004-onZ-D2G1-LP2036" 
#    python gerar_grafico.py --servidor_nome "IDAA0004-onZ-D3G1-LP2031" 
#    python gerar_grafico.py --servidor_nome "IDAA0004-onZ-D3G4-LP2032" 
