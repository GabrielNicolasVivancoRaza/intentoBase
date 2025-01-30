from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Configuración de conexión a MongoDB
mongo_uri = "mongodb+srv://ldmoran:ldmoran@cluster0.tbsel.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri)
db = client['amazon']
users_collection = db['usuarios']

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar el login
@app.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    email = login_data.get('email')
    password = login_data.get('password')

    # Buscar el usuario en la base de datos
    user = users_collection.find_one({"email": email})
    if user and user['password'] == password:
        return jsonify({"message": "Login exitoso", "name": user["name"]}), 200
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401

# Ruta para la página de inicio
@app.route('/inicio', methods=['GET'])
def inicio():
    return render_template('inicio.html')

# Ruta para servir la página de registro
@app.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

# Ruta para manejar el registro de usuarios
@app.route('/register', methods=['POST'])
def register():
    user_data = request.get_json()
    email = user_data.get('email')
    password = user_data.get('password')
    name = user_data.get('name')
    cedula = user_data.get('cedula')  # Recibir cédula del usuario

    # Verificar si el email ya existe
    if users_collection.find_one({"email": email}):
        return jsonify({"message": "El correo ya está registrado"}), 400

    # Verificar si la cédula ya está registrada
    if users_collection.find_one({"cedula": cedula}):
        return jsonify({"message": "La cédula ya está registrada"}), 400

    # Insertar nuevo usuario
    new_user = {
        "email": email,
        "password": password,
        "name": name,
        "cedula": cedula  # Almacenar la cédula
    }
    users_collection.insert_one(new_user)
    return jsonify({"message": "Registro exitoso"}), 201

# Ruta para manejar la compra
@app.route('/comprar', methods=['POST'])
def comprar():
    try:
        data = request.get_json()  # Obtener los datos enviados desde el frontend
        print("Received data:", data)  # Para ver los datos que llegan
        
        cedula = data.get('cedula')  # Obtener la cédula del usuario
        products = data.get('products')  # Obtener los productos
        total = data.get('total')  # Obtener el total
        address = data.get('address')  # Obtener la dirección

        # Verificar que los datos necesarios estén completos
        if not cedula or not products or not total or not address:
            print("Missing required data")  # Log de error
            return jsonify({"message": "Missing required data"}), 400

        # Buscar el usuario por cédula
        user = users_collection.find_one({"cedula": cedula})
        if not user:
            print("User not found")  # Log de error
            return jsonify({"message": "User not found"}), 404

        # Almacenar la compra, con los nombres de los productos
        updated_data = {
            "$push": {
                "purchases": {
                    "products": products,  # Lista de productos (con nombres)
                    "total": total,  # Total de la compra
                    "address": address  # Dirección de envío
                }
            },
            "$inc": {"total_spent": total}  # Aumentar el total gastado
        }

        # Actualizar los datos en la base de datos
        users_collection.update_one({"cedula": cedula}, updated_data)
        print("Purchase processed successfully")  # Log de éxito

        return jsonify({"message": "Compra realizada con éxito"}), 200
    
    except Exception as e:
        print(f"Error during payment processing: {e}")  # Log del error
        return jsonify({"message": "Error in processing the payment"}), 500




if __name__ == '__main__':
    app.run(debug=True)

