Projet ETL pour la gestion des médicaments
Ce projet implémente un processus ETL (Extract, Transform, Load) pour récupérer des données sur les médicaments et leurs effets secondaires, les transformer et les charger dans une base de données MySQL. L'application se compose de deux parties : un backend construit avec Flask pour gérer le processus ETL et exposer une API, et un frontend construit avec React pour interagir avec l'utilisateur et afficher les données.

Fonctionnalités
Extraction des données (Extract) :
Récupération des données d'étiquettes de médicaments et des événements indésirables à partir de l'API publique de la FDA.
Transformation des données (Transform) :
Transformation et nettoyage des données extraites pour les adapter au modèle de la base de données MySQL.
Chargement des données (Load) :
Insertion des données dans une base de données MySQL avec gestion des doublons.
Backend (API Flask) :
Exposition d'une API RESTful avec des endpoints pour charger les données et récupérer la liste des médicaments et leurs effets secondaires.
Frontend (React) :
Interface utilisateur interactive permettant de visualiser les médicaments et leurs effets secondaires.
Interface pour déclencher le processus ETL et charger les données.
Architecture
Le projet se compose de deux principaux composants :

Backend :
Flask expose des API RESTful pour charger les données (/load_data) et récupérer la liste des médicaments (/medicaments).
La base de données MySQL stocke les médicaments et leurs effets secondaires.
Frontend :
React consomme les API exposées par Flask pour afficher les médicaments et leurs effets secondaires dans une interface utilisateur conviviale.
Permet de déclencher l'opération ETL depuis l'interface utilisateur.
Technologies utilisées
Backend :
Flask pour le serveur web et les API.
SQLAlchemy pour la gestion de la base de données MySQL.
MySQL comme base de données.
requests pour interagir avec l'API publique de la FDA.
Frontend :
React pour la création de l'interface utilisateur.
Axios pour faire des requêtes HTTP vers l'API Flask.
CSS pour le design de l'interface.
