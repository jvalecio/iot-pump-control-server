from flask import Flask, request, jsonify
import mercadopago
import test

# Inicializar a aplicação Flask
app = Flask(__name__)

# Definir o Access Token diretamente
access_token = 'APP_USR-3462435005013774-110709-b9a599644005b02e56acc83bfe5a11ec-1107138723'  # Substitua pelo seu Access Token

# Configuração da API do Mercado Pago
mp = mercadopago.SDK(access_token=access_token)
# Rota para gerar o pagamento PIX e o QR Code
@app.route('/criar-pix', methods=['GET'])
def criar_pix():
    # Dados do pagamento
    product_reference = debug

    payment_data = {
        "transaction_amount": 1.0,  # Valor do pagamento
        "description": "Compra de produto via PIX",
        "payment_method_id": "pix",
        "external_reference": "product_reference",
        "payer": {
            "email":"jvalecio2@gmail.com",
            #"first_name": "Joao",
            #"last_name": "Alecio"
        }
    }

    # Realiza a criação do pagamento
    payment_response = mp.payment().create(payment_data)

    
    print(payment_response['response']['external_reference'])
    return payment_response
    

    if payment_response['status'] == 201:
        # Se o pagamento foi criado com sucesso, extrai o QR Code
        qr_code_url = payment_response['response']['point_of_interaction']['transaction_data']['qr_code']
        return jsonify({
            'status': 'success',
            'qrCodeUrl': qr_code_url
        }), 201
    else:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao gerar pagamento'
        }), 500

# Rota para o webhook (notificação de pagamento)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Verificar o status do pagamento
    payment_id = data['data']['id']
    payment_info = mercadopago.payment.get(payment_id)

    payment_status = payment_info['response']['status']
    if payment_status == 'approved':
        # O pagamento foi aprovado
        print(f'Pagamento aprovado! ID: {payment_id}')
        return jsonify({'status': 'Pagamento aprovado'}), 200
    else:
        print(f'Pagamento não aprovado. Status: {payment_status}')
        return jsonify({'status': 'Pagamento não aprovado'}), 200

def test_mp():
    # Dados do pagamento
    payment_data = {
        "transaction_amount": 1.0,  # Valor do pagamento
        "description": "Compra de produto via PIX",
        "payment_method_id": "pix",
        "payer": {
            "email":"jvalecio2@gmail.com",
            #"first_name": "Joao",
            #"last_name": "Alecio"
        }
    }

    # Realiza a criação do pagamento
    payment_response = mp.payment().create(payment_data)
    return payment_response
    """
    if payment_response['status'] == 201:
        # Se o pagamento foi criado com sucesso, extrai o QR Code
        qr_code_url = payment_response['response']['point_of_interaction']['transaction_data']['qr_code']
        return jsonify({
            'status': 'success',
            'qrCodeUrl': qr_code_url
        }), 201
    else:
        return jsonify({
            'status': 'error',
            'message': 'Erro ao gerar pagamento'
        }), 500

    """

if __name__ == '__main__':
    # Rodar o servidor Flask na porta 5000
    app.run(host='0.0.0.0', port=5000)
    #r = test_mp()
    #print(r)
