from flask import Flask, jsonify, request, make_response
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import requests
from sqlalchemy.dialects.mysql import insert


app = Flask(__name__)

# Configuration de la base de données MySQL
DB_CONFIG = {
    'user': 'root',
    'password': 'domont',
    'host': 'localhost',
    'port': 3307,
    'database': 'medicaments_db'
}

# Création de l'URL de connexion
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
print("URL de connexion à la base de données:", DATABASE_URL)

# Déclaration de la base et du moteur SQLAlchemy
Base = declarative_base()
engine = create_engine(DATABASE_URL)

# Déclaration du modèle
class Medicament(Base):
    __tablename__ = 'medicaments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom_medicament = Column(String(255), nullable=False, unique=True)  # Ajout de la contrainte unique
    effets_secondaires = Column(Text, nullable=False)


# Création des tables si elles n'existent pas encore
Base.metadata.create_all(engine)

# Étape 1 : Extraction des données
def extract_data():
    # URL pour les informations sur les étiquettes (labels) des médicaments
    label_url = "https://api.fda.gov/drug/label.json?limit=500"

    # URL pour les événements indésirables rapportés pour les médicaments
    event_url = "https://api.fda.gov/drug/event.json?search=receivedate:[20040101+TO+20081231]&limit=500"

    # Appel API pour les étiquettes des médicaments
    label_response = requests.get(label_url)
    label_data = []
    if label_response.status_code == 200:
        label_data = label_response.json().get('results', [])
    else:
        print("Erreur lors de l'extraction des données d'étiquettes.")

    # Appel API pour les événements indésirables
    event_response = requests.get(event_url)
    event_data = []
    if event_response.status_code == 200:
        event_data = event_response.json().get('results', [])
    else:
        print("Erreur lors de l'extraction des données d'événements.")

    # Retourner les deux ensembles de données
    return {
        "labels": label_data,
        "events": event_data
    }


# Étape 2 : Transformation des données
def transform_data(data):
    transformed_data = []
    for item in data:
        nom_medicament = item.get('openfda', {}).get('brand_name', ['N/A'])[0]
        effets_secondaires = item.get('adverse_reactions', ['N/A'])

        if nom_medicament != 'N/A':
            transformed_data.append({
                'Nom du médicament': nom_medicament,
                'Effets secondaires': effets_secondaires if effets_secondaires != ['N/A'] else [
                    'Aucun effet secondaire enregistré'],
            })
    return transformed_data

# Étape 3 : Chargement des données dans MySQL
def load_data(transformed_data):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        for row in transformed_data:
            medicament = Medicament(
                nom_medicament=row['Nom du médicament'],
                effets_secondaires=', '.join(row['Effets secondaires'])
            )

            # Utilisation de la méthode `insert()` de SQLAlchemy avec la gestion des doublons
            stmt = insert(Medicament).values(
                nom_medicament=medicament.nom_medicament,
                effets_secondaires=medicament.effets_secondaires
            )
            stmt = stmt.on_duplicate_key_update({})  # Ignorer si un doublon est trouvé
            session.execute(stmt)

        session.commit()
        print("Données chargées avec succès dans la base de données MySQL.")
    except Exception as e:
        session.rollback()
        print(f"Erreur lors de l'insertion dans MySQL: {e}")
    finally:
        session.close()

@app.route('/load_data', methods=['POST', 'OPTIONS'])
def load_data_route():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = extract_data()
    if data:
        transformed_data = transform_data(data)
        load_data(transformed_data)
        response = jsonify({"message": "Données chargées avec succès."})
    else:
        response = jsonify({"message": "Aucune donnée à traiter."})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/medicaments', methods=['GET'])
def get_medicaments():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Récupérer et trier les médicaments par nom
        medicaments = session.query(Medicament).order_by(Medicament.nom_medicament.asc()).all()
        results = [{"id": m.id, "nom_medicament": m.nom_medicament, "effets_secondaires": m.effets_secondaires} for m in medicaments]
        response = jsonify(results)
    except Exception as e:
        print(f"Erreur lors de la récupération des médicaments: {e}")
        response = jsonify({"message": "Erreur lors de la récupération des médicaments."})
        response.status_code = 500
    finally:
        session.close()

    # Ajout manuel des en-têtes CORS
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
