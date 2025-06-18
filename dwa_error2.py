#NAO É MAIS USADO
import paramiko
import datetime
import webbrowser

def executar_comandos_remotos(host_name, host, user, key_file, port=2222):
    try:
        # Criando conexão SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, key_filename=key_file, port=port)

        # Obter a data de hoje no formato YYYY-MM-DD
        data_hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # 🔹 1. Executar comandos adicionais primeiro
        comandos_adicionais = [
            "docker exec -i dashDB cat /sys/firmware/ocf/cpc_name",
            "docker exec -i dashDB sh -c 'cat /head/dwa/iu/instance/*/etc/dwa-apply.properties'",
            "docker exec -i dashDB wvcli system nodes",
            "docker exec -i dashDB wvcli system devices",
            "docker exec -i dashDB status",
            "strings /opt/ibm/appliance/storage/head/dwa/var/server/event_log/hardwareEventLog.bin"
        ]

        comandos_output = ""
        for comando in comandos_adicionais:
            stdin, stdout, stderr = client.exec_command(comando)
            comando_resultado = stdout.read().decode().strip()
            comando_error = stderr.read().decode().strip()

            if comando_error:
                comando_resultado = f"Erro ao executar o comando: {comando_error}"

            comandos_output += f"<h3>Resultado do comando: {comando}</h3><pre>{comando_resultado}</pre>"

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
        # REMOVED '/var/log/messages'
        command = ""
        for log_path in logs_paths:
            command += (
                f'echo "===== LOGS DE: {log_path} ====="; '  
                f'cat {log_path} 2>/dev/null | '
                f'grep -iE "ERROR|SEVERE|FAIL|EXCEPTION" | '
                f'grep "{data_hoje}" | '
                f'grep -Ev "query|regular|SQLCODE so far is 0|spill|CloseOfDRDAConnectionDetected|SQLCARD|history|ODBC|INFO|DEBUG|COMMUNICATION|ignored|denied|AbortCommunicationException|reset|VECTOR|E4039|Update|GetVersionInformation"; '
            )

        stdin, stdout, stderr = client.exec_command(command)
        dwa_logs = stdout.read().decode().strip()
        error_msg = stderr.read().decode().strip()

        if error_msg:
            print(f"Erro ao executar o comando: {error_msg}")

        if not dwa_logs:
            print("Nenhum log encontrado para a data de hoje.")
            dwa_logs = "Nenhum log encontrado."

        # 🔹 3. Criar HTML com logs e comandos
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                    h1 {{
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
                </style>
            </head>
            <body>
                <h1>Conteúdo do Log - {host_name}</h1>
                <p><strong>Data da consulta:</strong> {timestamp}</p>
                <h2>Comandos Adicionais</h2>
                {comandos_output}
                <h2>Logs de Erro</h2>
                <pre>{dwa_logs}</pre>
            </body>
        </html>
        """

        # 🔹 4. Salvar e abrir HTML
        html_filename = f"{host_name}_logs_{timestamp.replace(' ', '_').replace(':', '-')}.html"
        with open(html_filename, "w") as html_file:
            html_file.write(html_content)

        print(f"Arquivo HTML gerado com sucesso: {html_filename}")
        webbrowser.open(html_filename)

    except Exception as e:
        print(f"Erro ao executar comandos: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    usuario = "root"         # Substitua pelo usuário SSH
##    chave_ssh = "C:\\Users\\FelipeGustinelliBort\\Downloads\\bdb Doc\\scripts\\minha_chave.pem"  # Substitua pelo caminho da sua chave privada
    chave_ssh = "minha_chave.pem"  # Substitua pelo caminho da sua chave privada
    porta_ssh = 2222  # Porta do SSH
   

#######################idaa0004###############################################_D###########

    servidor    = "D3G4_idaa0004"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.162"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)   

####################### DEV #########################################################    
    servidor    = "Desenvolvimento"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.167"  # Substitua pelo IP do servidor    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)
#######################HOMOLOGACAO ##########################################################

    servidor    = "homologacao"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.194.5"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)
#######################idaa0000 ##########################################################

    servidor    = "D4G2_D3G4_idaa0000_006"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.17"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)    
#######################idaa0008 ##########################################################

    servidor    = "D4G2_idaa0008"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.172"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)     
#######################idaa0009 ##########################################################

    servidor    = "D4G2_D3G4_idaa0009_005"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.194.130"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)         
#######################idaa0001 ##########################################################

    servidor    = "D4G1_D3G4_idaa0001"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.236.19"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)     

#######################idaa0002 ##########################################################

    servidor    = "D4G1_D3G4_idaa0002"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.172"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)    

#######################idaa0003 ##########################################################

    servidor    = "D2G1_idaa0003"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.194.4"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)        
    
    
    
    
#######################idaa0004 ##########################################################

    servidor    = "D2G1_idaa0004"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.166"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)     

#######################idaa0001 ##########################################################

    servidor    = "D3G4_idaa0001"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.236.19"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)     

