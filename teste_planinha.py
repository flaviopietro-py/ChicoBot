import gspread

# 1. Conecta usando as credenciais do arquivo JSON
gc = gspread.service_account(filename='credenciais.json')

# 2. Abre a planilha pelo NOME exato que você deu a ela no Google Drive
planilha = gc.open("Registro de Ponto").sheet1

# 3. Adiciona uma linha de teste com [Data, Hora, Tipo]
planilha.append_row(["12/08/2026", "08:00:00", "Entrada - Teste"])

print("✅ Linha adicionada com sucesso no Google Sheets!")