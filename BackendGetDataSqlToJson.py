#######07112018 - Criado por Rodrigo Castro
#modulo para ler ini
import configparser
#modulo para acessar banco de dados
import pyodbc
#modulo para Json
import json
#modulo para date
import datetime
#modulo para .env
import os
from dotenv import load_dotenv
project_folder = os.path.expanduser('.')
load_dotenv(os.path.join(project_folder, '.env'))

server = os.getenv("server")
user = os.getenv("user")
password = os.getenv("password")
dirHtdocs = os.getenv("dirHtdocs")

#Funcao para pegar dados no sql server, recebe o servidor e a consulta e retorna o resultado
def consulta(servidor,consulta):
	connection = pyodbc.connect("Driver={SQL Server};" "Server="  +  servidor   +  ";" "Database=;" "uid=" +user+";" "pwd="+password+";",timeout=3)
	cursor = connection.cursor()
	SQLCommand = (consulta)
	try:
		cursor.execute(SQLCommand)
		results = cursor.fetchone()
		return results[0]
		cursor.close()
	except:
		return "Erro"
def verificacritico(midias,liberado):
        if midias != "Erro":
                if midias >= 2 or liberado > 1000:
                        return "X"
                else:
                        return " "
              
def verificahds(midias,liberado):
                if midias != "Erro":
                        if midias == 0 and liberado > 1000:
                                return "X"
                        else:
                                return " "



#Variavel para data
now = datetime.datetime.now()
#inicia o dicionario
unidades = []
midias = []
liberadossembackup = []
critico = []
verificahd = []
numeromidias = []
#pega as configs do INI
parser = configparser.ConfigParser()
parser.read('confign.ini')
for section_name in parser.sections():
	for name, value in parser.items(section_name):
		#separa o valor por ;
		a = value.split(';')
		unidades.append(a[0])
		#pega o segundo parametro do ini
		linked=a[1]
		#consulta das midias pendentes
		consmidias = "SELECT count(Cd_N) [Cd_N] FROM " +linked+".RIS.dbo.Hist_CD where CD_gravado = 0 and ISO_gravado = 0 and Size_Of_Cd > 0" 
		consliberadosembackup = "SELECT COUNT(id_atend) AS Valor FROM " +linked+".RIS.dbo.Atendimento AS A WITH (nolock) WHERE (id_status = 4) AND (N_CD IS NULL) AND(id_atend = id_atend_acesso) AND EXISTS (SELECT AccessionN FROM " +linked+".DICOM.dbo.DICOMStudies AS E WITH (nolock) WHERE(AccessionN = A.id_atend_acesso))"
		consnumerosmidias = "DECLARE @cd varchar(300) SELECT  @cd = COALESCE(@cd + ' ', '') + cast([Cd_n] as varchar) FROM  " +linked+".RIS.dbo.Hist_CD with (nolock) where ISO_gravado = '0' and CD_gravado ='0' and Size_Of_Cd > '0' SELECT @cd"
		print("Buscando dados de: " + a[0])
		midiass = consulta(server,consmidias)
		liberadossembackupp = consulta(server,consliberadosembackup)
		numeromidiass = consulta(server,consnumerosmidias)
		midias.append(midiass)
		numeromidias.append(numeromidiass)
		liberadossembackup.append(liberadossembackupp)
		critico.append(verificacritico(midiass,liberadossembackupp))
		verificahd.append(verificahds(midiass,liberadossembackupp))
arrumar = []
#loop para pegar dos arrays e colocar na lista
#while i < len(unidades):
for i in range(len(unidades)):
	arrumar.append({
		"unidade" : unidades[i],
		"midiaspendentes" : str(midias[i]),
		"liberadosSemBackup": str(liberadossembackup[i]),
		"critico": str(critico[i]),
		"verificarhd": str(verificahd[i]),
		"midias": str(numeromidias[i])
	})
#Arruma no formato JSON
json.dumps(arrumar)
#grava o arquivo JSON
with open(dirHtdocs + '\data.json', 'w') as outfile:  
	json.dump(arrumar, outfile)

dataexecucao = now.strftime("%d/%m/%Y as %H:%M")
with open(dirHtdocs + '\exec.txt', 'w') as arquivo:
	arquivo.write(dataexecucao)
print("Termino!")