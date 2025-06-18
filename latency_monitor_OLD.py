import paramiko
import datetime
import re
import pandas as pd
import argparse
import os
import csv
import socket

def extract_and_save_latency_data(host_name, host, user, key_file, port=2222):
    """
    Connects via SSH, extracts detailed latency information from hardwareEventLog.bin,
    and saves it to a CSV file.
    """
    client = None
    try:
        if not os.path.isfile(key_file):
            print(f"Error: SSH key file '{key_file}' not found.")
            print("Please verify the path and permissions of the file.")
            return

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Attempting to connect to {host_name} ({host}:{port}) as {user}...")
        client.connect(hostname=host, username=user, key_filename=key_file, port=port)
        print("SSH connection established successfully.")

        # --- NOVA MODIFICAÇÃO CHAVE AQUI: GREP MENOS RESTRITIVO, MAS AINDA EFICIENTE ---
        # Garantimos que as linhas que contêm o início/fim do bloco de log e as palavras-chave essenciais
        # sejam incluídas, deixando o regex Python fazer o trabalho de montar o bloco.
        command = (
            "strings /opt/ibm/appliance/storage/head/dwa/var/server/event_log/hardwareEventLog.bin | "
            "grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}|Latency|Originator: MonitoringEventCreatorThread|Subscription:'"
        )
        print(f"Executing remote command: {command}...")
        
        stdin, stdout, stderr = client.exec_command(command)

        channel = stdout.channel
        read_timeout_seconds = 300 # 5 minutos. Pode ser aumentado se a rede for muito lenta.
        channel.settimeout(read_timeout_seconds)

        raw_log_output = ""
        error_msg = ""
        try:
            raw_log_output = stdout.read().decode('utf-8', errors='ignore').strip()
            print(f"DEBUG: Read {len(raw_log_output)} characters from stdout.")
        except socket.timeout:
            print(f"WARNING: Reading stdout from remote command for {host_name} timed out after {read_timeout_seconds} seconds.")
            raw_log_output = ""
        except Exception as e:
            print(f"ERROR: Unexpected error reading stdout for {host_name}: {e}")
            raw_log_output = ""

        channel.settimeout(None)
        error_msg = stderr.read().decode('utf-8', errors='ignore').strip()

        exit_status = channel.recv_exit_status()
        print(f"DEBUG: Remote command exit status: {exit_status}")

        if error_msg:
            print(f"ERROR (stderr) executing command on {host_name}: {error_msg}")
            if exit_status != 0 and not raw_log_output:
                print(f"Command '{command}' failed on remote host with exit status {exit_status}.")
                return

        if not raw_log_output:
            print(f"No output from command '{command}' for {host_name}. This might mean no relevant logs were found or grep filtered too much, or the command failed to produce output.")
            return

        # 4. Process output to extract all required fields using a single comprehensive regex
        # A regex Python original permanece a mesma, pois agora ela terá menos dados para processar.
        data_records = []
        
        combined_log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*(?:\r?\n|\s+)'
            r'.*?Id: \d+\s*'
            r'Subscription:\s*(?P<subscription>.*?)(?:_20\d{2}| Message:|$)\s*'
            r'Message:\s*.*?Latency\s*(?P<latency>\d+)\s*seconds\.\s*'
            r'Latest commit RBA/LRSN\s*(?P<latest_commit_lrsn>0x[0-9A-Fa-f]+)\.\s*'
            r'Number of open transactions\s*(?P<open_transactions>\d+),\s*'
            r'earliest open RBA/LRSN\s*(?P<earliest_open_lrsn>0x[0-9A-Fa-f]+)\.\s*'
            r'(?:Parsed source operations:\s*(?P<parsed_insert>\d+)\s*insert,\s*'
            r'(?P<parsed_update>\d+)\s*update,\s*'
            r'(?P<parsed_delete>\d+)\s*delete\.\s*)?'
            r'(?:Applied target operations:\s*(?P<applied_insert>\d+)\s*insert,\s*'
            r'(?P<applied_delete>\d+)\s*delete\.\s*)?'
            r'Originator: MonitoringEventCreatorThread',
            flags=re.IGNORECASE | re.DOTALL
        )
        
        for match in combined_log_pattern.finditer(raw_log_output):
            try:
                timestamp_str = match.group('timestamp')
                subscription = match.group('subscription').strip()
                latency = int(match.group('latency'))
                latest_commit_lrsn = match.group('latest_commit_lrsn')
                open_transactions = int(match.group('open_transactions'))
                earliest_open_lrsn = match.group('earliest_open_lrsn')
                
                parsed_insert = int(match.group('parsed_insert')) if match.group('parsed_insert') else 0
                parsed_update = int(match.group('parsed_update')) if match.group('parsed_update') else 0
                parsed_delete = int(match.group('parsed_delete')) if match.group('parsed_delete') else 0
                applied_insert = int(match.group('applied_insert')) if match.group('applied_insert') else 0
                applied_delete = int(match.group('applied_delete')) if match.group('applied_delete') else 0

                event_time = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                data_records.append({
                    "Timestamp": event_time,
                    "Subscription": subscription,
                    "Latency_Seconds": latency,
                    "Latest_Commit_LRSN_Hex": latest_commit_lrsn,
                    "Number_Open_Transactions": open_transactions,
                    "Earliest_Open_LRSN_Hex": earliest_open_lrsn,
                    "Parsed_Insert": parsed_insert,
                    "Parsed_Update": parsed_update,
                    "Parsed_Delete": parsed_delete,
                    "Applied_Insert": applied_insert,
                    "Applied_Delete": applied_delete,
                    "Host_Name": host_name
                })
            except ValueError as ve:
                print(f"Warning: Error converting data in a matched log entry: {ve}")
            except AttributeError as ae:
                print(f"Warning: Could not extract all expected groups from a matched log entry: {ae}")

        if not data_records:
            print(f"No relevant latency/transaction data found in the filtered log output for {host_name}.")
            print("This could mean the grep command was too restrictive or no matching logs exist.")
            return

        df = pd.DataFrame(data_records)
        df.sort_values(by="Timestamp", inplace=True)

        safe_host_name = host_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        csv_filename = f"{safe_host_name}_detailed_latency_data.csv"
        
        file_exists = os.path.isfile(csv_filename)
        df.to_csv(csv_filename, mode='a', header=not file_exists, index=False, encoding='utf-8')
        print(f"Detailed latency data saved to '{csv_filename}'")

    except paramiko.AuthenticationException:
        print(f"Authentication error for {host_name} ({host}). Please check user and SSH key.")
    except paramiko.SSHException as ssh_err:
        print(f"SSH error for {host_name} ({host}): {ssh_err}")
    except Exception as e:
        print(f"Unexpected error connecting, processing, or saving data for {host_name} ({host}): {e}")

    finally:
        if client:
            client.close()
            print(f"SSH connection to {host_name} closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extracts detailed latency and transaction data from SSH logs and saves to CSV."
    )

    parser.add_argument(
        "--servidor_nome",
        type=str,
        required=True,
        help="Name of the server for SSH connection (e.g., my_web_server)"
    )
    parser.add_argument(
        "--servidor_ip",
        type=str,
        required=True,
        help="SSH server IP address"
    )
    parser.add_argument(
        "--usuario",
        type=str,
        required=True,
        help="Username for SSH connection"
    )
    parser.add_argument(
        "--chave_ssh",
        type=str,
        required=True,
        help="Full path to the private SSH key file (OpenSSH/Paramiko format)"
    )
    parser.add_argument(
        "--porta_ssh",
        type=int,
        default=2222,
        help="SSH port number (default: 2222)"
    )

    args = parser.parse_args()

    extract_and_save_latency_data(
        args.servidor_nome,
        args.servidor_ip,
        args.usuario,
        args.chave_ssh,
        args.porta_ssh
    )
