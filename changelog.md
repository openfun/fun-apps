# Changelog www.fun-mooc.fr

## 3.15 08/06/2016

- Comptabilité :
    - téléchargement de relevé de transaction comptable #2704
    - résolution d'un problème empéchant de s'inscrire en mode vérifié si une date d'expiration est définie dans le LMS #2863

- Certification:
    - possibilité de générer des certificats vérifiés pour un cours avec vérification du service de surveillance d'examen
    - requetage du service de surveillance des examens (proctoru) par utilisateur ou par interval #2975
    - changement de la mise en page des certificats #2982
    - fusion des méthodes de générations des attestations / certificats vérifiés (le bouton générer les attestations dans le backoffice génère tout)

- Autre :
    - backoffice, résolution de la disparition de l'onglet "utilisateurs vérifiés" #2976
    - ajout du logo OpenEDX dans le footer #2408


## 3.14 26/05/2016
- Certificats verifiés:
    + Génération
    + Le backoffice permet de visualiser et de changer la note
    + Ajout de trackinglogs
    + Saisi de la note d'obtention dans le studio
    + Divers wording relatifs à l'adaptation à notre workflow
- Suppression des informations nominatives sur les apprenants des exports du dashboard concepteur

## 3.13 11/05/2016

- Analytics :
    - Suppression de XITI dans le code
    - Possibilité de refuser les cookies de tracking
- Certificats vérifiés / attestations :
    - La délivrance des certificats prent en compte les informations de proctorU et la note à l'examen certifié (génération d'un attestation si possible le cas échéant)
    - On peut générer des certificats depuis le backoffice
    - Les certificats sont générés sous forme de page web (imprimables correctement)
    - La CA peut personnaliser depuis le CMS les informations (signatures, logos...) apparaissant sur le certificat, les non admins ne voient pas le menu
    - On peut regarder les informations sur la certification (note, statut proctorU) dans le backoffice
- Vidéos :
    - Amélioration des performances lors des appels à libcast, ce qui devrait dimunuer le nombre de timeout observés
    - Résolution de problèmes concernant l'upload de vidéos pesant plus de 64 Mo
    - Augmentation du timeout toléré lors de la récupération des vidéos d'un cours dans le studio, notamment lors du premier accès pour un cours venant d'être créé
- Droits d'accès / rôles plate-forme :
    - Création d'un rôle d'éditeur d'actualités pour édition via l'admin django sans avoir les droits admins
- Conditions d'utilisation :
    - Amélioration des performances
- Autres :
    - Amélioration de la traduction dans la page d'acceptation des conditions de paiement (/payment/terms/agreement/)
    - La pagination de la page de news utilise un style FUN


## 3.12 03/05/2016
- Backoffice:
    - Mises en évidence des cours auxquels un utilsateurs est désinscrit
    - Affichage des cours ayant un mode payant
    - Page de statut des utilisateurs inscrits à un cours payant (état proctoring, note obtenue etc...)
- Gestion de versions du règlement d'examen certifiant

## 3.11 28/04/2016
- Backoffice: Possibilité de passer du mode 'honor' au mode 'verified' pour un
  apprenant inscrit à un cours. Pour tester les cours payants sans avoir à
  mettre sa CB.
- Backoffice: Le résultat des tâches de génération des certificats est
  maintenant de nouveau affiché dans le backoffice.
- Backoffice: Redéfinition du flag 'Prevent auto update' qui s'appelle
  maintenant "Empêcher la mise à jour automatique du score" et n'empêche plus
  la synchronisation entre studio et backoffice.
- LMS: Ajout d'un nouveau filtre "Ouvert aux inscriptions" dans le filtre
  disponibilité.
- LMS: Les cours sans date de fin d'inscription n'apparaissent plus en premier.
- LMS: Améliorations des performances du studio du bac à sable.
- LMS: Mise à jour du xBlock proctorU dans sa version 1.4.

## 3.10 14/04/2016
- Amélioration des pages de paiement échec et abandon.
- Ajout de la possibilité de trier les cours selon differents critères
- Tri des video dans le dashboard d'upload
- Accès utilisateur à l'historique des paiements de certificats dans le dashboard

## 3.9 24/03/2016
- Ajout du xBlock ProctorU
- Ajustements divers sur le système de paiement: wording, email de confirmation..

## 3.8 17/03/2016
- Mise en production du système de cours payant
- Changement du nom de domaine principal: fun-mooc.fr
- Ajout de la pagination sur la page des actualités
- Retrait des pages HTML surchargées dans `fun-apps` pour un fork dans `edx-platform`

## 3.7 03/03/2016
- Précision de la charte de bonne conduite des apprenants
- Page principale :
    - Affichage de la tagline "L'excellence..." en une langue cohérente avec le reste du site
    - Mise à jour à chaque rafraîchissement des actualités et des cours à la une
    - Affichage des établissements non "obsolètes", qu'ils disposent d'une page propre ou non
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

