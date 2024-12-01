import base64
from datetime import datetime, timezone, timedelta
import time
from flask import Flask, request, jsonify
import mercadopago
import io
import base64
from PIL import Image
import random
# Inicializar a aplicação Flask
app = Flask(__name__)

# Definir o Access Token diretamente
access_token = 'ACESS_TOKEN'

# Configuração da API do Mercado Pago
mp = mercadopago.SDK(access_token=access_token)
# Rota para gerar o pagamento PIX e o QR Code

current_payment_id = None

@app.route('/')
def hello():
    return "hello world"

@app.route('/checar-pagamento', methods=['GET'])
def checar_pix():
    print("CHECANDO PIX")
    global current_payment_id
    r = mp.payment().get(payment_id=current_payment_id)
    
    print(r)

    try:
        status = r['response']['status']
    except:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao gerar pagamento'
        }), 500
    
    return jsonify({"id":current_payment_id,
        "status":status})

@app.route('/criar-pix', methods=['GET'])
def criar_pix():
    # Dados do pagamento
    product_reference = "debug"

    # Criar um objeto datetime
    dt = datetime.fromtimestamp(time.time() - 60*60*3 + 60*10)
    print(time.time())
    # Definir o fuso horário desejado
    timezone_offset = timedelta(hours=-3)
    tz = timezone(timezone_offset)

    # Converter o datetime para o fuso horário especificado
    dt_with_tz = dt.replace(tzinfo=tz)

    # Formatar no padrão ISO 8601 com milissegundos e fuso horário
    formatted_time = dt_with_tz.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + dt_with_tz.strftime("%z")
    formatted_time = formatted_time[:-2] + ":" + formatted_time[-2:]  # Adiciona o ":" no deslocamento do fuso horário
    print(formatted_time)
    payment_data = {
        "transaction_amount": round(random.uniform(0.01, 0.05),2),  # Valor do pagamento
        "description": "Compra de produto via PIX",
        "payment_method_id": "pix",
        "external_reference": product_reference,
        "date_of_expiration": formatted_time,
        "payer": {
            "email":"jvalecio2@gmail.com",
            #"first_name": "Joao",
            #"last_name": "Alecio"
        }
    }

    # Realiza a criação do pagamento
    payment_response = mp.payment().create(payment_data)

    if payment_response['status'] == 201:
        print(payment_response)
        qr_code_url = payment_response['response']['point_of_interaction']['transaction_data']['ticket_url']
        qr_code = payment_response['response']['point_of_interaction']['transaction_data']['qr_code']
        qr_code_base64 = payment_response['response']['point_of_interaction']['transaction_data']['qr_code_base64']

        print("PAGAMENTO CRIADO")
        print(qr_code_url)

        global current_payment_id
        current_payment_id = payment_response['response']['id']

        
        hexstring = base64.b64decode(qr_code_base64).hex()
        hex_array = [hex(int(hexstring[i:i+2],16)) for i in range(0,len(hexstring), 2)]

        buffer = io.BytesIO()
        imgdata = base64.b64decode(qr_code_base64)
        img = Image.open(io.BytesIO(imgdata))
        new_img = img.resize((240, 240))  # x, y
        new_img.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue())

        qr_code_base64 = str(img_b64)[2:-1] # 240 x 240
        #print(hex_array)
        response = jsonify({
            'qrcode':qr_code,
            'id' : current_payment_id
        })

        return response

    else:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao gerar pagamento'
        }), 500
        

# Rota para o webhook (notificação de pagamento)print(payment_response)
@app.route('/webhook', methods=['POST'])
def webhook():
    print("WEBHOOK RECEBIDO")
    data = request.get_json()
    print(data)

    if data['action'] == 'payment.updated':
        updated_payment_id = data['data']['id']
        print(f"PAGAMENTO ATUALIZADO {updated_payment_id}")
        
        global current_payment_id
        print(f"current: {current_payment_id}")
        print(f"updated: {updated_payment_id}")

        #if(updated_payment_id == current_payment_id):
        print("CHECANDO PAGAMENTO")
        print(int(updated_payment_id) == int(current_payment_id))
        r = mp.payment().get(payment_id=current_payment_id)
        print(r)
        status = r['response']['status']
        print(status)
        if(status == 'approved'):
            print("PAGAMENTO APROVADO")
            return jsonify({'id':current_payment_id,
                            'status': 'approved'}), 200
        

    # Verificar o status do pagamento
    #payment_id = data['data']['id']
    #payment_info = mercadopago.payment.get(payment_id)

    #payment_status = payment_info['response']['status']
    #if payment_status == 'approved':
        # O pagamento foi aprovado
    #    print(f'Pagamento aprovado! ID: {payment_id}')
    #    return jsonify({'status': 'Pagamento aprovado'}), 200
    #else:
     #   print(f'Pagamento não aprovado. Status: {payment_status}')
    #    return jsonify({'status': 'Pagamento não aprovado'}), 200
    return "200"

def dbg():
    while(1):
        dt = datetime.fromtimestamp(time.time()+30)
        print(dt)
        # Definir o fuso horário desejado
        timezone_offset = timedelta(hours=-0)
        tz = timezone(timezone_offset)

        # Converter o datetime para o fuso horário especificado
        dt_with_tz = dt.replace(tzinfo=tz)

        # Formatar no padrão ISO 8601 com milissegundos e fuso horário
        formatted_time = dt_with_tz.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] #+ dt_with_tz.strftime("%z")
        #formatted_time = formatted_time[:-2] + ":" + formatted_time[-2:]  # Adiciona o ":" no deslocamento do fuso horário
        print(formatted_time)
        time.sleep(3)

if __name__ == '__main__':
    # Rodar o servidor Flask na porta 5000
    app.run(host="0.0.0.0", port=5000, ssl_context='adhoc',debug=True)
    #r = test_mp()
    #print(r)
     # Criar um objeto datetime
    

    #2022-11-17T09:37:52.000-04:00.
    #2024-11-24T15:14:32.632-03:00