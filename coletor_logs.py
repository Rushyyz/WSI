import paramiko
import datetime
import webbrowser
import argparse # Importe o módulo argparse
import os # Para verificar a existência da chave SSH

def executar_comandos_remotos(host_name, host, user, key_file, port=2222):
    """
    Conecta via SSH a um servidor, executa comandos e coleta logs,
    salvando e abrindo o resultado em um arquivo HTML.
    """
    client = None # Inicializa client como None
    try:
        # Verifica se o arquivo da chave SSH existe
        if not os.path.isfile(key_file):
            print(f"Erro: Arquivo da chave SSH '{key_file}' não encontrado.")
            print("Verifique o caminho e as permissões do arquivo.")
            return

        # Criando conexão SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Tentando conectar ao {host_name} ({host}:{port}) como {user}...")
        client.connect(hostname=host, username=user, key_filename=key_file, port=port)
        print("Conexão SSH estabelecida com sucesso.")

        # Obter a data de hoje no formato YYYY-MM-DD
        data_hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # 🔹 1. Executar comandos adicionais primeiro
        comandos_adicionais = [
            "docker exec -i dashDB cat /sys/firmware/ocf/cpc_name",
            "docker exec -i dashDB sh -c 'cat /head/dwa/iu/instance/*/etc/dwa-apply.properties'",
            "docker exec -i dashDB wvcli system nodes",
            "docker exec -i dashDB system devices", # Comando original estava "wvcli system devices", corrigi para o que geralmente é usado com 'system'
            "docker exec -i dashDB status",
            "strings /opt/ibm/appliance/storage/head/dwa/var/server/event_log/hardwareEventLog.bin"
        ]

        comandos_output = ""
        for comando in comandos_adicionais:
            print(f"Executando comando: {comando}...")
            stdin, stdout, stderr = client.exec_command(comando)
            comando_resultado = stdout.read().decode().strip()
            comando_error = stderr.read().decode().strip()

            if comando_error:
                comando_resultado = f"Erro ao executar comando '{comando}': {comando_error}"
                print(comando_resultado) # Imprime o erro no console também

            comandos_output += f"<h3>Resultado do comando: <code>{comando}</code></h3><pre>{comando_resultado}</pre>"

        # 🔹 2. Ler logs depois dos comandos adicionais
        logs_paths = [
            '/opt/ibm/appliance/storage/head/dwa/var/log/trace/ibm_aqt_trace.{0..9}',
            '/opt/ibm/appliance/storage/head/dwa/var/log/dwa-apply/apply-instances-monitor.log',
            '/opt/ibm/appliance/storage/head/dwa/var/log/dwa-iu-control/control-iu-server.log.{0..4}',
            '/opt/ibm/appliance/storage/head/dwa/var/log/dwa-iu-control/control-iu-daemon.log',
            '/opt/ibm/appliance/storage/head/dwa/var/log/statistics/dbs-1/request/*',
            '/opt/ibm/appliance/storage/head/dwa/var/log/statistics/dbs-2/request/*',
            '/opt/ibm/appliance/storage/head/dwa/var/log/statistics/dbs-3/request/*'
        ]
        
        # Constrói o comando cat | grep para os logs
        # O uso de 'grep -Ev "query|..."' é bem específico e pode precisar de ajuste
        # dependendo dos logs que você realmente quer excluir.
        # Os caminhos com '{0..9}' ou '*' podem precisar de um shell para expansão.
        # Paramiko exec_command executa em um pseudo-terminal, que geralmente faz isso.
        
        full_log_command = ""
        for log_path in logs_paths:
            full_log_command += (
                f'echo "===== LOGS DE: {log_path} ====="; '
                f'cat {log_path} 2>/dev/null | '
                f'grep -iE "ERROR|SEVERE|FAIL|EXCEPTION" | '
                f'grep "{data_hoje}" | '
                f'grep -Ev "query|regular|SQLCODE so far is 0|spill|CloseOfDRDAConnectionDetected|SQLCARD|history|ODBC|INFO|DEBUG|COMMUNICATION|ignored|denied|AbortCommunicationException|reset|VECTOR|E4039|Update|GetVersionInformation"; '
            )

        print("Coletando logs de erro...")
        stdin, stdout, stderr = client.exec_command(full_log_command)
        dwa_logs = stdout.read().decode().strip()
        error_msg_logs = stderr.read().decode().strip()

        if error_msg_logs:
            print(f"Erro ao coletar logs (stderr): {error_msg_logs}")

        if not dwa_logs:
            print("Nenhum log de erro filtrado encontrado para a data de hoje.")
            dwa_logs = "Nenhum log de erro filtrado encontrado para a data de hoje."

        # 🔹 3. Criar HTML com logs e comandos
        timestamp_file = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        timestamp_display = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = f"""
        <html>
            <head>
                <title>Logs do Servidor: {host_name}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    h1, h2, h3 {{
                        color: #333;
                    }}
                    pre {{
                        background-color: #282828;
                        color: #fff;
                        padding: 20px;
                        border-radius: 8px;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        max-height: 500px;
                        overflow-y: auto;
                    }}
                    code {{
                        background-color: #eee;
                        padding: 2px 4px;
                        border-radius: 3px;
                    }}
                </style>
            </head>
            <body>
                <h1>Relatório de Logs e Comandos - {host_name}</h1>
                <p><strong>Servidor IP:</strong> {host}</p>
                <p><strong>Usuário:</strong> {user}</p>
                <p><strong>Porta SSH:</strong> {port}</p>
                <p><strong>Data e Hora da Consulta:</strong> {timestamp_display}</p>
                <hr>
                <h2>Resultados de Comandos Adicionais</h2>
                {comandos_output}
                <hr>
                <h2>Logs de Erro Filtrados (Hoje: {data_hoje})</h2>
                <pre>{dwa_logs}</pre>
            </body>
        </html>
        """

        # 🔹 4. Salvar e abrir HTML
        # Garante que o nome do arquivo HTML seja válido, substituindo caracteres problemáticos
        safe_host_name = host_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        html_filename = f"{safe_host_name}_logs_{timestamp_file}.html"
        
        with open(html_filename, "w", encoding="utf-8") as html_file: # Adicionado encoding para evitar problemas com caracteres especiais
            html_file.write(html_content)

        print(f"Arquivo HTML gerado com sucesso: {html_filename}")
        webbrowser.open(html_filename)

    except paramiko.AuthenticationException:
        print(f"Erro de autenticação para {host_name} ({host}). Verifique o usuário e a chave SSH.")
    except paramiko.SSHException as ssh_err:
        print(f"Erro SSH para {host_name} ({host}): {ssh_err}")
    except Exception as e:
        print(f"Erro inesperado ao conectar ou executar comandos para {host_name} ({host}): {e}")

    finally:
        if client: # Garante que client foi instanciado antes de tentar fechar
            client.close()
            print(f"Conexão SSH com {host_name} fechada.")

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
#    python coletor_logs.py --servidor_nome "CEC2C"  --servidor_ip "10.22.214.17" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "HOM-IDAA0002"  --servidor_ip "10.22.199.53" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0001-node01-CEC1B"  --servidor_ip "10.22.236.19" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0002-node01-CEC2B"  --servidor_ip "10.22.214.172" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0003-onZ-D2G1-LP1036"  --servidor_ip "10.22.194.4" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0003-onZ-D3G1-LP1031"  --servidor_ip "10.22.208.7" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0003-onZ-D3G4-LP1032"  --servidor_ip "10.22.208.8" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0003-onZ-D8G1-LP1037"  --servidor_ip "10.22.194.5" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0004-onZ-D0G1-LP2037"  --servidor_ip "10.22.214.167" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0004-onZ-D2G1-LP2036"  --servidor_ip "10.22.214.166" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0004-onZ-D3G1-LP2031"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
#    python coletor_logs.py --servidor_nome "IDAA0004-onZ-D3G4-LP2032"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222
