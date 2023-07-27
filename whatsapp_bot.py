from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request, redirect
from funciones import ejecutar_query, crear_conexion
import funciones as fn
import pandas as pd
import numpy as np




app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Start our TwiML response
    resp = MessagingResponse()
    incoming_msg = request.values.get('Body', '').lower()
    from_msg = request.values.get('From', '').lower()
    dic_numeros = {'whatsapp:+mi_numero':'David',
                   'whatsapp:+numero_novia':'novia'}
    dic_destinatrios = {'whatsapp:+mi_numero':'whatsapp:+numero_novia',
                        'whatsapp:+numero_novia': 'whatsapp:+mi_numero'}
    mensaje_completo = incoming_msg.split(', ')



    if mensaje_completo[0] == 'registro':        
        respuesta = fn.respuesta_registro(mensaje_completo = mensaje_completo,
                                          dic_numeros = dic_numeros,
                                          from_msg = from_msg,
                                          dic_destinatrios = dic_destinatrios,
                                          )
        
        resp.message(respuesta)


    elif mensaje_completo[0] == 'consulta':
        tipo = mensaje_completo[1]
        if tipo == 'consumos_mes':
            respusta = (f'Consumos del mes: ${fn.consumos_mes}')
        elif tipo == 'balance':
            respusta = (f'Balance: ${fn.balance}')
        resp.message(respuesta)
                
    else:
        # Add a message
        resp.message(f"Solo tengo 3 funciones, registro de transacciones, consulta de remanente o tutorial")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=80)