import os
import telebot
from datetime import datetime
import gspread


gc = gspread.service_account(filename='credenciais.json')
id_planilha = "1U4bDqlzHavIu1stC2B9Sg1nwgY2ZgY-Vr6Ro-ayAJCw"
planilha = gc.open_by_key(id_planilha).sheet1
resumo = gc.open_by_key(id_planilha).worksheet("resumo")


#export TELEGRAM_BOT_TOKEN="token" ou via ~/.bashrc)
chave_api = os.environ.get("TELEGRAM_BOT_TOKEN")
if not chave_api:
    raise RuntimeError(
        "Token não encontrado. Defina a variável de ambiente TELEGRAM_BOT_TOKEN."
    )

bot = telebot.TeleBot(chave_api)


#---- COMANDOS DO BOT ----

def atualizar_resumo():
    registros = planilha.get_all_records()

    dias = {}

    for registro in registros:
        data = registro["Data"]
        hora = registro["Hora"]
        tipo = registro["Tipo"]

        if data not in dias:
            dias[data] = {
                "Entrada": "",
                "Saída Almoço": "",
                "Retorno Almoço": "",
                "Saída": ""
            }

        if tipo in dias[data]:
            dias[data][tipo] = hora

    
    resumo.clear()

    
    resumo.append_row([
        "Data",
        "Entrada",
        "Saída Almoço",
        "Retorno",
        "Saída",
        "Horas Trabalhadas"
    ])

    total_segundos = 0

    for data, pontos in dias.items():

        horas_trabalhadas = ""

        
        if (
            pontos["Entrada"]
            and pontos["Saída Almoço"]
            and pontos["Retorno Almoço"]
            and pontos["Saída"]
        ):
            entrada = datetime.strptime(pontos["Entrada"], "%H:%M:%S")
            almoco_saida = datetime.strptime(
                pontos["Saída Almoço"], "%H:%M:%S"
            )
            almoco_retorno = datetime.strptime(
                pontos["Retorno Almoço"], "%H:%M:%S"
            )
            saida = datetime.strptime(
                pontos["Saída"], "%H:%M:%S"
            )

            periodo_manha = almoco_saida - entrada
            periodo_tarde = saida - almoco_retorno

            total = periodo_manha + periodo_tarde

            total_segundos += total.total_seconds()

            horas_trabalhadas = str(total)

        resumo.append_row([
            data,
            pontos["Entrada"],
            pontos["Saída Almoço"],
            pontos["Retorno Almoço"],
            pontos["Saída"],
            horas_trabalhadas
        ])

    
    horas = int(total_segundos // 3600)
    minutos = int((total_segundos % 3600) // 60)

    resumo.append_row([
        "",
        "",
        "",
        "",
        "TOTAL DO MÊS",
        f"{horas:02d}:{minutos:02d}"
    ])

@bot.message_handler(commands=["start"])
def boas_vindas(mensagem):
    bot.reply_to(
        mensagem,
        "olá! Eu sou o seu bot de pontos.\n"
        "Comandos disponíveis:\n"
        "/entrada\n"
        "/almoco_saida\n"
        "/almoco_retorno\n"
        "/saida\n"
        "/ponto (registro manual/avulso)"
    )


def registrar_evento(mensagem, tipo, rotulo):
    
    try:
        agora = datetime.now()
        data = agora.strftime("%d/%m/%y")
        hora = agora.strftime("%H:%M:%S")

        planilha.append_row([data, hora, tipo])

        atualizar_resumo()

        resposta = f"{rotulo} registrada com sucesso!\n📅 Data: {data}\n⏰ Hora: {hora}"
        bot.reply_to(mensagem, resposta)

    except Exception as e:
        bot.reply_to(mensagem, f"Erro ao salvar na planilha: {e}")


@bot.message_handler(commands=["entrada"])
def registrar_entrada(mensagem):
    registrar_evento(mensagem, "Entrada", "Entrada")


@bot.message_handler(commands=["almoco_saida"])
def registrar_almoco_saida(mensagem):
    registrar_evento(mensagem, "Saída Almoço", "Saída para o almoço")


@bot.message_handler(commands=["almoco_retorno"])
def registrar_almoco_retorno(mensagem):
    registrar_evento(mensagem, "Retorno Almoço", "Retorno do almoço")


@bot.message_handler(commands=["saida"])
def registrar_saida(mensagem):
    registrar_evento(mensagem, "Saída", "Saída")


@bot.message_handler(commands=["ponto"])
def registrar_ponto(mensagem):
    registrar_evento(mensagem, "Manual / Fora do App", "Ponto")


bot.infinity_polling()
