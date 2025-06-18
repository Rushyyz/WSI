import paramiko
import datetime
import csv
import os

def executar_comandos_remotos(host_name, host, user, key_file, port=2222):
    try:
        # Criando conexão SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, key_filename=key_file, port=port)
        
        
        # Executando comando df -m para obter espaço disponível em /head
        stdin, stdout, stderr = client.exec_command("df -m /srv/data_pool | tail -1 | awk '{print $5}'")
        used_percentage = stdout.read().decode().strip()
        
        error_msg = stderr.read().decode().strip()
        if error_msg:
            print(f"Erro ao executar o comando: {error_msg}")
        
        if not used_percentage:
            print("Erro: Não foi possível obter o uso de disco.")



        
        # Criando saída formatada
        result = f"Servidor: {host_name} Uso do disco em /srv/Data_pool: {used_percentage}\n\n"
        # print(f"{used_percentage}")
      
        # Salvando os dados em CSV
        csv_filename = host_name+"_uso_disco.csv"
        file_exists = os.path.isfile(csv_filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(csv_filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Data", "Servidor", "Uso%"])
            writer.writerow([timestamp, host_name, used_percentage])
        
        #  print(f"Dados salvos em {csv_filename}")
        
    except Exception as e:
        print(f"Erro ao executar comandos: {e}")
    
    finally:
        client.close()  # Fecha a conexão SSH corretamente
  

if __name__ == "__main__":
####################### DEV #########################################################    
    servidor    = "Desenvolvimento"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.167"  # Substitua pelo IP do servidor    
    usuario = "root"         # Substitua pelo usuário SSH
##    chave_ssh = "C:\\Users\\FelipeGustinelliBort\\Downloads\\bdb Doc\\scripts\\minha_chave.pem"  # Substitua pelo caminho da sua chave privada
    chave_ssh = "minha_chave.pem"  # Substitua pelo caminho da sua chave privada
    porta_ssh = 2222  # Porta do SSH
    
    
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

#######################idaa0004###############################################_D###########

    servidor    = "D3G4_idaa0004"  # Substitua pelo nome do servidor
    servidor_ip = "10.22.214.162"  # Substitua pelo IP do servidor    
    
    
    executar_comandos_remotos(servidor, servidor_ip, usuario, chave_ssh, porta_ssh)     