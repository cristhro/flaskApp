from datetime import datetime
from os import environ
from flask import Flask, jsonify, request, render_template, make_response
from time import time
from pymongo import MongoClient
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn import svm
import pandas as pd
import numpy as np
from collections import Counter

import cPickle 


MONGODB_URI = "mongodb://admin:admin@ds159050.mlab.com:59050/flaskdb"
client = MongoClient(MONGODB_URI)
db = client.get_default_database()

doc_palabras = db.palabras
doc_usuarios = db.doc_usuarios
doc_features = db.features_train_1
doc_features_test = db.features_test

app = Flask(__name__)


@app.route('/')
@app.route('/home')

def home():
    return render_template(
        'index.html',
        title='App',
        message='autentication',
    )

@app.route('/entrenamiento')
def entrenamiento():
    usuario = 'Jesus'
    numPalabra = 0
    palabra = doc_palabras.find_one({'numPalabra': numPalabra})
    numTotalPalabras = doc_palabras.count()
    fin = False

    return render_template(
        'entrenamiento.html',
        title='Entrenamiento',
        year=datetime.now().year,
        message='Teclea las palabras que te aparezcan',
        usuario=usuario,
        palabra=palabra['palabra'],
        t0=time(),
        t0_palabra=time(),
        tiempoPalabra=0,
        tiempo=0,
        numPalabra=numPalabra,
        numTotalPalabras=numTotalPalabras,
        falloCaracter=False,
        hayErrPalabra=False,
        tiempoErrPalabra=0,
        t0_error=0,
        fin=fin,

    )

@app.route('/autenticacion',methods = ["GET", "POST"])
def autenticacion():

    palabraLeida = ""
    palabra = "ZANAHORIA"
    t0 = time()
    tiempo = 0
    t0_error = 0
    tiempoErrPalabra = 0
    t0_palabra = time()
    tiempoPalabra = 0
    hayErrPalabra = False
    fin = False
    usuario = "Jesus"

    if request.method == 'POST':
        palabraLeida = request.form['palabraLeida']
        tiempo = str(time() - float(request.form['t0']))
        t0_error = float(request.form['t0_error'])
        t0_palabra = float(request.form['t0_palabra'])

        if (mismaPalabra(palabra, palabraLeida)):
                fin = True
                if  (t0_error != 0):
                    tiempoErrPalabra = str(time() - t0_error)
                t0_error = 0
                tiempoPalabra = str(time() - t0_palabra)
                t0_palabra = time()

                # Si es correcta la palabra #####################################################################
                realizar_prediccion()
                #################################################################################################
        else:
            if  (t0_error != 0):
                tiempoErrPalabra = time() - t0_error
                tiempoErrPalabra = tiempoErrPalabra + (time() - t0_error)

            t0_error = time()
            hayErrPalabra = True


    return render_template(
        'autenticacion.html',
        title='Autenticacion',
        year=datetime.now().year,
        message='Teclea la palabra para autenticarte',
        palabra= palabra,
        usuario=usuario,
        t0=t0,
        tiempo=0,
        falloCaracter=False,
        hayErrPalabra=hayErrPalabra,
        tiempoErrPalabra=tiempoErrPalabra,
        t0_error=t0_error,
        t0_palabra=t0_palabra,
        tiempoPalabra=tiempoPalabra,
        fin=fin)

@app.route('/getCaracter', methods=['POST'])
def getCaracter():
    usuario = request.form['usuario']
    palabra = request.form['palabra']
    palabraLeida = request.form['palabraLeida']
    tiempo = str(time() - float(request.form['t0']))
    ultimoCaracter = ""
    falloCaracter = False
    tiempoErrPalabra = 0
    numPalabra = 0
    tiempoPalabra = 0
    numTotalPalabras = 0


    objeto = {
        'usuario': usuario,
        'palabra': palabra,
        'palabraLeida': palabraLeida,
        'tiempo': tiempo,
        'hayErrPalabra': False,
        'tiempoErrPalabra': tiempoErrPalabra,
        'numPalabra': numPalabra,
        'numTotalPalabras': numTotalPalabras,
        'tiempoPalabra':tiempoPalabra,
        'tamPalabra': len(palabra),
        'caracter': '',
        'falloCaracter': False,
        't0': 0,
        'palabraCorrecta' : False
    }

    if not (isValidoUltimoCaracter(palabra, palabraLeida)):
        falloCaracter = True
        objeto['falloCaracter'] = True
        ultimoCaracter = palabraLeida[len(palabraLeida) - 1]
        objeto['caracter'] = ultimoCaracter

    else:
        ultimoCaracter = palabraLeida[len(palabraLeida) - 1]
        objeto['caracter'] = ultimoCaracter
        objeto['falloCaracter'] = False

    doc_features.insert(objeto)

    return jsonify({
        'usuario': usuario,
        'palabra': palabra,
        'palabraLeida': palabraLeida,
        'tiempo': tiempo,
        'caracter': ultimoCaracter,
        'falloCaracter': falloCaracter,
        't0': time(),
        'tiempo': tiempo,
        'hayErrPalabra': False,
        'tiempoErrPalabra': 0,
        't0_error': time(),

    })

@app.route('/getCaracterLogin', methods=['POST'])
def getCaracterLogin():
    palabra = request.form['palabra']
    palabraLeida = request.form['palabraLeida']
    tiempo = str(time() - float(request.form['t0']))
    ultimoCaracter = ""
    falloCaracter = False
    tiempoErrPalabra = 0
    tiempoPalabra = 0


    objeto = {
        'palabra': palabra,
        'palabraLeida': palabraLeida,
        'tiempo': tiempo,
        'hayErrPalabra': False,
        'tiempoErrPalabra': tiempoErrPalabra,
        'tiempoPalabra':tiempoPalabra,
        'tamPalabra': len(palabra),
        'caracter': '',
        'falloCaracter': False,
        't0': 0,
        'palabraCorrecta' : False
    }

    if not (isValidoUltimoCaracter(palabra, palabraLeida)):
        falloCaracter = True
        objeto['falloCaracter'] = True
        ultimoCaracter = palabraLeida[len(palabraLeida) - 1]
        objeto['caracter'] = ultimoCaracter

    else:
        ultimoCaracter = palabraLeida[len(palabraLeida) - 1]
        objeto['caracter'] = ultimoCaracter
        objeto['falloCaracter'] = False

    doc_features_test.insert(objeto)

    return jsonify({
        'palabra': palabra,
        'palabraLeida': palabraLeida,
        'tiempo': tiempo,
        'caracter': ultimoCaracter,
        'falloCaracter': falloCaracter,
        't0': time(),
        'tiempo': tiempo,
        'hayErrPalabra': False,
        'tiempoErrPalabra': 0,
        't0_error': time(),

    })

@app.route('/siguiente_palabra', methods=['POST'])
def siguiente_palabra():
    objeto = {}
    numPalabra = int(request.form['numPalabra'])
    numTotalPalabras = request.form['numTotalPalabras']
    usuario = request.form['usuario']
    palabras = doc_palabras.find()
    docPalabra = doc_palabras.find_one({'numPalabra': int(numPalabra)})
    palabra = docPalabra['palabra']
    nuevaPalabra = ""
    palabraLeida = request.form['palabraLeida']
    tiempo = str(time() - float(request.form['t0']))
    t0_error = float(request.form['t0_error'])
    tiempoErrPalabra = 0
    t0_palabra = float(request.form['t0_palabra'])
    tiempoPalabra = 0
    hayErrPalabra = False
    fin = False
    palabraCorrecta = False

    if(int(numPalabra) == (int(numTotalPalabras) - 1)):
        fin = True
    else :
        docNuevaPalabra = doc_palabras.find_one({'numPalabra': int(numPalabra) + 1})
        nuevaPalabra  = docNuevaPalabra["palabra"]
        if (mismaPalabra(palabra, palabraLeida)):

            if  (t0_error != 0):
                tiempoErrPalabra = str(time() - t0_error)
            
            palabraCorrecta = True
            t0_error = 0
            tiempoPalabra = str(time() - t0_palabra)
            t0_palabra = time()
            numPalabra = int(numPalabra) + 1
        else:
            if  (t0_error != 0):
                tiempoErrPalabra = time() - t0_error
                tiempoErrPalabra = tiempoErrPalabra + (time() - t0_error)

            t0_error = time()
            hayErrPalabra = True
            nuevaPalabra = palabra
    # Guardamos el ojeto en la BD
    doc_features.insert({
                'usuario': usuario,
                'palabra': palabra,
                'palabraLeida': palabraLeida,
                'tiempo': tiempo,
                'hayErrPalabra': hayErrPalabra,
                'tiempoErrPalabra': tiempoErrPalabra,
                'numPalabra': numPalabra,
                'numTotalPalabras': numTotalPalabras,
                'tiempoPalabra':tiempoPalabra,
                'tamPalabra': len(palabra),
                'caracter': '',
                'falloCaracter': False,
                't0': 0,
                'palabraCorrecta' : palabraCorrecta
            })

    # Realizamos el entrenamiento
    realizar_entrenamiento()

    return render_template(
        'entrenamiento.html',
        title='Entrenamiento',
        year=datetime.now().year,
        message='Teclea las palabras que te aparezcan',
        usuario=usuario,
        palabra=nuevaPalabra,
        t0=time(),
        tiempo=0,
        numPalabra=numPalabra,
        numTotalPalabras=numTotalPalabras,
        falloCaracter=False,
        hayErrPalabra=hayErrPalabra,
        tiempoErrPalabra=tiempoErrPalabra,
        t0_error=t0_error,
        t0_palabra=t0_palabra,
        tiempoPalabra=tiempoPalabra,
        fin=fin)

def isValidoUltimoCaracter(palabra, palabraLeida):
    if(len(palabraLeida) <= len(palabra) and len(palabraLeida) > 0):
        if(palabra[len(palabraLeida) - 1] == palabraLeida[len(palabraLeida) - 1]):
            return True
        else:
            return False
    else:
        return False

def mismaPalabra(palabra, palabraLeida):
    if(palabra == palabraLeida):
        return True
    else:
        return False

def insertatPalabras(doc):
    doc.insert({'numPalabra': 0, 'palabra': "ROJO"})
    doc.insert({'numPalabra': 1, 'palabra': "PANTALON"})
    doc.insert({'numPalabra': 2, 'palabra': "ZANAHORIA"})
    doc.insert({'numPalabra': 3, 'palabra': "MINERIA DE DATOS"})
    doc.insert({'numPalabra': 4, 'palabra': "CRISTHIANO RONALDO"})
    doc.insert({'numPalabra': 5, 'palabra': "ADIOS"})
    doc.insert({'numPalabra': 6, 'palabra': "GRACIAS"})

####################### MODELO #########################33
def get_feature_test():
    with open('le_caracter.pkl', 'rb') as fid:
        le_caracter = cPickle.load(fid)

    features_test_obs = doc_features_test.find()

    features_test = []
    for objeto in features_test_obs:
        
        try:
            caracter_t = le_caracter.transform([[objeto["caracter"]]])
            feature_caracter = round(float(objeto["tiempo"]),5) 
            feature_fallo = round(float(objeto["falloCaracter"]),5) 

            feature = [caracter_t[0], feature_caracter, feature_fallo]
            features_test.append (feature)
        except Exception as e:
            pass

    return features_test

def preprocess():
    print('<-- preprocess')
    with open('le_caracter.pkl', 'rb') as fid:
        le_caracter = cPickle.load(fid)
    with open('le_usuario.pkl', 'rb') as fid2:
        le_usuario = cPickle.load(fid2)
    
    features_train_obs = doc_features.find()
    features_train = []
    labels_train = []

    for objeto in features_train_obs:
        try:
            # Features
            usuario = le_usuario.transform([objeto["usuario"].strip()])
            caracter_t = le_caracter.transform([[objeto["caracter"]]])
            feature_caracter = round(float(objeto["tiempo"]),5) 
            feature_fallo = round(float(objeto["falloCaracter"]),5) 

            # Guardamos
            feature = [caracter_t[0], feature_caracter, feature_fallo]
            features_train.append (feature)
            labels_train.append(usuario[0])
            
        except Exception as e:
            pass
    print ('<-- OK') 
    return features_train, labels_train

def get_nombre_usuario(num_usuario):
    with open('le_usuario.pkl', 'rb') as fid:
        le_usuario = cPickle.load(fid)

    u =  le_usuario.inverse_transform([num_usuario])
    return u[0]

def get_usuario_ganador (mylist):
    return max(k for k,v in Counter(mylist).items() if v>1)

def realizar_prediccion():
    modelo = importarModelo()
    features_test = get_feature_test()
    y_pred = modelo.predict(features_test)

    print(get_nombre_usuario(y_pred))
    usuario = get_nombre_usuario(get_usuario_ganador(y_pred))
    print (usuario)

    doc_features_test.drop()
def realizar_entrenamiento():
    print ('<-- realizando entrenamiento')
    # svm = svm.SVC(kernel='linear', C=1)
    ada = AdaBoostClassifier(n_estimators=100)
    # random_forest = RandomForestClassifier(n_estimators=101)
    
    # Obtenemos las features y los labels
    features_train, labels_train = preprocess()

    print (np.shape(labels_train))
    print (np.shape(features_train))

    # Entrenamos
    ada.fit(features_train, labels_train)

    exportarModelo(ada)

def importarModelo():
    with open('classifier.pkl', 'rb') as fid:
        modelo = cPickle.load(fid)
    return modelo

def exportarModelo(modelo):  
    print('<--- exportar modelo')  
    # save the classifier
    with open('classifier.pkl', 'wb') as fid:
        cPickle.dump(modelo, fid) 

@app.route('/list',methods = ["GET"])
def list():
    ops = doc_features.find()
    ss = ""
    for o in ops:

      try:
        ss += str(o["usuario"]) 
        ss += ";" 
        ss += str(o["palabra"]) 
        ss += ";" 
        ss += str(o["palabraLeida"]) 
        ss += ";" 
        ss +=  str("%.3f" % round(float(o["tiempo"]),5) )
        ss += ";" 
        ss += str(o["hayErrPalabra"]) 
        ss += ";" 
        ss += str("%.3f" % round(float(o["tiempoErrPalabra"]),5) ) 
        ss += ";" 
        ss += str(o["numPalabra"]) 
        ss += ";" 
        ss += str("%.3f" % round(float(o["tiempoPalabra"]),5) ) 
        ss += ";" 
        ss += str(o["tamPalabra"])
        ss += ";" 
        ss += str(o["caracter"])
        ss += ";" 
        ss += str(o["falloCaracter"])
        ss += ";" 
        ss += str(o["palabraCorrecta"])
        ss += "\n"
      except Exception as e:
        pass
    output = make_response(ss)
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output

# #################### RUN APP #############################
if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    #HOST = environ.get('SERVER_HOST', 'ec2-52-205-165-220.compute-1.amazonaws.com')
    try:
        PORT = int(environ.get('SERVER_PORT', '8000'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT, debug=True)
