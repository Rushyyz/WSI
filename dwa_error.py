# NAO É MAIS USADO
import paramiko
import datetime
import os
import webbrowser  # Importa webbrowser para abrir o HTML no navegador
    
def executar_comandos_remotos(host_name, host, user, key_file, port=2222):
    try:
        # Criando conexão SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, key_filename=key_file, port=port)
  
        # Obter a data de hoje no formato YYYY-MM-DD
        data_hoje = datetime.datetime.now().strftime('%Y-%m-%d')

        # Construir o comando com a data substituída
        #command = 'docker exec -t dashDB grep -E "ERROR|SEVERE|FAIL|EXCEPTION" /head/dwa/var/log/trace/ibm_aqt_trace.{0..9} | grep "' + data_hoje + '"'
        command = (
            'docker exec -t dashDB grep -E "ERROR|SEVERE|FAIL|EXCEPTION" /head/dwa/var/log/trace/ibm_aqt_trace.{0..9} '
            '| grep "' + data_hoje + '" '
            '| grep -Ev "SQL|INFO|DEBUG|COMMUNICATION|Operation RECEIVE|AbortCommunicationException|reset|VECTOR|E4039|Socket"'  # Exclui múltiplas palavras
        )



        # Executando comando grep para filtrar logs
        stdin, stdout, stderr = client.exec_command(command)


        dwa_logs = stdout.read().decode().strip()
        error_msg = stderr.read().decode().strip()
        
        if error_msg:
            print(f"Erro ao executar o comando: {error_msg}")
        
        if not dwa_logs:
            print("Erro: Não foi possível obter as logs")
            dwa_logs = "Nenhum log encontrado para a data de hoje."

        # Gerando HTML com os logs
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
                <h2>Logs de Erro</h2>
                <pre>{dwa_logs}</pre>
            </body>
        </html>
        """

        # Salvando a saída HTML
        html_filename = f"{host_name}_logs_{timestamp.replace(' ', '_').replace(':', '-')}.html"
        with open(html_filename, "w") as html_file:
            html_file.write(html_content)
        
        print(f"Arquivo HTML gerado com sucesso: {html_filename}")
        
        # Abrir o arquivo HTML no navegador padrão
        webbrowser.open(html_filename)

    except Exception as e:
        print(f"Erro ao executar comandos: {e}")
    
    finally:
        client.close()  # Fecha a conexão SSH corretamente

if __name__ == "__main__":
    ####################### DEV #########################################################    
    servidor    = "Desenvolvimento"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.167"  # Substitua pelo IP do servidor    
    usuario = "root"         # Substitua pelo usuário SSH
    chave_ssh = "C:\\Users\\FelipeGustinelliBort\\Downloads\\bdb Doc\\scripts\\minha_chave.pem"  # Substitua pelo caminho da sua chave privada
    porta_ssh = 2222  # Porta do SSH

    # Chamada da função
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)

#######################idaa0008 ##########################################################

    servidor    = "D4G2_idaa0008"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.172"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh) 
