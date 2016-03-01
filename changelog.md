# Changelog www.france-universite-numerique.fr

## 3.7 03/03/2016
- Précision de la charte de bonne conduite des apprenants
- Page principale :
    - Affichage de la tagline "L'excellence..." en une langue cohérente avec le reste du site
    - Mise à jour à chaque rafraîchissement des actualités et des cours à la une
    - Affichage des établissements "obsolètes", qu'ils disposent d'une page propre ou non
- Backoffice :
    - Recherche de cours plus rapide
    - Ajout d'un bouton "Exorciser" pour prendre possession d'un utilisateur
    - Re-génération du certificat d'un utilisateur pour lequel la note a changé
    - Ajout de traductions manquantes
- Faire en sorte qu'il soit impossible de mettre à jour les scores de certains cours

## 3.6 18/02/2016
- Recherche de cours par titre, sujet, université, enseignants ou description.
- Backoffice : accélération de la recherche d'utilisateurs
- Correction de la liste des langues dans la page de paramètres du compte
- Rectification de la croix rouge et de la coche vert indiquant la validité d'une réponse à une question à choix multiples
- Rectification des statistiques de répartition des réponses dans le tableau de bord de cours
- Rectification des statistiques de répartition geographique des utilisateurs dans le tableau de bord de cours
- Mise en cohérence du format des images utilisées pour les actualités
- Affichage des langues de cours dans le syllabus


## 3.5 04/02/2016
- Mise en cache des données de l'API Libcast pour améliorer la stabilité
- Moteur de recherche full-text de cours
- Amelioration de la prise en charge des themes et etablissements dans l'API

## 3.4
- Ajout de la langue allemande dans les filtre de cours
- Nouveaux flux RSS Cours et Actualité
- Amelioration du Backoffice actualité

## 3.3 20/01/2016
- Merge de la nouvelle version LTS de edX: Cypress
    - http://edx.readthedocs.org/projects/open-edx-release-notes/en/latest/cypress.html

## 3.2.1
- Ajout de l'api de consultation des établissements

## 3.2
- Backoffice: Page de gestion du wiki
    + Affichage de l'arborescence des pages et leur activité
    + Retrait et ajout des permissions d'écriture
- Amélioration de la gestion des actualités dans le backoffice et de leur ordre d'affichage sur le front
- SEO: Amélioration des `title` et `meta description` de la home page
- Prise en compte des majuscules accentuées dans le tri des établisement et thématiques
- Amelioration du support Internet Explorer

## 3.1 8/12/2015
- Possibilité de spécifier la langues principale d'un cours
    - Création des certificats dans cette langue
    - Filtrage des cours par langue
- Bugfixes (Popin de login en basse résolution et teaser video sous FF)

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

