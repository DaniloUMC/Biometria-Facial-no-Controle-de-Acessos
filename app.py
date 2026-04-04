from flask import Flask
from controllers.usuario_controller import usuario_bp
import os

# Inicialização do app
app = Flask(__name__, template_folder="views", static_folder="static")

# 🔐 Chave secreta para sessão (obrigatória)
app.secret_key = os.urandom(24)

# Registro das rotas (Blueprint)
app.register_blueprint(usuario_bp)

# Execução
if __name__ == "__main__":
    app.run(debug=True)