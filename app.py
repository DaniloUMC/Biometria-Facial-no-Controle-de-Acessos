from flask import Flask
from controllers.usuario_controller import usuario_bp
import os

app = Flask(__name__, template_folder="views", static_folder="static")


app.secret_key = os.urandom(24)
app.secret_key = "chave_super_secreta"
app.register_blueprint(usuario_bp)


if __name__ == "__main__":
    app.run(debug=True)