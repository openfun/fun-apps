# Changelog www.france-universite-numerique.fr

## 3.0 23/11/2015
- Nouveau design du site, et suppression du système de thème edX. Toutes les pages non courseware sont maintenant indépendantes du dépôt `edx-platform`.
    + Nouvelle page d'accueil présentant des cours mis en avant, des actualités, des thèmes...
    + Nouvelle page de liste et de recherche des cours
    + Dénormalisation des metadonnées de cours de mongoDB dans la base SQL
    + Une API publique est disponible pour consulter et chercher la liste des cours
    + Etc..

## 2.17 30/07/2015
- Ajout d'un xblock permettant d'intégrer des notes externes dans le courseware
- Backoffice :
    - Edition des news
    - Prise en compte des microsites
- Upload de vidéo sur Dailymotion Public. (pas de lien pour les concepteurs)
- Intégration de la FAQ Zendesk sur la page /aide 
- Résolution d'un problème de CSS qui décentrait le header de toutes les pages
- Création d'un script permettant de supprimer les permissions d'écriture du wiki d'un cours
- Modification de la visibilité par défaut des profils des utilisateurs
- Ajout de metadatas cours/enseignant/thematiques en vue fun v3 + migrations des données existantes

## 2.14 16/06/2015
- Merge edX au 26/05/2015
    - Visualisation et édition des profils utilisateurs
- Backoffice utilisateurs:
	- pagination, tri par colonne
	- renvoi du mail d'activation
	- bouton pour modifier la note d'une attestation
- Utilisation des vidéos DailyMotion via l'ajout d'un module dans les paramètres avancés

## 2.13 26/05/2015
- Ajout des conditions de confidentialité CNIL
- Modifications mineures

## 2.12 12/05/2015
- Mise à jour des mentions légales
- Backoffice:
    - Accélération du chargement de la page principale
    - Prise en compte des DROM-COM dans les statistiques nationales françaises
    - Visualisation et édition des informations utilisateurs
- Course Dashboard:
    - Distribution des réponses pour QCM et questions avec liste déroulante.
    - Anonymisation du champ 'username' par clé dans les rapports csv de distribution des réponses.
- Bugfixes
	- Backoffice : les rôles edx des concepteurs sont correctment triés.
    - Ajout d'une police manquante en mode développement

## 2.11 23/04/2015
- Merge edX au 31 mars 2015 + hotfixes
- Dashboard de répartition des réponses au quizz: affichage du plan sous forme d'arbre
	- affichage des distributions sous forme de camembert
- Dashboard enseignant de statistiques d'activité du wiki
- Backoffice: Optimisation du temps d'affichage de la liste des cours
- ORA2: possibilité de téléverser des images
- Bugfixes
    - liens conversations sur le profile utilisateurs forum
    - La prévisualisation de la page de news n'affiche plus l'article en cours de rédaction en double
	 - traductions
	

## 2.10 09/03/2015
- Refactorisation du code permettant la consultation de la répartition des reponses aux quizz
- Ajout d'un commande permettant de désinscrire en masse des utiilsateurs d'un cours
- Ajout à l'admin Django des exclusions temporaires: LoginFailures
- Ajout à l'admin Django des résultats de tâches Celery: TaskMeta et TaskSetMeta
- Bugfix stats utilisateurs du forum


## 2.9  26/03/2015
- Mise à jours edx-platform au 10 mars 2015
- Le xblock DMCloud supporte mieux les erreurs d'ID video (plus de bloquage)
- Tri des cours par date dans le backoffice cellule d'appui
- Dans le forum, support des cohortes et de la validation des réponses par l'équipe pédagogique
- Les stats du forum pointent vers le profil l'utilisateur le plus actif
- Le dashboard enseignant permet maintenant aux enseignants d'ajouter des élèves aux cohortes


## 2.8 12/03/2015
- Téléchargement des resultat de quizz en CSV depuis le dashboard enseignant
- Flux RSS des cours disponibles
- Statistiques inscriptions, geographiques et forum au niveau globales (CA)
- Le téléchargement des réponses à l'évaluation par les pairs est maintenant asynchrone
- Les settings de développement sont maintenant dans le dépôt public `fun-apps`
- Refonte de l'organisation des settings par environement: production dépôt privé `fun-config` et developpement dépôt public `fun-apps`
- Bugfixes


## 2.7 26/02/2015
- Mise à jours edx-platform au 13 février 2015 (Aspen rc3)
- Modification du thème FUN pour être plus proche du thème edx; Largeur et menu du courseware
- Statistiques géographiques d'inscriptions par cours
- Téléchargement des réponses à l'évaluation par les pairs
- Export de la liste des cours au format CVS (CA)
- Bugfixes


## 2.6 5/02/2015
- Statistiques inscriptions, geographique et forum par cours pour l'equipe pédagogique.
- Génération d'un certificat de test (CA)

