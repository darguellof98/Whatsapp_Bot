## funcion de cargar registros a la db

def ejecutar_query (query):
    
    # Creo la conexion
   
    import pandas as pd
    import pyodbc
    con_str = pyodbc.connect("""
    Driver={ODBC Driver 18 for SQL Server};
    Server=tcp:{azure_server};
    Database={data_base_name};
    Uid={user};
    Pwd={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
    """)
    # Creo mi cursosr en SQL
    cursor = con_str.cursor()
    cursor.execute(query)
    con_str.commit()
    cursor.close()
    con_str.close()
    return ('Ejecutado correctamente')

def crear_conexion ():
    from sqlalchemy import create_engine
    server = 'azure_server'
    database = 'data_base_name'
    username = 'user'
    password = 'pws'
    port = 1433
    driver= 'ODBC Driver 18 for SQL Server'
    connection_string = f"mssql+pyodbc://{username}:{password}@{server}:{port}/{database}?driver={driver}"
    # Creo mi motor con sqlalchemy
    engine = create_engine(connection_string)
    return(engine)

def descargar_datos():
    import pandas as pd
    import numpy as np
    query = (f"""SELECT * FROM dbo.presupuesto_bot """)
    df_balance = pd.read_sql_query(query, con = crear_conexion())
    df_balance['NETO'] = np.where(df_balance['DESCRIPCION'].isin(['sueldo','rol']), df_balance['MONTO'], -df_balance['MONTO'])
    df_balance['FECHA_CONSUMO'] = pd.to_datetime(df_balance['FECHA_CONSUMO'])
    df_balance['PERIODO'] = df_balance['FECHA_CONSUMO'].dt.to_period('M')

    return(df_balance)

def consumos_mes():
    df_balance = descargar_datos()
    df_mes = df_balance[(df_balance['PERIODO'] == df_balance['PERIODO'].max()) & (~df_balance['DESCRIPCION'].isin(['sueldo','rol']))]
    consumos = round((df_mes['MONTO'].sum()),2)
    return(consumos)

def balance():
    df_balance = descargar_datos()
    balance = round((df_balance[df_balance['PERIODO'] == df_balance['PERIODO'].max()]['NETO'].sum()),2)
    return(balance)

def avisar_otro(destinatario, monto, desc, tipo):
    from twilio.rest import Client
    account_sid = 'ssid_'
    auth_token = 'token'
    client = Client(account_sid, auth_token)
    if tipo == 'consumo':
        message = client.messages.create(
        from_='whatsapp:+twilio_number',
        body = f'Se ha hecho un consumo de $:{monto} en {desc}',
        to= {destinatario}
        )
    else: 
        message = client.messages.create(
        from_='whatsapp:+twilio_number',
        body = f'Se ha acreditado de $:{monto} de {desc}',
        to = {destinatario}
        )
    return('Notificacion lista')


def respuesta_registro(mensaje_completo, dic_numeros, from_msg, dic_destinatrios):
    monto = mensaje_completo[1]
    tipo_pago = mensaje_completo[2]
    descripcion = mensaje_completo[3]
    query = (f""" INSERT INTO dbo.presupuesto_bot VALUES(GETDATE(), '{dic_numeros[from_msg]}', {monto}, '{tipo_pago}', '{descripcion}')""")
    ejecutar_query(query)
    if descripcion in (['sueldo', 'rol']):
        valor_balance = balance()
        respuesta =(f"""Cargado correctamente la transaccion, balance: ${valor_balance}""")
        avisar_otro(destinatario = dic_destinatrios[from_msg], 
                    monto = monto,
                    desc = descripcion, 
                    tipo = 'acreditacion')
        
    else:
        consumos = consumos_mes()
        valor_balance = balance()
        respuesta =(f"""Cargado correctamente el consumo, consumos totales mes: ${consumos}, balance: ${valor_balance}""")
        avisar_otro(destinatario = dic_destinatrios[from_msg], 
                    monto = monto,
                    desc = descripcion, 
                    tipo = 'consumo')

    return(respuesta)

def avisar_otro(destinatario, monto, desc, tipo):
    from twilio.rest import Client
    account_sid = 'ssid_'
    auth_token = 'token'
    client = Client(account_sid, auth_token)
    if tipo == 'consumo':
        message = client.messages.create(
        from_='whatsapp:+twilio_number',
        body = f'Se ha hecho un consumo de $:{monto} en {desc}',
        to= {destinatario}
        )
    else: 
        message = client.messages.create(
        from_='whatsapp:+twilio_number',
        body = f'Se ha acreditado de $:{monto} en {desc}',
        to = {destinatario}
        )
    return('Notificacion lista')
