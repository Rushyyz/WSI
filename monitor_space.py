import paramiko
import datetime
import csv
import os
import argparse # Importe o módulo argparse

def executar_comandos_remotos(host_name, host, user, key_file, port=2222):
    """
    Tenta conectar via SSH, executa o comando df -m, e salva o resultado em CSV.
    """
    client = None # Inicializa client como None para garantir que está definido
    try:
        # Criando conexão SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Tentando conectar ao {host_name} ({host}:{port}) como {user}...")
        client.connect(hostname=host, username=user, key_filename=key_file, port=port)
        print("Conexão SSH estabelecida com sucesso.")
        
        # Executando comando df -m para obter espaço disponível em /srv/data_pool
        stdin, stdout, stderr = client.exec_command("df -m /srv/data_pool | tail -1 | awk '{print $5}'")
        used_percentage = stdout.read().decode().strip()
        
        error_msg = stderr.read().decode().strip()
        if error_msg:
            print(f"Erro ao executar o comando no servidor {host_name}: {error_msg}")
        
        if not used_percentage:
            print(f"Erro: Não foi possível obter o uso de disco para {host_name}.")
            used_percentage = "N/A" # Define um valor para não quebrar o CSV
            
        # Criando saída formatada (opcional, mas mantido da sua original)
        result = f"Servidor: {host_name} Uso do disco em /srv/Data_pool: {used_percentage}\n\n"
        # print(f"Resultado para {host_name}: {used_percentage}") # Descomente para ver no console
            
        # Salvando os dados em CSV
        csv_filename = host_name.replace(" ", "_").replace("/", "_") + "_uso_disco.csv" # Tratamento para nomes de arquivo válidos
        file_exists = os.path.isfile(csv_filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(csv_filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Data", "Servidor", "Uso%"])
            writer.writerow([timestamp, host_name, used_percentage])
        
        print(f"Dados para {host_name} salvos em {csv_filename}")
        
    except paramiko.AuthenticationException:
        print(f"Erro de autenticação para {host_name}. Verifique o usuário e a chave SSH.")
    except paramiko.SSHException as ssh_err:
        print(f"Erro SSH para {host_name}: {ssh_err}")
    except FileNotFoundError:
        print(f"Erro: Arquivo da chave SSH '{key_file}' não encontrado ou caminho incorreto para {host_name}.")
    except Exception as e:
        print(f"Erro inesperado ao conectar ou executar comandos para {host_name}: {e}")
        
    finally:
        if client: # Garante que client foi instanciado antes de tentar fechar
            client.close()
            # print(f"Conexão SSH com {host_name} fechada.") # Descomente se quiser ver o fechamento
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
    parser.add_argument(
        "--servidor_ip",
        type=str,
        required=True,
        help="Endereço IP do servidor SSH"
    )
    parser.add_argument(
        "--usuario",
        type=str,
        required=True,
        help="Nome de usuário para a conexão SSH"
    )
    parser.add_argument(
        "--chave_ssh",
        type=str,
        required=True,
        help="Caminho completo para o arquivo da chave privada SSH (formato OpenSSH/Paramiko)"
    )
    parser.add_argument(
        "--porta_ssh",
        type=int,
        default=2222,  # Porta padrão, pode ser 22 ou a que você usa
        help="Número da porta SSH (padrão: 2222)"
    )

    args = parser.parse_args()

    executar_comandos_remotos(
        args.servidor_nome,
        args.servidor_ip,
        args.usuario,
        args.chave_ssh,
        args.porta_ssh
    )
#    python monitor_space.py --servidor_nome "CEC2C"  --servidor_ip "10.22.214.17" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "HOM-IDAA0002"  --servidor_ip "10.22.199.53" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0001-node01-CEC1B"  --servidor_ip "10.22.236.19" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0002-node01-CEC2B"  --servidor_ip "10.22.214.172" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0003-onZ-D2G1-LP1036"  --servidor_ip "10.22.194.4" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0003-onZ-D3G1-LP1031"  --servidor_ip "10.22.208.7" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0003-onZ-D3G4-LP1032"  --servidor_ip "10.22.208.8" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0003-onZ-D8G1-LP1037"  --servidor_ip "10.22.194.5" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0004-onZ-D0G1-LP2037"  --servidor_ip "10.22.214.167" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0004-onZ-D2G1-LP2036"  --servidor_ip "10.22.214.166" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0004-onZ-D3G1-LP2031"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python monitor_space.py --servidor_nome "IDAA0004-onZ-D3G4-LP2032"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

