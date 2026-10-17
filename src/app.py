from flask import Flask, render_template

 
app=Flask(__name__)
 
@app.route("/") #decorador o ruta
def index():
    titulo="Pagina de Inicio"
    listado=['Python','Flask','Jinja2','HTML','CSS']
    return render_template("index.html",titulo=titulo,listado=listado)


@app.route("/hola")
def hola():
    return "<h1> hola PWA - IEVN1003</h1>"

#como pasar parametros por url

@app.route("/user/<string:nom>")
def user(nom):
    return "<h1> hola user: {} </h1>".format(nom)
 
@app.route("/numero/<int:n>")
def numero(n):
    return "<h1>Numero: {} </h1>".format(n)

@app.route("/user/<int:id>/<string:username>")
def username(id,username):
    return "<h1>ID: {}, USERNAME {} </h1>".format(id,username)

@app.route("/suma/<float:num1>/<float:num2>")
def suma(num1,num2):
    return "<h1>La suma es: {} </h1>".format(num1+num2)

if __name__=="__main__":
    app.run(debug=True)