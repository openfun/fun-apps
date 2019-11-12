# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import migrations, models
from payment.models import TermsAndConditions, TranslatedTerms, PAYMENT_TERMS

LICENCE_EN = ""

LICENCE_FR = """
.. contents::
   :depth: 1
..

.. _tos:

Conditions Générales d’Utilisation
==================================

Préambule
---------


Les présentes Conditions générales d’utilisation décrivent les termes et
conditions dans lesquels le GIP FUN-MOOC (ci-après « FUN ») fournit un
service de création et d’hébergement de contenu sur son site Internet
`*www.fun-mooc.fr* <http://www.fun-mooc.fr>`__, (ci-après désigné par
« site »). Tels qu’utilisés dans les présentes "Conditions générales
d'Utilisation" et les suivantes « Politique de confidentialité » et
« Charte d’utilisateurs », « nous » et « notre » se réfèrent au GIP
FUN-MOOC et au `*site* <https://www.fun-mooc.fr/>`__ FUN.

L’accès à ce site est subordonné au respect des présentes Conditions
générales d’utilisation. Tout internaute souhaitant y accéder doit avoir
pris connaissance préalablement de ces Conditions générales
d’utilisation, de la charte utilisateurs, de la politique de
confidentialité et des mentions légales, et s’engage à les respecter
sans réserve.

Objet
-----

FUN fournit une plateforme en ligne d’hébergement de MOOC (Massive Open
Online Courses, en français « cours en ligne ouverts et massifs) créés
par des établissements d’enseignement supérieur, les organismes de
recherche et les partenaires de FUN en France et dans le monde entier.
En vous inscrivant à un cours en ligne sur le
`*site* <https://www.fun-mooc.fr/>`__, vous rejoignez une communauté
mondiale d'apprenants. L'ambition de FUN est de fournir un accès aux
meilleures formations de l’enseignement supérieur et de ses partenaires,
et ce, quelle que soit votre localisation géographique.

En vous inscrivant sur le `*site* <https://www.fun-mooc.fr/>`__, vous
accepte, sans restriction ni réserve, les conditions générales
d’utilisation, la charte utilisateurs et la politique de
confidentialité. Tout accès et/ou utilisation du
`*site* <https://www.fun-mooc.fr/>`__ est subordonné au respect de
l’ensemble des termes des conditions générales d’utilisation, de la
charte d'utilisateurs et la politique de confidentialité sans
restriction ni réserve.

Si vous ne comprenez pas ces termes ou que vous ne souhaitez pas y être
liés légalement, nous vous invitons à ne pas utiliser le site internet
de FUN, `*www.fun-mooc.fr.* <http://www.fun-mooc.fr./>`__

FUN se réserve donc le droit de refuser l'accès ou d’exclure, sans
préjudice de tout dommage et intérêt pour l’utilisateur et sans
notification préalable, tout utilisateur qui ne respecterait pas les
conditions générales d'utilisation, la charte utilisateurs et la
politique de confidentialité, et également de supprimer toute
contribution ou commentaire notamment en cas d’infraction au regard de
la loi française, de même qu’en cas de réclamation d’un tiers.

FUN se réserve le droit de modifier à tout moment et sans communication
préalable les conditions générales d'utilisation, la charte utilisateurs
et la politique de confidentialité et les mentions légales tout en
préservant le respect des dispositions de la loi n° 78-17 du 6 janvier
1978 relative à l'informatique, aux fichiers et aux libertés. Tout
changement sera immédiatement répercuté sur la présente page. La date de
mise à jour sera mentionnée. Vous êtes donc invité à consulter
régulièrement leur dernière version mise à jour. L'utilisation du
`*site* <https://www.fun-mooc.fr/>`__ est soumise à un accord explicite.


Règles de conduites de l’utilisateur
------------------------------------

En tant qu’utilisateur du `*site* <https://www.fun-mooc.fr/>`__, vous
êtes responsable de vos publications et de l’utilisation que vous faites
du `*site.* <https://www.fun-mooc.fr/>`__ Les publications incluent
l’ensemble des éléments de contenu soumis, publiés ou diffusés sur le
`*site* <https://www.fun-mooc.fr/>`__ par vous ou d’autres utilisateurs.
Par éléments de contenu, on entend les textes, les photos, les vidéos,
les discussions dans le cadre des espaces d’interaction (forum, wiki,
réseaux sociaux), les travaux soumis lors des devoirs (évaluation par
les pairs notamment). De manière générale, FUN vous rappelle que FUN ne
garantit pas la véracité, la complétude, l’exhaustivité ni l’exactitude
des commentaires diffusés via le `*site* <https://www.fun-mooc.fr/>`__
par d’autres utilisateurs.

Vous reconnaissez que vous utiliserez le
`*site* <https://www.fun-mooc.fr/>`__ en conformité avec les présentes
conditions générales d'utilisation, la charte utilisateurs et la
politique de confidentialité.

FUN rappelle qu’il est strictement interdit de procéder à tout acte de
cybercriminalité : à savoir les infractions contre la confidentialité,
l'intégrité et la disponibilité de l’accès, des contenus/données et
systèmes informatiques du `*site* <https://www.fun-mooc.fr/>`__, sans
que cette liste ne soit exhaustive.

Vous vous engagez ainsi à respecter les règles de déontologie
informatique et notamment à ne pas effectuer intentionnellement des
opérations qui pourraient avoir pour conséquence de :

-  Usurper l’identité d’autrui ;
-  S’approprier le mot de passe d’un autre utilisateur ;
-  Modifier ou détruire des informations ne vous appartenant pas ;
-  Accéder à des informations appartenant à d’autres utilisateurs sans
   leur autorisation ;
-  Vous connecter ou tenter de vous connecter sur un compte sans
   autorisation ;
-  Laisser quelqu’un utiliser votre nom d’utilisateur et/ou votre mot de
   passe ;
-  Détourner l’une des fonctionnalités du
   `*site* <https://www.fun-mooc.fr/>`__ de son usage normal ;
-  D’endommager, mettre hors service, surcharger ou détériorer le
   serveur ou le réseau.

Cette liste est pourrait être complétée dans le respect des dispositions
légales et réglementaires actuelles.

Vous vous engagez, par ailleurs, à ne pas essayer d’avoir un accès non
autorisé au site, à ne pas recueillir sans autorisation des informations
stockées sur le site, ses serveurs ou des ordinateurs associés par
n'importe quels moyens non intentionnellement rendus disponibles par le
site.

En outre, vous vous engagez à respecter les dispositions légales et
réglementaires en vigueur. Il est par conséquent formellement interdit
de tenir :

-  des propos à caractère raciste, xénophobe, antisémite, homophobe,
   négationniste, pornographique, pédophile, pédopornographique… ;
-  des propos injurieux, diffamatoires, ou portant atteinte à la vie
   privée, et plus généralement aux droits de la personnalité de
   quiconque ;
-  des propos portant atteinte à la dignité humaine ;
-  des propos incitant à la violence, au suicide, au terrorisme, à
   l’utilisation, la fabrication ou la distribution de substances
   illicites ;
-  des propos incitant aux crimes ou aux délits ou qui en font
   l’apologie et plus particulièrement les crimes contre l’humanité ;
-  de porter atteinte aux droits de propriété intellectuelle de tiers
   (notamment textes, photographies) ou au droit à l’image des personnes
   (publication de la photographie d’une personne sans autorisation)
   pour lesquels vous ne disposez pas des autorisations nécessaires des
   auteurs et/ou ayants droit ;
-  de publier intentionnellement du contenu faux, erroné ou trompeur ;
-  de publier des contenus faisant la promotion de services à but
   lucratif.

*Cette liste est pourrait être complétée dans le respect des
disposition légales et réglementaires actuelles.*

Le `*site* <https://www.fun-mooc.fr/>`__ comporte des informations mises
à disposition par des utilisateurs ou des liens hypertextes vers
d’autres sites qui ne sont pas édités par FUN mais fournis ou proposés
par des tiers. Le contenu mis à disposition sur le site est fourni à
titre indicatif. L’existence d’un lien du
`*site* <https://www.fun-mooc.fr/>`__ vers un site externe ne constitue
pas une validation du `*site* <https://www.fun-mooc.fr/>`__ externe ou
de son contenu. Il vous appartient d’exploiter ces informations avec
discernement et esprit critique. Le caractère raisonnable ou actuel,
l’exactitude ou l’exhaustivité du contenu de ces informations n’est pas
vérifié par FUN. Dans ce cadre, FUN rejette expressément toute
responsabilité.

Vous vous engagez également à :

• Respecter les droits de propriété intellectuelle afférents aux
  contenus diffusés sur le `*site* <https://www.fun-mooc.fr/>`__,
  ainsi que les droits de propriété intellectuelle des tiers
  conformément aux conditions d’utilisation propres à chaque cours
  proposé sur le `*site* <https://www.fun-mooc.fr/>`__ ;
• Respecter la vie privée des autres utilisateurs et, plus
  généralement, ne pas porter atteinte à leurs droits ;
• Ne pas porter atteinte à la confidentialité et à la sécurité des
  données personnelles concernant les utilisateurs du
  `*site* <https://www.fun-mooc.fr/>`__ ;
• Ne pas collecter de quelque façon que ce soit des informations sur
  les utilisateurs, y compris leurs adresses e-mail, sans leur
  consentement.
• Ne pas tricher pour améliorer vos résultats ;
• Ne pas améliorer ou dégrader les résultats des autres ;
• Ne pas publier les réponses aux exercices utilisés comme mode
   d’évaluation des apprenants.


En cas de manquement par un utilisateur à l’une ou l’autre des règles
précitées, FUN se réserve le droit de lui bloquer l’accès à tout ou
partie des services du `*site* <https://www.fun-mooc.fr/>`__, de façon
temporaire ou définitive, sans aucune contrepartie et notification à
l’utilisateur.

FUN se réserve également le droit de retirer tout ou partie des
contenus, informations et données de toute nature, que l’utilisateur
aura mis en ligne sur le `*site* <https://www.fun-mooc.fr/>`__.

Utilisation du compte utilisateur
---------------------------------

Afin de participer pleinement aux activités offertes par le
`*site* <https://www.fun-mooc.fr/>`__, vous devez fournir un nom
complet, un nom d’utilisateur, une adresse électronique et un mot de
passe afin de créer un compte d'utilisateur. Lors de l'installation de
votre compte, vous pouvez être amenés à donner des informations
facultatives supplémentaires.

Vous êtes seul responsable de garder confidentiels et non accessibles
vos identifiants et mots de passe. En cas de perte ou de vol de ceux-ci,
ou dans l’éventualité où vous penseriez qu’un tiers a accédé à votre
profil, vous vous engagez à informer FUN via la page contact du
site : \ `*https://www.fun-mooc.fr/contact/* <https://www.fun-mooc.fr/contact/>`__

Vous vous engagez à fournir des informations précises qui correspondent
à votre situation actuelle. Vous consentez également à mettre à jour vos
informations.

Vous vous engagez également à ne pas créer une fausse identité de nature
à induire qui que ce soit en erreur.

FUN s'engage à garantir la confidentialité et la sécurité de vos
informations personnelles conformément à la Politique de
Confidentialité.

Règles d’utilisation des contenus diffusés sur le site
======================================================

Les contenus (textes, cours, photographies, vidéos, etc.) diffusés sur
le `*site* <https://www.fun-mooc.fr/>`__ ne peuvent être utilisés qu’à
des fins strictement personnelles.

Sauf si les conditions d'utilisation des cours en ligne en disposent
autrement, vous vous interdisez de reproduire et/ou d’utiliser les
marques et logos présents sur le `*site* <https://www.fun-mooc.fr/>`__,
ainsi que de modifier, assembler, décompiler, attribuer, sous licencier,
transférer, copier, traduire, reproduire, vendre, publier, exploiter et
diffuser sous quelque format que ce soit, tout ou partie des
informations, textes, photos, images, vidéos et données présents sur ce
site. La violation de ces dispositions impératives vous soumet, et
toutes personnes responsables, aux peines pénales et civiles prévues par
la loi française.

Règles d’utilisation des contenus diffusés sur les cours en ligne hébergés par FUN
----------------------------------------------------------------------------------

Vous vous engagez à respecter les conditions d'utilisation propres à
chaque cours en ligne hébergé sur le
`*site* <https://www.fun-mooc.fr/>`__. Ces conditions sont définies pour
chaque cours et sont disponibles dans la page de présentation de chaque
cours.

Ces conditions sont précisées au moment de votre inscription à un cours
en ligne hébergé sur le `*site* <https://www.fun-mooc.fr/>`__. En
l’absence de précision lors de votre inscription à un cours en ligne,
vous ne pouvez exploiter les contenus qu’à des fins privées et devez
obtenir l’autorisation préalable des auteurs et les mentionner.

Règles d’utilisation des contenus que vous diffusez dans le cadre des cours en ligne hébergés par FUN auxquels vous êtes inscrits
-----------------------------------------------------------------------------------------------------------------------------------

Avant de diffuser des contenus, vous vous assurez de disposer des
autorisations nécessaires relatives aux droits d'auteur ou autres droits
de propriété intellectuelle éventuellement attachés à votre contribution
et/ou commentaire, à travers notamment leur reproduction et leur
diffusion sur le `*site* <https://www.fun-mooc.fr/>`__. Vous veillez
notamment au respect des droits des tiers (droit d’auteur, droit des
marques, droit de la personnalité).

Lorsque vous diffusez des contenus dans le cadre des cours en ligne,
vous autorisez la reproduction et la diffusion de ces contenus, pour le
monde entier, dans le seul cadre des cours en ligne sauf si les
conditions d'utilisation de ces cours en disposent autrement.

Utilisation des marques et des logos
------------------------------------

Les marques et les logos associés, présents sur le
`*site* <https://www.fun-mooc.fr/>`__ sont protégés. Ils appartiennent
par conséquent exclusivement aux organismes émetteurs. Vous ne pouvez
utiliser aucun de ces signes ou leur variante sans l’accord préalable
desdits organismes.


Responsabilités
===============

Responsabilité de l’utilisateur
-------------------------------


L’ensemble du matériel et des logiciels nécessaires à l’accès et à
l’utilisation du `*site* <https://www.fun-mooc.fr/>`__ est à votre
charge. Vous êtes donc responsable du bon fonctionnement de votre
matériel et de son accès internet. Vous êtes tenu de prendre toutes les
mesures préventives nécessaires à la protection de ses données,
logiciels et/ou systèmes informatiques pour se prémunir contre la
contamination d’éventuels virus.

L’usage des contenus mis à disposition par l’intermédiaire du
`*site* <https://www.fun-mooc.fr/>`__ relève de votre seule
responsabilité. Les faits ou actes que vous seriez amené à accomplir en
considération de ces informations ne sauraient engager d’autre
responsabilité que la vôtre. L’accès aux contenus mis à disposition sur
le `*site* <https://www.fun-mooc.fr/>`__ relève de votre responsabilité
et FUN ne pourrait être tenu responsable pour les dégâts ou la perte de
données qui pourraient résulter du téléchargement ou de l’utilisation
des contenus diffusés sur le site.

Vous êtes seul responsable à l’égard de FUN et le cas échéant de tout
tiers, de tous dommages, directs ou indirects, de quelque nature que ce
soit, causés par un contenu, et ce quelle que soit sa nature,
communiqué, transmis ou diffusé par vous, par l’intermédiaire du
`*site* <https://www.fun-mooc.fr/>`__, ainsi que pour toute violation
des présentes conditions générales d'utilisation, la charte utilisateurs
et la politique de confidentialité.

Responsabilité de FUN
---------------------


Le `*site* <https://www.fun-mooc.fr/>`__ est par principe accessible
24/24h, 7/7j, sauf interruption, programmée ou non, pour les besoins de
sa maintenance ou cas de force majeure. Etant de fait soumis à une
obligation de moyen, FUN ne saurait être tenu responsable de tout
dommage, quelle qu’en soit la nature, résultant d’une indisponibilité du
`*site* <https://www.fun-mooc.fr/>`__.

FUN met en œuvre tous les moyens raisonnables à sa disposition pour
assurer un accès de qualité à ses utilisateurs, mais n'est tenu à aucune
obligation d'y parvenir.

FUN ne peut, en outre, être tenu responsable de tout dysfonctionnement
du réseau ou des serveurs ou de tout autre événement échappant au
contrôle raisonnable, qui empêcherait ou dégraderait son accès.

FUN se réserve la possibilité d'interrompre, de suspendre momentanément
ou de modifier sans communication préalable l'accès à tout ou partie de
son site, afin d'en assurer la maintenance, ou pour toute autre raison,
sans que l'interruption n'ouvre droit à aucune obligation ni
indemnisation.

Sauf dans le cas où FUN aurait été dûment informé de l'existence d'un
contenu illicite au sens de la législation en vigueur, et n'aurait pas
agi promptement pour le retirer, FUN ne peut pas être tenu responsable
de la diffusion de ces contenus.

FUN n’est pas responsable des contenus mis à disposition par les
établissements dans les cours en ligne hébergés sur le
`*site* <https://www.fun-mooc.fr/>`__.

En aucun cas, la responsabilité de FUN ne pourra par ailleurs être
recherchée à l’occasion des relations qui pourraient exister entre les
utilisateurs et les cours en ligne hébergés par FUN.

Notifications
-------------

Sauf stipulation expresse contraire, toute notification envoyée à FUN
doit être adressée via la page de contact :
: `*https://www.fun-mooc.fr/contact/* <https://www.fun-mooc.fr/contact/>`__

Toute notification qui vous est destinée sera envoyée en principe par
e-mail à l'adresse que vous avez communiquée sur le
`*site* <https://www.fun-mooc.fr/>`__ lors de votre inscription d’où la
nécessité de renseigner une adresse mail valide.

Juridiction compétente
----------------------

Les présentes Conditions générales d’utilisation, la charte
d'utilisateurs, et la politique de confidentialité sont régies par la
loi et la langue françaises.

En tant qu'utilisateur du `*site* <https://www.fun-mooc.fr/>`__, vous
acceptez que tout litige relatif à l’interprétation, l’exécution des
présentes conditions générales d’utilisation, à la charte
d'utilisateurs, à la politique de confidentialité et/ou grief lié au
fonctionnement de ce site soit réglé devant une juridiction du ressort
de FUN et ce y compris en cas de référé, de requête ou de pluralité de
défendeurs.

Conditions générales d'utilisation du service d'examen surveillé à
distance

En participant à la surveillance à distance de votre examen vous
reconnaissez avoir été informé :

• que la surveillance est effectuée par la société ProctorU, société
  américaine avec laquelle FUN a signé un contrat de service ;
• que vous devrez, depuis le `*site* <https://www.fun-mooc.fr/>`__
  dans le cours certifiant concerné, créer un compte personnel sur la
  plateforme de gestion de cette société. Vous communiquerez alors les
  informations suivantes : nom / prénom / numéro de téléphone /
  adresse postale / pays / photo / photo de la pièce d'identité.
• que la société ProctorU vous demandera d'installer un logiciel de
  prise de contrôle à distance de votre ordinateur (cet outil ne
  pourra être ni installé ni activé sans votre accord explicite) ;
• que la société ProctorU procédera à un contrôle de votre identité
  ainsi qu'à une vérification de l'environnement de travail dans
  lequel se trouve votre ordinateur (voir le `*Manuel
  utilisateur* <https://www.proctoru.com/pre-exam-checklist/>`__)
  juste avant chaque examen ;
• que la société ProctorU pourra, lors de l'examen uniquement, avoir
  accès à votre ordinateur. À savoir : prise de contrôle à distance du
  clavier et de la souris ; visualisation de votre écran ; activation
  de la caméra et du microphone ;
• que les données recueillies seront stockées sur les serveurs de la
  société ProctorU aux USA, en dehors de la zone européenne. Dans le
  cadre du contrat de service signé avec FUN, la société ProctorU
  s'est engagée à tout mettre en œuvre afin de protéger les données
  recueillies et à les détruire au bout d'un an pour les données
  déclaratives et au bout de 6 semaines pour la pièce d’identité, la
  photo et l’enregistrement vidéo et audio de l’examen.





.. _honor:

Charte utilisateurs
===================

En vous inscrivant sur le `*site* <https://www.fun-mooc.fr/>`__, vous
rejoignez une communauté mondiale d'apprenants. L'ambition de FUN est de
fournir un accès aux meilleures formations de l’enseignement supérieur
et ce, quelle que soit votre localisation géographique.

Recommandations aux utilisateurs
--------------------------------


Sauf indication contraire de l'enseignant du cours, vous êtes encouragés
à :

• Participer à l’ensemble des activités d’un cours : lecture des
  vidéos, exercices, devoirs et travaux pratiques ;

• Discuter avec les autres apprenants des concepts généraux et des
  ressources de chaque cours en utilisant les outils collaboratifs mis
  à disposition ;

• Proposer des idées et éventuellement proposer les documents que
  vous pourrez élaborer, aux autres apprenants à des fins de
  commentaires ;

• Vous assurer que le nom complet est celui que vous souhaitez faire
  figurer sur vos attestations et certificats (\*) ;

• S'assurer que votre nom d'utilisateur est choisi avec soin car il
  n'est pas modifiable - comme il sera visible des autres
  participants, il recommandé qu'il ne reflète pas votre vrai nom.

Engagements des utilisateurs
----------------------------

En complément des règles de conduite précisées dans les Conditions
Générales d’Utilisation, et à la Politique de Confidentialité, vous vous
engagez à :

• Ne pas tricher pour améliorer vos résultats ;

• Ne pas améliorer ou dégrader les résultats des autres ;

• Ne pas publier les réponses aux exercices pris en compte dans
  l’évaluation finale des étudiants ;

• Respecter les droits de propriété intellectuelle accordés par la
  licence d’utilisation attachée à chaque cours en ligne sur le
  `*site* <https://www.fun-mooc.fr/>`__ (cf. conditions d’utilisation
  précisées sur la page de présentation / inscription de chaque cours);

• Donner accès à l’équipe enseignante à vos données collectées sur
  le `*site* <https://www.fun-mooc.fr/>`__ pour les besoins du cours
  suivi.

(\*) A noter: une fois les attestations et/ou certifications éditées, il
n’y aura plus de possibilité de modifier le nom complet sur ce document.

.. _privacy:

Politique de confidentialité
============================

Confidentialité et sécurité des informations personnelles
---------------------------------------------------------

Nous nous soucions de la confidentialité et de la sécurité de vos
informations personnelles. Nous déploierons tous les efforts
raisonnables pour les protéger (le terme « données personnelles » est
défini ci-dessous). Toutefois, aucune méthode de transmission ou de
stockage de données numériques n'est jamais complètement sécurisée, et
nous ne pouvons donc pas garantir la sécurité de l'information transmise
ou stockée sur le site `*www.fun-mooc.fr* <http://www.fun-mooc.fr/>`__.

Notre politique de confidentialité s'applique uniquement aux
informations collectées par le \ `*site* <https://www.fun-mooc.fr/>`__,
c’est à dire à tous les contenus et aux pages présentes dans le domaine
`*www.fun-mooc.fr* <http://www.fun-mooc.fr>`__. Elle ne s'applique pas
aux informations que nous pouvons recueillir de votre part par d'autres
moyens, par exemple à celles que vous nous fournissez par téléphone, par
fax, par mail ou par courrier conventionnel. En outre, veuillez noter
que vos données personnelles sont protégées par les règles du droit
français.

En accédant ou en vous inscrivant sur ce site, vous consentez et
acceptez le fait que les informations collectées vous concernant,
puissent être utilisées et divulguées conformément à notre politique de
confidentialité et nos conditions générales d'utilisation. Comme la loi
peut l'exiger ou le permettre, ces informations peuvent être
transférées, traitées et stockées en France, aux Etats-Unis (uniquement
pour la certification) et potentiellement dans les pays des
établissements producteurs de MOOC diffusés sur le
`*site* <https://www.fun-mooc.fr/>`__, dans les `*pays adéquats et non
adéquats* <https://www.cnil.fr/fr/la-protection-des-donnees-dans-le-monde>`__
aux termes consacrés par la Commission Nationale de l'Informatique et
des Libertés. Si vous n'acceptez pas ces termes, alors nous vous
invitons à ne pas accéder, naviguer ou vous inscrire sur ce site. Si
vous choisissez de ne pas nous fournir certaines informations
nécessaires pour vous offrir nos services, vous ne pourrez pas ouvrir un
compte utilisateur.

Tel qu'utilisé dans la présente « politique de confidentialité »,
« données personnelles » désigne toute information vous concernant que
vous nous fournissez lors de l'utilisation du site, par exemple lorsque
vous créez un compte utilisateur ou concluez une transaction, ce qui
peut inclure de manière non limitative votre nom, vos coordonnées, sexe,
date de naissance et profession.

Données personnelles
--------------------

Les données personnelles vous concernant et collectées par le site
`*www.fun-mooc.fr* <http://www.fun-mooc.fr>`__ vous appartiennent. Ces
données sont protégées et non diffusées conformément à la loi
française.

Ces données sont utilisées pour assurer la délivrance des services
offerts par le `*site* <https://www.fun-mooc.fr/>`__ : délivrance de
certificats et attestations, échanges de pairs à pairs, échanges entre
l’équipe pédagogique et les apprenants, envoi d’informations de manière
proactive, etc. Nous nous engageons à ce que ces données ne soient pas
diffusées à des tiers ni commercialisées sans votre accord explicite.

Elles peuvent également être utilisées pour vous envoyer des mises à
jour sur les cours en ligne offerts par
`*www.fun-mooc.fr* <http://www.fun-mooc.fr/>`__ ou d'autres événements,
pour communiquer sur les produits ou les services du
`*site* <https://www.fun-mooc.fr/>`__ ou affiliés, pour vous envoyer des
messages électroniques à propos de la maintenance du site ou des mises à
jour ou pour vous envoyer des newsletters.

Nous partagerons l'information recueillie avec les établissements
membres et partenaires de FUN. Eux et nous pouvons partager cette
information, y compris les renseignements personnels, avec des tierces
parties, comme suit :

-  Avec les fournisseurs de services ou entrepreneurs qui effectuent
   certaines tâches en notre nom ou au nom des établissements. Ceci
   comprend les informations que vous nous faites parvenir ainsi que
   toute transaction au travers de l’exploitation de ce
   `*site* <https://www.fun-mooc.fr/>`__ ;

-  Avec les autres visiteurs du `*site* <https://www.fun-mooc.fr/>`__,
   dans la mesure où vous soumettez des commentaires, des devoirs ou
   toute autre information ou du contenu à une zone du
   `*site* <https://www.fun-mooc.fr/>`__ conçue pour les communications
   avec le public et avec d'autres membres d'un cours de FUN auquel vous
   participez. Nous pouvons proposer vos contributions aux étudiants qui
   s'inscriraient plus tard dans les mêmes cours, dans le cadre de
   forums, de didacticiels ou autrement. Si vous nous soumettez vos
   contributions dans des parties non publiques, nous les publierons
   anonymement, sauf avec votre permission explicite, mais nous pouvons
   utiliser votre nom d'utilisateur pour les afficher à l’intention des
   autres membres de votre cours ;

-  Afin de répondre aux citations à comparaître, ordonnances de tribunal
   ou une autre procédure judiciaire, en réponse à une demande de
   coopération de la police ou un autre organisme gouvernemental, en cas
   d'enquête, pour prévenir ou prendre des mesures concernant des
   activités illégales, fraude, aux fins de sécurité ou contre des
   techniques à enjeux suspects, ou pour appliquer nos conditions
   d'utilisation, la charte utilisateur ou cette politique de
   confidentialité, tel qu'il peut être requis par la loi ou pour
   protéger nos droits, notre propriété ou notre sécurité ou celles des
   autres ;

-  Pour vous permettre de communiquer avec d’autres utilisateurs qui
   pourraient avoir des intérêts
   ou des objectifs éducatifs similaires aux vôtres. Par exemple, nous
   pouvons vous recommander des partenaires pour une étude spécifique
   ou mettre en relation des étudiants potentiels avec des enseignants.
   Dans de tels cas, nous pouvons utiliser les informations collectées
   à votre sujet afin de déterminer qui pourrait être intéressé à
   communiquer avec vous, mais nous ne fournirons pas votre nom à
   d'autres utilisateurs, et ne divulguerons pas votre vrai nom ou
   adresse e-mail sans votre consentement explicite ;

-  Pour l'intégration de services tiers. Par exemple, un site externe
   d’hébergement de contenus vidéo ou d'autres sites externes à FUN.
   En outre, nous pouvons partager des informations qui ne vous
   identifient pas personnellement (anonymisées), avec le public et
   avec des tiers, y compris, par exemple, des chercheurs.

Données d’usage
---------------

Les données d’usage sont les données collectées par le site
`*www.fun-mooc.fr* <http://www.fun-mooc.fr>`__ et concernent les usages
des services du site. Il s’agit de données brutes,
totalement anonymisées, utilisées pour produire des statistiques sur
l’utilisation des services du `*site* <https://www.fun-mooc.fr/>`__, et
dont l’analyse permet d’améliorer les services et les fonctionnalités du
`*site* <https://www.fun-mooc.fr/>`__.

Nous collectons des informations lorsque vous vous créez un compte
utilisateur, participez à des cours en ligne, envoyez des messages
courriel et / ou participez à nos forums, nos wiki…. Nous recueillons
des informations sur les performances et les modes d'apprentissage des
apprenants. Nous enregistrons des informations indiquant, entre autres,
les pages de notre site ayant été visitées, l'ordre dans lequel elles
ont été visitées, quand elles ont été visitées et quels sont les liens
et autres contrôles de l'interface utilisateur qui ont été utilisés.

Nous pouvons enregistrer l'adresse IP, le système d'exploitation et le
navigateur utilisé par chaque utilisateur du site. Divers outils sont
utilisés pour recueillir ces informations.

Les données d’usage peuvent être utilisées :

-  Pour permettre aux établissements de proposer, administrer et
   améliorer leurs cours ;

-  Pour nous aider, nous et les établissements, à améliorer l'offre de
   `*www.fun-mooc.fr* <https://www.fun-mooc.fr/>`__, de manière
   individuelle (par exemple au travers de l'équipe pédagogique
   travaillant avec un apprenant) et de manière globale pour
   personnaliser l'expérience et évaluer l'accessibilité et l'impact de
   `*www.fun-mooc.fr* <http://www.fun-mooc.fr>`__ dans la communauté
   éducative internationale ;

-  À des fins de recherche scientifique, en particulier dans les
   domaines des sciences cognitives et de l'éducation ;

-  Pour suivre la fréquentation, à la fois individuelle et globale, la
   progression et l'achèvement d'un cours en ligne et pour analyser les
   statistiques sur la performance des apprenants et la façon dont ils
   apprennent ;

-  Pour détecter des violations de la charte utilisateur, la manière
   d’utiliser le site ainsi que des utilisations frauduleuses ou l'étant
   potentiellement ;

-  Pour publier des informations, mais pas des données personnelles,
   recueillies par `*www.fun-mooc.fr* <https://www.fun-mooc.fr/>`__ sur
   les accès, l'utilisation, l'impact et la performance des apprenants ;

-  Pour archiver ces informations et / ou les utiliser pour des
   communications futures avec vous ;

-  Afin de maintenir et d'améliorer le fonctionnement et la sécurité du
   site et de nos logiciels, systèmes et réseaux.

Gestion des données personnelles et des données d’usage
-------------------------------------------------------

Conformément aux dispositions de la loi n° 78-17 du 6 janvier 1978
relative à l'informatique, aux fichiers et aux libertés, le traitement
automatisé des données nominatives réalisées à partir du site Internet
`*https://www.fun-mooc.fr/* <https://www.fun-mooc.fr/>`__ a fait l'objet
d'une déclaration auprès de la Commission Nationale de l'Informatique et
des Libertés (CNIL).



Responsable du traitement des données collectées
Le Responsable du Traitement des données à caractère personnel est :

**GIP FUN-MOOC**

**12, Villa de Lourcine**

**75014 PARIS**



Finalités de la collecte des données
------------------------------------

La collecte des données sur
le \ `*https://www.fun-mooc.fr/register* <https://www.fun-mooc.fr/register>`__ facilite
l’accès au service proposé depuis le
`*site* <https://www.fun-mooc.fr/>`__, et est réalisée afin :



-  de permettre l’accès et l’inscription aux cours diffusés sur le
   `*site* <https://www.fun-mooc.fr/>`__ ;

-  de permettre le suivi des cours, la participation aux activités
   pédagogiques et aux évaluations, la délivrance d’attestations et/ou
   de certificat ;

-  d’effectuer des travaux de recherche pour réaliser des études
   statistiques après anonymisation.

Diffusion des données collectées
--------------------------------

Les données ainsi collectées pourront être transmises aux personnels de
FUN ainsi qu’à tous tiers chargés de participer à la mise en place, à la
réalisation ou au suivi de votre inscription.

Les personnels de FUN ainsi que les tiers désignés par ce dernier,
auront accès et pourront utiliser les données collectées dans le but de
fournir les services proposés sur le `*site* <https://www.fun-mooc.fr/>`__. Il s’agit :


- des enseignants des équipes pédagogiques et les représentants
  officiels des établissements porteurs des cours, pour toutes les
  données collectées ;

- Des équipes de recherche, es établissements de l'enseignement
  supérieur et de la recherche, des membres ou partenaires de FUN, ou
  des équipes de recherche labélisées, pour les données collectées
  anonymisées;

- Les équipes de FUN afin de produire des bilans d'usage de la
  plate-forme.


En aucun cas, les données collectées ne seront cédées à des tiers, que
ce soit à titre gracieux ou onéreux.

Destinataires des données en dehors de l’Union Européenne

Certains de ces destinataires sont situés en dehors de l’Union
Européenne, et en particulier les destinataires situés dans les pays
suivants :

-  Tunisie,

-  Etats-Unis

Ces destinataires ont communication des données suivantes :


**Pour ce qui concerne les utilisateurs du `*site* <https://www.fun-mooc.fr/>`__**

- Identité de l'utilisateur : nom, prénom, ville et pays de
  résidence, adresse électronique, année de naissance (facultatif) ;

- Sexe (facultatif) ;

- Identifiants de connexion : nom d'utilisateur du
  `*site* <https://www.fun-mooc.fr/>`__ et mot de passe du compte ;

- Plus haut niveau de formation obtenu (facultatif) : doctorat,
  master / diplôme d'ingénieur, licence, licence professionnelle,
  diplôme universitaire de technologie / brevet de technicien
  supérieur, baccalauréat, brevet des collèges, aucun, autre ;

- Motivations concernant l'inscription au `*site* <https://www.fun-mooc.fr/>`__ (facultatif) ;

- Formation suivie : type et identifiant du cours ou du module suivi;

- Résultats obtenus aux exercices, aux questionnaires à choix
  multiples ou aux travaux pratiques en ligne ;

- Contenus mis en ligne sur le `*site* <https://www.fun-mooc.fr/>`__
  : commentaires, informations ou devoirs soumis dans une zone du `*site* <https://www.fun-mooc.fr/>`__ conçue pour les communications
  avec les autres utilisateurs ;

- Données de journalisation qui retracent les opérations réalisées
  par l’apprenant sur le `*site* <https://www.fun-mooc.fr/>`__ : les
  dates et heures d'accès, l'adresse IP du poste de travail,
  identifiant et action sur le `*site* <https://www.fun-mooc.fr/>`__
  (lecture vidéo, ouverture d’une page, réponse à un problème...).

**Pour les utilisateurs du** `*site* <https://www.fun-mooc.fr/>`__ **qui passent l’examen surveillé en ligne par l’intermédiaire d’un prestataire externe, en vue de l’obtention d’un certificat**

- Nom, prénom, adresse, ville, numéro de téléphone, fuseau horaire,
  pays ;

- Enregistrement vidéo et audio de l’examen ; photo de l’apprenant
  pris au début de l’examen ;

- Photo de la pièce d’identité.


**Pour ce qui concerne les membres de l'équipe pédagogique**

- identité de l'enseignant : nom, prénom, adresse électronique ;

- identifiants de connexion : nom d'utilisateur du
  `*site* <https://www.fun-mooc.fr/>`__ et mot de passe du compte ;

- localisation géographique ;

- données de journalisation qui retracent les opérations réalisées
  par les membres de l’équipe pédagogique sur le
  `*site* <https://www.fun-mooc.fr/>`__ (informations identiques à
  celles récupérées pour un apprenant).



La transmission de ces données aux destinataires situés en dehors de
l’Union Européenne est destinée à :

-  Permettre le suivi des cours, la participation aux activités
   pédagogiques et aux évaluations, la délivrance d’attestations et/ou
   de certificat ;

-  Effectuer des travaux de recherche pour réaliser des études
   statistiques après anonymisation.

Les garanties suivantes ont été prises pour s’assurer d’un niveau de
protection suffisant des données collectées :

-  Le transfert de données vers un pays tiers a été déclaré à la CNIL et
   est effectué dans des conditions de protection équivalente à celles
   requises au sein de l’Union Européenne via la signature de Clauses
   Contractuelles Types de la Commission Européenne entre FUN et chaque
   établissement d’enseignement supérieur situé dans les `*pays non
   adéquats* <https://www.cnil.fr/fr/la-protection-des-donnees-dans-le-monde>`__
   (contrat de responsable des traitements à responsable des traitements
   - modèle 2001).

-  Le transfert des données vers le sous-traitant surveillant la
   certification située aux Etats-Unis d’Amérique (ProctorU) a été
   déclaré à la CNIL et est effectué via la signature de Clauses
   Contractuelles Types de la Commission Européenne (contrat de
   responsable des traitements à sous-traitant).

Durée de conservation
---------------------

Sont conservées :

1. Les données à caractère personnel collectées, pendant une durée
   de cinq ans à compter de la dernière activité de l'utilisateur sur
   le `*site* <https://www.fun-mooc.fr/>`__. À l'issue de cette durée
   réglementaire de conservation des données, les données permettant
   d’identifier l’utilisateur sont anonymisées :  Nom, prénom, email et
   nom d'utilisateur.

2. Les données concernant les apprenants qui souhaitent passer
   l’examen surveillé, le sous-traitant conservera les données pour les
   durées suivantes :

3. Nom, prénom, adresse, ville, numéro de téléphone, fuseau horaire,
   pays : un an.

4. Enregistrement vidéo et audio de l’examen, photo de l’apprenant
   pris au début de l’examen, photo de la pièce d’identité : 6
   semaines

Utilisations de Cookies
-----------------------

Certaines informations sont collectées au moyen de cookies (de petits
fichiers texte placés sur votre ordinateur qui stockent des informations
vous concernant et qui peuvent être consultés par le site).

Un cookie ne nous permet pas de vous identifier. De manière générale, il
enregistre des informations relatives à la navigation de votre
ordinateur sur notre `*site* <https://www.fun-mooc.fr/>`__ (les pages
que vous avez consultées, la date et l’heure de la consultation, etc.)
que nous pourrons lire lors de vos visites ultérieures. En l’espèce, il
contient les informations que vous avez fournies. Ainsi, vous n’aurez
pas besoin, lors de votre prochaine visite de remplir à nouveau le
formulaire que nous vous avons proposé.

Nous vous informons que vous pouvez vous opposer à l’enregistrement de
cookies en configurant votre navigateur (dans le menu « outil options »
de Mozilla Firefox ou de Microsoft Explorer). La plupart des navigateurs
fournissent les instructions pour les refuser dans la section « Aide »
de la barre d'outils. Le paramétrage du logiciel de navigation permet
d'informer de la présence de cookie(s) et éventuellement de la refuser
de la manière décrite à l'adresse suivante :
`*www.cnil.fr* <http://www.cnil.fr>`__. Si vous refusez nos cookies, des
fonctions et fonctionnalités de ce site pourraient ne pas fonctionner
correctement.



Services externes
-----------------

Le site `*https://www.fun-mooc.fr/* <https://www.fun-mooc.fr/>`__ peut
donner accès à des liens vers d'autres sites publiés par d'autres
fournisseurs de contenu. Ces autres sites ne sont pas sous notre
contrôle, et vous reconnaissez et acceptez que nous ne sommes pas
responsables de la collecte et de l'utilisation de vos informations par
ces sites. Nous vous encourageons à lire les politiques de
confidentialité de chaque site que vous visitez et utilisez.

Noms d'utilisateurs et messages
-------------------------------

Les commentaires et autres informations que vous publiez dans nos
forums, wikis ou d'autres zones du site conçus pour les communications
publiques, peuvent être consultés et téléchargés par d'autres visiteurs
du site. Pour cette raison, nous vous encourageons à faire preuve de
discrétion avant de publier toute information qui pourrait être utilisée
pour vous identifier sur ces forums ou d’autres endroits publics ou
réservés à un cours.

Hébergement, stockage et sécurité
---------------------------------

Le site est hébergé sur le cloud opéré par Orange Cloud for Business. Il
s'appuie sur la technologie OpenStack. En matière de sécurité
l'hébergeur s'engage à respecter l'accord cadre du \ `*référentiel de
l'ANSSI* <http://www.ssi.gouv.fr/uploads/2016/03/Referentiel_exigences_prestataires_integration_maintenance_V1_0.1.pdf>`__.

Un archivage des données est mis en place à intervalle régulier dans le
respect de la politique de confidentialité. À l’issue de la durée légale
de la conservation des données, ces dernières
sont anonymisées conformément à la déclaration CNIL.

Les registres informatisés conservés dans les systèmes dans le respect
des règles de l’art en matière de sécurité, seront considérés comme
preuves des communications de courriers électroniques, envois de
formulaire d’inscription, téléchargements de contenus, publications de
contenus et postages de commentaires.

L’archivage des formulaires d’inscription est effectué sur un support de
nature à assurer le caractère fidèle et durable requis par les
dispositions légales en vigueur. Il est convenu qu’en cas de divergence
entre les registres informatisés du
`*site* <https://www.fun-mooc.fr/>`__ et les documents au format papier
ou électronique dont dispose l’utilisateur, les registres informatisés
du `*site* <https://www.fun-mooc.fr/>`__ feront foi.

Par ailleurs, vous reconnaissez être parfaitement informé qu’en l’état
de la technique, il est strictement impossible pour le GIP FUN-MOOC de
garantir l’absence d’intrusion dans le
`*site* <https://www.fun-mooc.fr/>`__ et en particulier de garantir
l’absence de destructions et/ou modification et notamment d’altération
malveillante ou non par un autre utilisateur ou toute autre personne,
des commentaires d’un utilisateur, notamment par virus ou autre code ou
instruction affectant le site et/ou tout commentaire.

.. _legal:

Mentions légales
================

Tous les cours présents sur le `*site* <https://www.fun-mooc.fr/>`__
sont conçus par des enseignants-chercheurs, enseignants ou chercheurs
d’établissements d’enseignement supérieur, d’organismes de recherche ou
par des experts des établissements ou organismes partenaires.

Le catalogue des cours disponibles s’enrichira continuellement pour
proposer une variété de formations répondant aux besoins de tous les
publics.

Éditeur du site
---------------


**GIP FUN-MOOC**

**12 Villa de Lourcine**

**75014 Paris**



Contact: `communication@fun-mooc.fr <mailto:communication@fun-mooc.fr>`__

Directeur de la publication

| Catherine Mongenet
| Directrice du GIP FUN-MOOC

Hébergement

| Orange
| Cloud for Business

Gestionnaire des statistiques

Google Analytics

Droit d’accès, de rectification ou de suppression des données

Conformément aux articles 39 et suivants de la loi n° 78-17 du 6 janvier
1978 relative à l'informatique, aux fichiers et aux libertés, toute
personne peut obtenir communication et, le cas échéant, rectification ou
suppression des informations la concernant, ou en adressant un courrier
par la voie postale, accompagné de la copie d’une pièce d'identité au
service :

| GIP-FUN MOOC
| Correspondante Informatique et Liberté
| 12 Villa de Lourcine 75014 Paris

Vous pouvez vous désinscrire des newsletter générales grâce à un lien de
désinscription ou en nous adressant une demande par mail ou par courrier
postal.

Pour toute question relative à la politique de confidentialité, veuillez
nous adresser un mail à l’adresse
suivante : \ `*cil@fun-mooc.fr* <mailto:cil@fun-mooc.fr>`__

Pour toute autre question, consultez
notre page \ `*contact * <https://www.fun-mooc.fr/contact>`__.

Ce site fait actuellement l’objet d’une nouvelle demande d’avis auprès
de la Commission Nationale de l’Informatique et des Libertés.

La précédente demande d’avis de la CNIL (délibération n° 2014-036 du 23
janvier 2014) a fait l’objet d’un arrêté du ministre de l'Éducation
Nationale, de l'Enseignement Supérieur et de la Recherche en date du 24
septembre 2014.

Crédits

Le `*site* <https://www.fun-mooc.fr/>`__ FUN utilise la technologie Open
edX.

Le projet est sous la \ `*licence
AGPL* <http://www.gnu.org/licenses/agpl-3.0.html>`__ et est visible à
l’adresse suivante
: `*https://github.com/openfun* <https://github.com/openfun>`__

| Hébergement : Orange, Cloud for Business, 75015 Paris - France
| Charte graphique : S.Q.L.I. Group, 268, avenue du Président Wilson -
  93210 Saint-Denis

*Dernière mise à jour : 19 Mai 2017*

*Entrée en vigueur : 28 Octobre 2013*

Ce traitement est en cours d'instruction auprès de la CNIL.


"""


def add_new_lience(*a):
    last = TermsAndConditions.get_latest()
    if last:
        name = last.name
        version = last.version
    else:
        name = PAYMENT_TERMS
        version = "1.0"
    new = TermsAndConditions(name=name, version=version + ".2")
    new.save()
    new.texts.add(TranslatedTerms(tr_text=LICENCE_FR, language="fr"))
    new.texts.add(TranslatedTerms(tr_text=LICENCE_EN, language="en"))
    new.save()


class Migration(migrations.Migration):

    dependencies = [("payment", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="TranslatedTerms",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "tr_text",
                    models.TextField(
                        default=b"\n.. Ce champs est dans un format ReST (comme un wiki)\n.. Ceci est un commentaire\n.. http://deusyss.developpez.com/tutoriels/Python/SphinxDoc/#LIV-G\n\n\n.. Les 4 lignes finales (honor, privacy, tos, legal)\n.. permettent la navigation dans le contrat au niveau des ancres\n.. Pri\xc3\xa8re de les ins\xc3\xa9rer avant les titres correspondant\n.. honor = Charte utilisateurs\n.. privacy = Politique de confidentialit\xc3\xa9\n.. tos = Conditions g\xc3\xa9n\xc3\xa9rales d'utilisation\n.. legal =  Mentions l\xc3\xa9gales\n\n.. Ces commentaires ci dessus peuvent \xc3\xaatre retir\xc3\xa9s\n.. ils sont juste l\xc3\xa0 comme aide m\xc3\xa9moire :)\n\n\n.. _honor:\n\n.. _privacy:\n\n.. _tos:\n\n.. _legal:\n\n",
                        verbose_name="Terms and conditions. (ReStructured Text)",
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        default={"french": b"fr"},
                        max_length=5,
                        verbose_name="Language",
                        choices=[
                            (b"fr", b"Fran\xc3\xa7ais"),
                            (b"en", b"English"),
                            (b"de-de", b"Deutsch"),
                        ],
                    ),
                ),
            ],
        ),
        migrations.AlterModelOptions(
            name="termsandconditions",
            options={
                "ordering": ("-datetime",),
                "verbose_name": "Terms and conditions",
                "verbose_name_plural": "Terms and conditions",
            },
        ),
        migrations.AlterField(
            model_name="termsandconditions",
            name="datetime",
            field=models.DateTimeField(
                default=datetime.datetime.now,
                verbose_name="Acceptance date",
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name="termsandconditions",
            name="name",
            field=models.CharField(
                default=b"verified_certificate",
                max_length=100,
                verbose_name="Name",
                db_index=True,
            ),
        ),
        migrations.AddField(
            model_name="translatedterms",
            name="term",
            field=models.ForeignKey(
                related_name="texts", to="payment.TermsAndConditions"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="translatedterms", unique_together=set([("term", "language")])
        ),
        migrations.RunPython(add_new_lience),
    ]
