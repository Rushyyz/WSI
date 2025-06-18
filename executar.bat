 @echo off



REM Navega até a pasta onde os scripts  estão localizados (se necessário)
cd /d "C:\Users\c1311101\scripts\build\exe.win-amd64-3.11"


@echo off
setlocal

:: =========================================================
:: Script para criar um diretorio com a data atual e mover
:: todos os arquivos que correspondem a *_logs_*.html para la.
:: =========================================================

echo.
echo Iniciando a organizacao dos arquivos de log HTML...

:: Obter a data atual no formato YYYY-MM-DD de forma consistente
:: (funciona independentemente das configuracoes regionais do Windows)
for /f "skip=1 tokens=1-6" %%a in ('wmic path Win32_LocalTime Get Day^,Hour^,Minute^,Month^,Second^,Year /value') do (
    if "%%a" NEQ "" (
        set %%a
    )
)

:: Formatar Mes e Dia com zero a esquerda se necessario
if "%Month:~0,1%"==" " set "Month=0%Month:~1%"
if "%Day:~0,1%"==" " set "Day=0%Day:~1%"

:: Construir a string da data no formato YYYY-MM-DD
set "CURRENT_DATE_FOLDER=%Year%-%Month%-%Day%"

:: Definir o nome do diretório de destino
set "TARGET_DIR=%CURRENT_DATE_FOLDER%_logs_backup"

echo.
echo Criando diretorio: "%TARGET_DIR%"
mkdir "%TARGET_DIR%"

:: Verificar se o diretorio foi criado com sucesso
if not exist "%TARGET_DIR%" (
    echo.
    echo Erro: Nao foi possivel criar o diretorio "%TARGET_DIR%".
    echo Certifique-se de ter permissoes de escrita no diretorio atual.
    pause
    exit /b 1
)

echo.
echo Movendo arquivos *_logs_*.html para "%TARGET_DIR%"...
:: O /Y suprime o prompt para confirmar a sobrescrita de arquivos existentes.
:: Remova o /Y se voce quiser ser perguntado.
move /Y *_logs_*.html "%TARGET_DIR%\"
move /Y *.png "%TARGET_DIR%\"
move /Y *.csv "%TARGET_DIR%\"
move /Y *relatorio*.html "%TARGET_DIR%\"

:: Verificar se a operacao de mover encontrou problemas
:: (Esta e uma verificacao simples; o comando 'move' pode retornar 0 mesmo se
:: alguns arquivos nao forem encontrados, mas eh util para diagnostico basico.)
if exist *_logs_*.html (
    echo.
    echo Aviso: Alguns arquivos *_logs_*.html podem nao ter sido movidos.
    echo Verifique se ha erros na saida acima.
) else (
    echo.
    echo Todos os arquivos *_logs_*.html encontrados foram movidos com sucesso para "%TARGET_DIR%".
)

echo.
echo Operacao de organizacao de logs concluida.
REM pause
REM exit /b 0


REM Executa o primeiro comando  monitor_space
monitor_space.exe --servidor_nome "CEC2C"  --servidor_ip "10.22.214.17" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "HOM-IDAA0002"  --servidor_ip "10.22.199.53" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0001-node01-CEC1B"  --servidor_ip "10.22.236.19" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0002-node01-CEC2B"  --servidor_ip "10.22.214.172" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0003-onZ-D2G1-LP1036"  --servidor_ip "10.22.194.4" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0003-onZ-D3G1-LP1031"  --servidor_ip "10.22.208.7" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0003-onZ-D3G4-LP1032"  --servidor_ip "10.22.208.8" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0003-onZ-D8G1-LP1037"  --servidor_ip "10.22.194.5" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0004-onZ-D0G1-LP2037"  --servidor_ip "10.22.214.167" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0004-onZ-D2G1-LP2036"  --servidor_ip "10.22.214.166" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0004-onZ-D3G1-LP2031"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

monitor_space.exe --servidor_nome "IDAA0004-onZ-D3G4-LP2032"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

REM Executa o segundo comando  grafico 
grafico_uso.exe --servidor_nome "CEC2C"  
grafico_uso.exe --servidor_nome "HOM-IDAA0002"  
grafico_uso.exe --servidor_nome "IDAA0001-node01-CEC1B"  
grafico_uso.exe --servidor_nome "IDAA0002-node01-CEC2B"  
grafico_uso.exe --servidor_nome "IDAA0003-onZ-D2G1-LP1036" 
grafico_uso.exe --servidor_nome "IDAA0003-onZ-D3G1-LP1031" 
grafico_uso.exe --servidor_nome "IDAA0003-onZ-D3G4-LP1032" 
grafico_uso.exe --servidor_nome "IDAA0003-onZ-D8G1-LP1037" 
grafico_uso.exe --servidor_nome "IDAA0004-onZ-D0G1-LP2037" 
grafico_uso.exe --servidor_nome "IDAA0004-onZ-D2G1-LP2036" 
grafico_uso.exe --servidor_nome "IDAA0004-onZ-D3G1-LP2031" 
grafico_uso.exe --servidor_nome "IDAA0004-onZ-D3G4-LP2032"

REM Aguarda 5 segundos antes de abrir o navegador (opcional)
timeout /t 5 >nul

REM Abre uma página da web no Google Chrome
start firefox "file:///C:\Users\c1311101\scripts\build\exe.win-amd64-3.11/espaco_utilizado.html"

REM Executa o segundo comando  SQL
SQL.exe --driver_path "db2jcc4.jar" --jdbc_url "jdbc:db2://GWDB2.BB.COM.BR:50100/BDB2P04" --db_user "X311101" --db_pass "34336914" --jdbc_driver "com.ibm.db2.jcc.DB2Driver"


REM Executa o segundo comando  dwa_error
coletor_logs.exe --servidor_nome "CEC2C"  --servidor_ip "10.22.214.17" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "HOM-IDAA0002"  --servidor_ip "10.22.199.53" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0001-node01-CEC1B"  --servidor_ip "10.22.236.19" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0002-node01-CEC2B"  --servidor_ip "10.22.214.172" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0003-onZ-D2G1-LP1036"  --servidor_ip "10.22.194.4" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0003-onZ-D3G1-LP1031"  --servidor_ip "10.22.208.7" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0003-onZ-D3G4-LP1032"  --servidor_ip "10.22.208.8" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0003-onZ-D8G1-LP1037"  --servidor_ip "10.22.194.5" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0004-onZ-D0G1-LP2037"  --servidor_ip "10.22.214.167" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0004-onZ-D2G1-LP2036"  --servidor_ip "10.22.214.166" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0004-onZ-D3G1-LP2031"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222

coletor_logs.exe --servidor_nome "IDAA0004-onZ-D3G4-LP2032"  --servidor_ip "10.22.214.161" --usuario "root" --chave_ssh "minha_chave.pem" --porta_ssh 2222



REM monitora latencia e le *_LOGS_ e GERA *_LATENCY.CSV

latency_monitor.exe

REM plot_latency_data.exe  LE *_LATENCY.CSV e GERA GRAFICOS e ALERTAS

plot_latency_data.exe
 
