# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from payment.models import TermsAndConditions, TranslatedTerms

LICENCE_EN="""
General Terms and Conditions of Use
===================================

Preamble
--------

These General Terms and Conditions of Use are meant to define the terms,
conditions, requirements and procedures under which GIP FUN-MOOC
(hereinafter “FUN”) provides web content management and  hosting
services on its `www.fun-mooc.fr <http://www.fun-mooc.fr/>`__ internet
website (hereinafter the “\ `Site <https://www.fun-mooc.fr/>`__\ “). As
used herein, and particularly in the “Privacy Policy” and
“User’s Charter” set out below, “we” and “our” refer to GIP FUN-MOOC and
the FUN website, and “you” refers to the
`Site <https://www.fun-mooc.fr/>`__ user.

By accessing this website, you agree to fully abide by these General
Terms and Conditions of Use. Any user wishing to access the
`Site <https://www.fun-mooc.fr/>`__ must have first read and understood
these General Terms and Conditions of Use, including the User’s Charter,
the Privacy Policy and legal notices and disclaimers, all of which the
user agrees to observe without reservation.

Object and Purpose
------------------

FUN provides an online platform which hosts MOOCs (Massive Open Online
Courses) created by higher education institutions, research
organizations and FUN partners based in France and throughout the world.
By registering for an online course offered on the
`Site <https://www.fun-mooc.fr/>`__, you join a worldwide community of
learners. FUN endeavors to provide you access to top-quality online
courses and learning materials offered by higher education
establishments and FUN partners, wherever you are located.

Furthermore, by registering on the `Site <https://www.fun-mooc.fr/>`__,
you agree, unconditionally and without reservation, to observe and abide
by the General Terms and Conditions of Use, the User’s Charter and the
Privacy Policy. Accessing and/or using
the\ `Site <https://www.fun-mooc.fr/>`__ constitutes your acknowledgment
to comply with these General Terms and Conditions of Use, User’s
Charter, and the Privacy Policy, without limitation or qualification.

If you do not understand these terms and conditions, or do not agree to
be bound to them, you are advised to not use the FUN
`www.fun-mooc.fr. <http://www.fun-mooc.fr./>`__ online website.

Accordingly, FUN reserves the right to deny access or to exclude without
prior notice any user who does not observe the General Terms and
Conditions of Use, the User’s Charter or the Privacy Policy, in which
case FUN shall accept no responsibility or liability for any loss,
damage, action or claim arising out of or otherwise in connection with
such denial of access or exclusion; and FUN also reserves the right to
delete any comment or contribution which is deemed to constitute a
violation of French law or is the subject of a third party claim.

FUN reserves the right to alter or modify the General Terms and
Conditions of Use, the User’s Charter, the Privacy Policy, and the legal
notices and disclaimers without prior notice, all while remaining in
compliance with the provisions of Law n° 78-17 of 6 January 1978 on
French Data Protection and Freedom of Information. Any such alteration
or modification shall be immediately effective upon displaying or
posting it on the present web page. Notice regarding the
updating/modification date shall also be posted on the website.
Accordingly, you are advised to regularly check for the latest, updated
versions of the aforementioned provisions. Permission to use the
`Site <https://www.fun-mooc.fr/>`__ is contingent on an express
agreement between the user and FUN.

User’s Rules of Conduct
-----------------------

As a user of the `Site <https://www.fun-mooc.fr/>`__, you are liable for
any information that you publish on the
`Site <https://www.fun-mooc.fr/>`__, as well as for the manner in which
you use the `Site <https://www.fun-mooc.fr/>`__. Publications include
all content contributed, posted or displayed by you or by other users on
the `Site <https://www.fun-mooc.fr/>`__. Such user-related content is
understood to mean any texts, photographs, videos, or discussions that
are transmitted, communicated, or otherwise presented on interactive
spaces (forums, wikis, social networks), and work submitted as part of
course assignments (including peer assessment assignments). In that
regard, FUN hereby informs you that, as a general practice, FUN does not
guarantee the accuracy, completeness, thoroughness or authenticity of
the comments displayed on the `Site <https://www.fun-mooc.fr/>`__ by
other users.

You acknowledge and agree that you will use the
`Site <https://www.fun-mooc.fr/>`__ while acting in compliance with
these Terms and Conditions of Use, User’s Charter and Privacy Policy.

FUN expressly prohibits you from using the
`Site <https://www.fun-mooc.fr/>`__ or its contents to engage in any
cyber-criminal act, including but not limited to breaches of privacy,
integrity and availability with respect to
`Site <https://www.fun-mooc.fr/>`__ access,
`Site <https://www.fun-mooc.fr/>`__ content,
`Site <https://www.fun-mooc.fr/>`__ data and
`Site <https://www.fun-mooc.fr/>`__ computer systems.

Accordingly, you agree to abide by prevailing rules of conduct for
computer and network use, notably by refraining from intentionally
engaging in any activities that constitute or may give rise to:

- Identity theft;
- Stealing passwords from other users;
- Modifying, altering or destroying data that does not
  belong to you;
- Monitoring or inspecting data belonging to other users,
  without their authorization;
- Connecting to or attempting to connect to an account without proper
  authorization;
- Letting someone use your user name and/or your password;
- Diverting one of the `Site <https://www.fun-mooc.fr/>`__\ ’s
  functions or features, causing it to deviate from normal use;
- Damaging, disabling, overcharging, impairing or disrupting the
  server or the network.

This list is subject to expansion in conformance with prevailing laws,
rules and regulations.

You further agree to abstain from attempting, by any means whatsoever,
unauthorized access to the Site and unauthorized collecting of any data
that is stored on the `Site <https://www.fun-mooc.fr/>`__, its servers
or on associated computers, through any means not intentionally made
available to you through the `Site <https://www.fun-mooc.fr/>`__.

In addition, you agree to observe all applicable laws, rules and
regulations in force prohibiting you from making any comments or
depictions that are:

-  racist, xenophobic, anti-Semitic, homophobic, negationistic,
   revisionist, pornographic, pedophilic, child pornographic in nature,
   or otherwise defamatory, sexually orientated or obscene;
-  abusive, vulgar, defamatory, or which infringe upon a person’s right
   to privacy, and, more generally, violate anyone’s personality rights;
-  of such a nature as to undermine someone’s human dignity;
-  of such a nature as to incite violence, suicide, terrorism, or the
   use, manufacture or distribution of unlawful substances;
-  likely to incite crimes or offenses, and particularly crimes against
   humanity;
-  deemed to infringe third-party intellectual property rights (notably
   copyrights pertaining to texts and photographs) or image rights
   (relating to the publication of a person’s image without their
   consent) whenever you have not received permission from authors
   and/or rights holders;
-  deemed to entail the publication of deliberately fraudulent, false,
   or misleading content;
-  deemed to entail the publication of content promoting for-profit
   services.

This list is subject to expansion in conformance with prevailing laws,
rules and regulations.

The `Site <https://www.fun-mooc.fr/>`__ contains information provided
by users or via hypertext links to other websites that are not edited or
monitored by FUN but have been supplied or offered by third parties. The
existence of a link on the `Site <https://www.fun-mooc.fr/>`__ toward an
external website should not be construed as a validation or endorsement
of the external website or its content by FUN. It is solely your
responsibility to verify and use any such information with discernment
and a critical mind. The reasonableness, timeliness, accuracy or
completeness of such information has not been verified by FUN.
Accordingly, FUN expressly declines any liability in that regard.

You agree, furthermore, to:

-  Respect the intellectual property rights pertaining to content
   featured on the `Site <https://www.fun-mooc.fr/>`__, as well as any
   and all third-party intellectual property rights, in accordance with
   the terms of use specific to each course offered on the
   `Site <https://www.fun-mooc.fr/>`__;
-  Respect the private life of other users and, more generally, abstain
   from interfering in their rights;
-  Preserve the confidentiality and security of private data regarding
   users of the `Site <https://www.fun-mooc.fr/>`__;
-  Not collect by any means user-related data, including e-mail
   addresses, without the concerned users’ consent.
-  Not engage in any form of cheating aimed at artificially enhancing
   your assessments or results;
-  Not attempt to artificially enhance or lower the assessments or
   results of others;
-  Abstain from divulging or publishing answers to exercises used to
   evaluate learners.

If a user breaches any of the aforementioned rules, FUN reserves the
right to block the infringing user’s access to
`Site <https://www.fun-mooc.fr/>`__ services, in whole or in part,
temporarily or definitively, without liability and without need to give
notice to the user.

FUN also reserves the right to remove, in whole or in part, contents,
information and data of any kind, which the user has placed online on
the `Site <https://www.fun-mooc.fr/>`__.

Use of the User Account 
------------------------

To take full advantage of the activities offered by the
`Site <https://www.fun-mooc.fr/>`__, you must provide a full name, a
user name, an e-mail address, and a password, for the purpose of
creating a user account. Upon creation of your account, you may be
required to provide additional, optional information.

It is your sole responsibility to keep your login IDs (usernames) and
passwords secret and non-accessible to third parties. If that
information is lost or stolen, or if you suspect that a third party has
gained access to your profile, you must promptly inform FUN via the
`Site <https://www.fun-mooc.fr/>`__\ ’s contact
page \ https://www.fun-mooc.fr/contact/.

You agree to supply accurate information corresponding to your current
situation and status. You also agree to maintain such information
up-to-date.

You also agree not to create or use a false identity with the intention
of misleading others.

FUN agrees to protect the confidentiality, privacy and security of your
private data, in conformance with the Privacy Policy.

Rules of Use for `Site <https://www.fun-mooc.fr/>`__ Contents 
--------------------------------------------------------------

The contents (texts, courses, photographs, videos, etc.) featured on the
`Site <https://www.fun-mooc.fr/>`__ are for strictly personal use only.

Unless the terms of use applicable to online courses stipulate
otherwise, you are prohibited from reproducing and/or using the brands,
logos and distinctive signs presented on the
`Site <https://www.fun-mooc.fr/>`__, as well as being further prohibited
from modifying, assembling, decompiling, assigning, sub-licensing,
transferring, copying, translating, duplicating, selling, publishing,
exploiting and distributing or issuing, in whole or in part, in any
other format, the information, texts, photos, images, videos and data
featured on this `Site <https://www.fun-mooc.fr/>`__. Failure to comply
with these mandatory conditions renders you and all other offenders
liable to the civil and criminal penalties or sanctions imposed by
French law.

Rules of Use for Content Featured in Online Courses Hosted by FUN 
------------------------------------------------------------------

You agree to abide by the terms of use specific to each online course
hosted on the `Site <https://www.fun-mooc.fr/>`__. Such terms of use are
delineated specifically for each course and are detailed on the
presentation page for each course.

Such terms of use are fully set out at the time of your registration for
an online course hosted on the `Site <https://www.fun-mooc.fr/>`__. If
no such details are provided upon your registration for an online
course, you may access or use the contents for strictly personal
purposes only, and must obtain the permission of use from the relevant
authors and explicitly mention them by name.

Rules of Use for Content posted by you as part of your registered online courses hosted by FUN
----------------------------------------------------------------------------------------------

Before posting/publishing any content, you must ensure that you have
requisite rights and permission, including all copyrights or other
intellectual property rights, pertaining to your contribution and/or
comment, particularly regarding their reproduction and dissemination on
the `Site <https://www.fun-mooc.fr/>`__. Moreover, you agree to use your
utmost diligence to observe third-party rights (copyrights, trademark
rights, or personality and image rights).

Whenever you post content for your online course, you agree to allow
such contents to be reproduced and disseminated potentially worldwide,
though solely for the purposes of the online courses, unless the terms
of use for the courses in question stipulate otherwise.

Use of brands and logos
-----------------------

The brands and associated logos appearing on the
`Site <https://www.fun-mooc.fr/>`__ are protected by trademark.
Consequently, they are the exclusive property of the issuing
organizations and institutions. As such, none of these distinctive signs
or variations thereof may be used, except with the prior consent of the
pertinent organizations and institutions.

Responsibilities
----------------

User Responsibilities
~~~~~~~~~~~~~~~~~~~~~

All hardware and software necessary to access and use the
`Site <https://www.fun-mooc.fr/>`__ are at your own cost, expense and
responsibility. Consequently, you are responsible for ensuring the
proper, continued operation of your hardware and Internet access. To
that end, you must take all corrective and/or preventive measures as may
be necessary to protect all data, software and/or computer systems
against potential contamination or spread of computer viruses.

You are solely responsible for the use of content made available through
the `Site <https://www.fun-mooc.fr/>`__. Any actions or decisions that
you take based on such information are entirely your responsibility. You
assume full liability or responsibility for accessing contents posted on
the `Site <https://www.fun-mooc.fr/>`__ and FUN shall bear no liability
for any loss or damage to data resulting from downloading or using
content posted on the `Site <https://www.fun-mooc.fr/>`__.

You agree to be held solely and fully responsible and liable to FUN and,
if the situation warrants, to any concerned third parties, for any
direct or indirect damage of any kind arising from or in connection with
content transmitted or posted on the `Site <https://www.fun-mooc.fr/>`__
or via the `Site <https://www.fun-mooc.fr/>`__, as well as for any
breach of these General Terms and Conditions of Use, User’s Charter and
Privacy Policy.

FUN’s Responsibilities 
-----------------------

Under normal circumstances, the `Site <https://www.fun-mooc.fr/>`__ is
accessible 24 hours a day every day of the week, except during service
interruptions due to scheduled maintenance or unscheduled emergency
maintenance or due to the occurrence of a *force majeure* event. Insofar
as it is bound to perform its services on the basis of a best efforts
obligation, FUN assumes no liability for any loss or damage of any kind
resulting from the unavailability of the
`Site <https://www.fun-mooc.fr/>`__.

FUN shall use all reasonable means available to provide quality access
to its users, without being bound by any obligation to achieve such
result.

Moreover, FUN assumes no liability for any failure or dysfunction
affecting the network or the servers or any other event deemed to be
beyond FUN’s reasonable control, preventing or impairing user access.

FUN reserves the right to temporarily interrupt, suspend or modify
access to all or part of its `Site <https://www.fun-mooc.fr/>`__,
without prior notice, for maintenance purposes or for any other reason,
without liability or compensation to you.

Except in the instance where FUN had been duly informed of the existence
of illegal content, as defined under applicable law, yet failed to act
promptly to remove it, FUN cannot be held liable for posting such
contents.

FUN bears no responsibility for contents provided by organizations and
institutions for inclusion in online courses hosted by the
`Site <https://www.fun-mooc.fr/>`__.

Also, under no circumstances may FUN be held liable for relationships
existing between users and online courses hosted by FUN.

Notifications 
==============

Unless expressly stipulated otherwise, any notices given pursuant to
these Terms will be deemed to be validly given only if submitted via the
contact page:  https://www.fun-mooc.fr/contact/

Any notice intended for you hereunder shall be deemed duly served if
submitted by e-mail to the address you indicated on the
`Site <https://www.fun-mooc.fr/>`__ upon registration. Hence, it is
imperative that you supply a valid e-mail address at such time.

Jurisdiction and Governing Law

These General Terms and Conditions of Use, User’s Charter, and Privacy
Policy shall be governed by and interpreted according to French law. The
provisions of each have been written in both English and French
languages. Both versions shall be equally valid and effective but, in
the event of inconsistency between the two versions, the French version
shall prevail.

As a user of the `Site <https://www.fun-mooc.fr/>`__, you agree that any
dispute and/or claim arising out of the interpretation or performance of
these General Terms and Conditions of Use, User’s Charter, and/or
Privacy Policy, pertaining to the operation of this
`Site <https://www.fun-mooc.fr/>`__, shall be submitted exclusively to
the French court with jurisdiction over the registered office of FUN,
including in the event of summary judgments, the introduction of third
parties or multiple defendants.

Terms and Conditions for use of the remote exam proctoring service 
===================================================================

By participating in the remote exam proctoring service, you acknowledge
and agree that you have been informed of the following:

-  proctoring is performed by ProctorU, an American company with which
   FUN has entered into a service contract;
-  you are required to create a personal account on said company’s test
   management platform, which you must do from the
   `Site <https://www.fun-mooc.fr/>`__ of the relevant certified course.
   At that time, you will then provide the following information: last
   name/first name/telephone number/mailing address/country/photo/ photo
   of a piece of ID.
-  ProctorU will ask you to install a remote control software on your
   computer (this tool cannot be installed or activated without your
   express consent);
-  ProctorU will authenticate your identity and verify that your
   computer is located in a secure testing environment (see the `User’s
   Manual <https://www.proctoru.com/pre-exam-checklist/>`__) immediately
   prior to each examination;
-  ProctorU will be authorized to access your computer remotely solely
   during the examination itself, specifically as regards taking remote
   control of the keyboard and mouse, seeing your screen, and activating
   the camera and microphone;
-  all data collected will be stored on ProctorU‘s servers located in
   the United States, outside the European area. Pursuant to the terms
   of the service contract entered into with FUN, ProctorU agrees to
   take all necessary measures to protect the data collected and to
   destroy them after a year has passed, in the case of declarative
   data, and after 6 weeks, in the case of the piece of ID, the photo
   and the video and audio recording of the examination.




User’s Charter
==============

By registering on the `Site <https://www.fun-mooc.fr/>`__, you join a
worldwide community of learners. FUN ‘s goal is to offer access to
quality higher education learning, wherever you are in the world.

Recommendations to users 
-------------------------

Unless your online instructor indicates otherwise, you are encouraged
to:

-  Complete all course related activities: watch all videos, do all
   exercises, homework and practical work assignments;
-  Discuss general concepts and course materials for each course with
   the other learners while relying on the collaborative tools
   available;
-  Share ideas and, potentially, documents that you have prepared, with
   other learners, and seek their comments;
-  Make sure that the full name you give is the one you want to appear
   on official documents and certificates (\*);
-  Choose your user name carefully, bearing in mind that it cannot be
   subsequently modified, and—because it will be visible to the other
   participants—you are advised not to use your real name.

Users’ Undertakings 
--------------------

In addition to the rules of conduct set forth in the General Terms and
Conditions of Use, and the Privacy Policy, you undertake to:

- Not engage in any form of cheating aimed at artificially enhancing
  your assessments or results;
- Not attempt to artificially enhance or lower the assessments or
  results of others;
- Not post answers to exercises included in students’ final evaluation;
- Observe the intellectual property rights granted under the user
  license attaching to each online course featured on the
  `Site <https://www.fun-mooc.fr/>`__ (see the terms of use detailed on
  the presentation/registration page for each course);
- Grant the teaching staff access to your data collected on the
  `Site <https://www.fun-mooc.fr/>`__, as may be necessary for the
  purposes of the course(s) you have taken.
- Please note: once the official documents and/or certificates have
  been issued, it will no longer be possible to modify the full name
  appearing on the document.

Privacy Policy 
===============

Privacy and security of personal information
--------------------------------------------

We take great care to preserve the privacy and security of your
“personal information” (as such term is defined below) and use all
reasonable efforts to protect it. Nonetheless, no means of digital data
transmission or storage is entirely secure, which is why we cannot
guarantee the security of the information transmitted or stored on the
`www.fun-mooc.fr <http://www.fun-mooc.fr/>`__ ‘s site.

Our Privacy Policy applies solely to the data collected by the
`Site <https://www.fun-mooc.fr/>`__, i.e., all content and pages
featured on the domain name
`www.fun-mooc.fr <http://www.fun-mooc.fr/>`__. It does not apply to data
that we might eventually collect from you by other means, specifically,
information you furnish by telephone, facsimile, e-mail or through the
ordinary postal system. You should also be aware that your personal
information is protected under the rules of French law.

By accessing this `Site <https://www.fun-mooc.fr/>`__ or registering on
it, you acknowledge and agree that the data collected concerning you can
be used and disclosed pursuant to our Privacy Policy and our General
Terms and Conditions of Use. As the law permits or requires, such data
may be transmitted, processed or stored in France, in the United States
(strictly for certification purposes) and potentially in the countries
where the MOOC provider institutions featured on the
`Site <https://www.fun-mooc.fr/>`__ are located, or in countries deemed
to offer an `“adequate” or
“inadequate” <https://www.cnil.fr/fr/la-protection-des-donnees-dans-le-monde>`__
level of data protections, as such terms are defined by the French Data
Protection Authority *Commission Nationale de l'Informatique et des
Libertés*. If you do not agree to abide by these terms, we advise you
not to access, browse or register on this
`Site <https://www.fun-mooc.fr/>`__. If you decide not to provide us
with certain information required to offer you our services, you will
not be permitted to open a user account. 

As used in this “Privacy Policy” section, “personal information” means
any information concerning you that you provide while using the
`Site <https://www.fun-mooc.fr/>`__, for instance, when you create a
user account or complete a transaction, which may include, but is not
limited to, your name, your contact details, your sex, date of birth,
and occupation. 

Personal Information  
----------------------

The personal information concerning you (personally identifiable data)
that is collected by the `www.fun-mooc.fr <http://www.fun-mooc.fr/>`__
site is your property. Such data is protected and is not subject to
dissemination, pursuant to French law.

This information is used to ensure delivery of the services offered by
the `Site <https://www.fun-mooc.fr/>`__, such as the issuance of
official documents and certificates, peer-to-peer exchanges, exchanges
between the teaching staff and learners, the sending of information on a
proactive basis, etc. We ensure that this information is not
disseminated to third parties or used for commercial purposes without
your express prior consent. 

Personal information may also be used to send you updates regarding the
online courses offered by `www.fun-mooc.fr <http://www.fun-mooc.fr/>`__
or for other events, to inform you about products or services offered by
the `Site <https://www.fun-mooc.fr/>`__ or affiliated organizations, in
order to send e-mail messages regarding the maintenance of the
`Site <https://www.fun-mooc.fr/>`__ or updates or to send you
newsletters. 

We may be led to share the collected information with member
organizations and partners of FUN. They and we share this data,
including personal information, with third parties, as follows: 

-  With service providers or entrepreneurs which carry out certain tasks
   on our behalf or on behalf of the institutions. That includes
   information that you submit to us as well as all transactions carried
   out in connection with operating this
   `Site <https://www.fun-mooc.fr/>`__ ;

-  With other visitors to the `Site <https://www.fun-mooc.fr/>`__,
   whenever you submit comments, homework assignments or any other
   information or content to a space on the
   `Site <https://www.fun-mooc.fr/>`__ intended for communications with
   the public and with others taking a FUN course in which you are
   participating. We may be led to publish your contributions, making
   them viewable by students who later sign up to take the same courses,
   participate in forums, online tutorials or otherwise. If you submit
   your contributions to us through the non-public part of the
   `site <https://www.fun-mooc.fr/>`__, we will publish them
   anonymously, except with your express consent, but we may use your
   name to post such messages for other members of your course;

-  With law enforcement authorities or other government third party
   officials to ensure compliance with subpoenas, court orders or a
   similar legal process, to accede to a request for cooperation
   addressed by such authorities or officials, in connection with an
   investigation seeking to prevent, detect or prosecute illegal or
   fraudulent activities, to resolve security breaches or technical
   problems, or to enforce our Terms and Conditions of Use, the User’s
   Charter or this Privacy Policy, to the extent permitted or required
   by law or in order to protect against imminent harm to the rights,
   property or security of FUN, or those of others;  

-  With other users, particularly in order to enable you to communicate
   with those who may have interests or educational objectives similar
   to your own. For example, we may refer you to partners to conduct a
   specific study or to bring potential students in contact with
   instructors. In such instances, we may be led to use personal
   information concerning you in order to determine who might be
   interested in communicating with you, but we will not disclose your
   name to other users and will not divulge your real name or actual
   e-mail address, except with your express consent;

-  With outside services, such as a video content hosting site or other
   websites external to FUN, for the purposes of outside content
   integration. 

Moreover, we may be led to share anonymized, or non-personally
identifiable data, with the public and third parties, including, for
example researchers. 

Usage data  
----------

Usage data consists of information gathered by the site
`www.fun-mooc.fr <http://www.fun-mooc.fr/>`__ regarding its visitor
(traffic) activity. It is an aggregate of raw, fully anonymized data
that is used to produce statistics on traffic volumes and patterns and
how visitors make use of services offered by the
`Site <https://www.fun-mooc.fr/>`__, and is analyzed with a view to
improve the services and features offered on the
`Site <https://www.fun-mooc.fr/>`__. 

We collect information when you create a user account, participate in
online courses, send e-mail messages and/or take part in our forums,
wikis, etc. We gather information on learners’ performances and modes of
learning. We record information indicating, among other things, our
most-visited website pages, the order in which they were visited, when
they were visited and which links and other user interface controls were
used. 

We might be led to record the IP address, operating system and the
browser employed by each `site <https://www.fun-mooc.fr/>`__ user. An
array of tools is used to collect this data. 

We may employ usage data for personalization and pedagogical
improvements, as follows: 

-  To allow institutions to provide, administer and improve their
   courses;
-  To enable the institutions and FUN to make pedagogical improvements
   to offerings available on
   `www.fun-mooc.fr <https://www.fun-mooc.fr/>`__, both individually
   (e.g. by educational staff when working with a learner) and, in
   aggregate, in order to individualize the experience of the individual
   learner and to evaluate the access and use of the
   `site <https://www.fun-mooc.fr/>`__ and the impact of
   `www.fun-mooc.fr <http://www.fun-mooc.fr/>`__ on the international
   educational community;
-  To serve the purposes of scientific research, particularly in the
   areas of cognitive science and education;  
-  To track individual and aggregate attendance, progress and completion
   of an online courseand to analyze learners’ performance
   statistics and how they learn;
-  To monitor and detect breaches of the User’s Charter, as well as real
   or potential misuses and fraudulent uses of the
   `Ssite <https://www.fun-mooc.fr/>`__;
-  To publish information, but not personal data, gathered about the
   `site <https://www.fun-mooc.fr/>`__\ ’s access, use, impact and
   learners’ performance;
-  To archive this information and/or use it in future communications
   with you;  
-  To maintain and improve the functioning and security of the
   `Site <https://www.fun-mooc.fr/>`__ and our software, systems and
   networks. 

Handling of personal information and usage data
-----------------------------------------------

Pursuant to the provisions of Law n° 78-17 of 6 January 1978 on French
Data Protection and Freedom of Information, a notification regarding the
automated processing of personal information obtained from Internet
website https://www.fun-mooc.fr/ has been filed with the French Data
Protection Authority *Commission Nationale de l'Informatique et des
Libertés* (CNIL).    

The Data Controller
~~~~~~~~~~~~~~~~~~~

The officer responsible for exercising overall control over the manner
in which personal data is processed is:  

**GIP FUN-MOOC**

**12, Villa de Lourcine**

**75014 PARIS**

 

Permitted Uses of the Collected Data 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The data collected on the https://www.fun-mooc.fr/register website is
intended to facilitate access to the services offered on the
`Site <https://www.fun-mooc.fr/>`__, and is processed for the following
purposes: 

-  To enable access to and registration for courses offered on the
   `Site <https://www.fun-mooc.fr/>`__; 
-  To allow students to take courses and let users participate in
   educational activities, take evaluations and assessments, and
   facilitate the issuance of official documents and/or certificates;
-  To conduct research aimed at producing statistics, while relying on
   anonymized data. 

Transmission of Collected Data 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data that has been collected in the manner and for the purposes
indicated above may be transmitted to FUN personnel, as well as to all
duly designated third parties responsible for planning, implementing,
and monitoring your registration.

FUN personnel and third parties duly designated by it, will have access
to the collected data and may use it for the purposes of providing the
services offered on the `Site <https://www.fun-mooc.fr/>`__. Such
personnel and third parties include: 

-  instructors belonging to the teaching staff and official
   representatives of course-providing institutions, with regard to all
   of the data collected; 

-  research teams, higher education and research institutions, members
   or partners of FUN, or accredited research teams, with regard to
   collected data that has been anonymized;

-  FUN teams responsible for carrying out platform usage assessments.

Under no circumstances will the collected data be assigned to third
parties, whether against payment or free of charge. 

Data recipients outside the European Union 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Certain data recipients are located outside the European Union, notably
recipients based in the following countries: 

-  Tunisia,
-  The United States   

The following data may be transferred to such recipients: 

 

With respect to `Site <https://www.fun-mooc.fr/>`__ users

-  The user’s identity: last name, first name, city and country of
   residence, e-mail address, year of birth (optional); 
-  Sex (optional); 
-  Login information: user name for the
   `Site <https://www.fun-mooc.fr/>`__ and account password; 
-  Highest academic degree achieved (optional): Ph.D., Master’s degree,
   Bachelor’s degree, two-year professional degree or associate’s
   degree, two-year short-cycle university-level degree in
   technology/vocational training certificate or diploma,
   *baccalaurea*\ te (high school diploma), secondary school
   certificate, none, other; 
-  Motivations for registering on the
   `Site <https://www.fun-mooc.fr/>`__ (optional); 
-  Course taken: type, name and code of course or module taken; 
-  Results and grades received on online exercises, multiple-choice
   question exams, or practical work assignments; 
-  online content posted on the\ `Site <https://www.fun-mooc.fr/>`__:
   comments, information or assignments submitted into a part of the
   `Site <https://www.fun-mooc.fr/>`__ designed to allow users to
   communicate with each other; 
-  Logging data used to track activities engaged in by the learner on
   the `Site <https://www.fun-mooc.fr/>`__: dates and times of access,
   IP address of the user’s work station, Login ID and activity on the
   Site (watching a video, opening a web page, responding to a problem,
   etc.). 

 

With respect to `Site <https://www.fun-mooc.fr/>`__ users
taking an exam that is proctored online by an outside service provider,
towards obtaining a certificate

-  Last Name, first name, address, city, telephone number, time zone,
   country; 
-  Video and audio recording of the examination session; photo of the
   learner taken at the start of the examination session;
-  Photo of the piece of ID submitted. 

With respect to members of the teaching staff

-  instructor’s identity: last name, first name, and e-mail address; 
-  login information: user name on the
   `Site <https://www.fun-mooc.fr/>`__ and account password; 
-  geographical location; 
-  logging data used to track activities engaged in by members of the
   teaching staff on the `Site <https://www.fun-mooc.fr/>`__:
   (information identical to that retrieved for a learner).

This information, which is transmitted to recipients based outside the
European Union, is intended to: 

-  allow courses to be monitored,
-  allow participation in educational activities and evaluations and
   assessments,
-  allow the issuance of official documents and/or certificates;
-  conduct research to produce statistics relying on anonymized data. 

We have taken the following steps to ensure that the collected data, if
transferred, receives an adequate level of protection: 

-  The fact that information will be transferred to a third country has
   been mentioned in a notification filed with the CNIL, stating that
   the transferred data will be afforded a similar level of protection
   as required within the European Union, and has been specified in the
   EC Standard Contractual Clauses entered into between FUN and each
   higher education institution established in a country not ensuring an
   **adequate** level of **data protection** (data controller to data
   controller model contract - 2001 version). 

-  The fact that data will be transferred to US-based data processors
   proctoring certification exams (ProctorU) has been mentioned in a
   notification filed with the CNIL and has been specified in the EC
   Standard Contractual Clauses entered into between FUN and Proctor U
   (data controller to data processor model contract). 

Retention Period   
-------------------

Data will be retained and used as follows: 

1. Personally identifiable data collected through each connection to the
   `Site <https://www.fun-mooc.fr/>`__ will be retained for a five-year
   period commencing on the user’s most recent activity on the
   `Site <https://www.fun-mooc.fr/>`__. At the close of such statutory
   data-retention period, data allowing the user to be identified will
   be anonymized, i.e. the User Last Name, First Name, email and user
   name.
2. Data relating to learners wishing to take the proctored examination
   will be retained by the data processor vendor as follows:  
3. Last Name, first name, address, city, telephone number, time zone,
   country: one year. 
4. Video and audio recording of the examination session, photo of the
   learner taken at the start of the examination session, photo of the
   piece of ID: 6 weeks. 

Use of Cookies  
----------------

Certain data is collected by using cookies (small text files saved by
your web browser onto your computer, in which personal information is
stored about you and your page activity, which can be consulted by the
`Site <https://www.fun-mooc.fr/>`__). 

A cookie does not make it possible for us to identify you. Generally
speaking, it records information about your computer’s browsing activity
on our `Site <https://www.fun-mooc.fr/>`__ (the pages that you have
visited, the date and time of your visit, etc.), which we can read
during subsequent visits. That is, it contains information that you have
supplied. As a result, during your next visit, there is no need for you
to fill out the form that is presented at the onset. 

Please note that you may block cookies through your browser settings (in
the Tools->Internet Options' menu item on browsers such as Mozilla
Firefox or Microsoft Explorer). Most browsers provide instructions for
blocking cookies under the "help" function on the toolbar. You can set
your browser to alert you when a cookie or cookies are being sent to
your device and allow you, should you so wish, to refuse them. (See the
following website address for full details:
`www.cnil.fr <http://www.cnil.fr/>`__.) If you disable or refuse
cookies, you may not be able to access some parts of the
`Site <https://www.fun-mooc.fr/>`__, and some features may not function
properly or be available to you. 

Links to other websites  
-------------------------

This Privacy Policy applies only to our
`site <https://www.fun-mooc.fr/>`__ at https://www.fun-mooc.fr/, which
may, however, include links to third party websites offering services
supplied by other content providers. We do not control such linked
services and are not responsible for their content. Nor are we
responsible for the collection, use or disclosure of any information
those services may collect. We advise you to carefully read the privacy
statements and policies of such third-party websites prior to the use of
any third-party website.

User Names and Postings  
-------------------------

Comments or other information posted by you to our forums, wikis, or
other areas of the `Site <https://www.fun-mooc.fr/>`__ designed for
public communications may be viewed and downloaded by others who visit
the `Site <https://www.fun-mooc.fr/>`__. For this reason, we encourage
you to use discretion when deciding whether to post to those forums (or
to other public or course-wide areas) any information that can be used
to identify you.

Site Hosting, storage and security  
------------------------------------

The `Site <https://www.fun-mooc.fr/>`__ is hosted on the cloud platform
operated by Orange Cloud for Business, relying on OpenStack. Technology.
The hosting provider agrees that, on matters of data security. it will
abide by the general security guidelines set forth in the framework
agreement of the French Network and Information Security Agency
(`référentiel de
l'ANSSI <http://www.ssi.gouv.fr/uploads/2016/03/Referentiel_exigences_prestataires_integration_maintenance_V1_0.1.pdf>`__\ `) <http://www.ssi.gouv.fr/uploads/2016/03/Referentiel_exigences_prestataires_integration_maintenance_V1_0.1.pdf>`__. 

Data archiving is conducted at regular intervals, in accordance with the
Privacy Policy. At the close of the statutory data-retention period, the
retained data will be will be anonymized, pursuant to the terms of the
notification filed with CNIL. 

Computerized records stored on systems in accordance with standard
security requirements shall be considered to constitute proof of email
communications, registration form submissions, content and comment
postings, content uploading, as well as content and comment postings.

Registration forms are archived on reliable and durable media so as to
serve as faithful and durable copies, in accordance with legal
requirements. Accordingly, you agree that, in the event of a discrepancy
between our `Site <https://www.fun-mooc.fr/>`__\ ’s computer records and
any paper or electronic documents in your possession, our computer
records shall be authoritative.

Furthermore, you acknowledge that you are fully aware that, although our
security procedures are continually enhanced as new technology becomes
available, FUN cannot guarantee against any unauthorized access and/or
intrusions into the `site <https://www.fun-mooc.fr/>`__\ ’s servers, nor
can it guarantee against any accidental or intentional destruction,
modification, manipulation, tampering and/or hacking of a user’s
comments by another user or by any other person, notably in the event of
data or computer misuse involving a computer virus or another harmful
code or programming instruction adversely affecting the
`site <https://www.fun-mooc.fr/>`__ and/or any comment published on the
`Site <https://www.fun-mooc.fr/>`__.

Legal notices and disclaimers 
==============================

All courses offered on the `Site <https://www.fun-mooc.fr/>`__ have been
created by professors, researchers, scholars or other academic faculty
at institutions of Higher Learning and Research organizations or by
experts from partner institutions or establishments.

The course catalog is continually expanding as an array of training
programs and learning modules are added to meet broadening public
interest.

Website Editor 
---------------

| **GIP FUN-MOOC **
| 12 Villa de Lourcine 
| 75014 Paris 

Contact: \ communication@fun-mooc.fr

Publishing Director
-------------------

| Catherine Mongenet
| Director of GIP FUN-MOOC 

Hosting Provider 
-----------------

| Orange
| Cloud for Business 

Statistics Manager 
-------------------

Google Analytics

Your right to access, modify or delete personal data 
-----------------------------------------------------

In accordance with Articles 39 *et seq*. of Law n° 78-17, dated January
6, 1978, on French Data Protection and Freedom of Information, you have
the right to access, or, where appropriate, modify, or delete personal
data that concerns you. These rights may be exercised upon simple
written request mailed to the following address:

| GIP-FUN MOOC 
| Correspondante Informatique et Liberté 
| 12 Villa de Lourcine 75014 Paris  

You can unsubscribe from our general newsletters by clicking the
unsubscribe link or by sending an unsubscribe request to our e-mail
address or via postal mail.

For all questions or inquiries regarding our Privacy Policy, please
e-mail us at the following address: \ cil@fun-mooc.fr.

For all other questions, please visit our contact page.  For all other
questions, please visit our contact page. 

A new request for an opinion regarding this website has been filed with
the French Data Protection Authority, *Commission Nationale de
l'Informatique et des Libertés* (CNIL).  

The previous request for a CNIL opinion (Decision n° 2014-036, dated 23
January 2014) was the subject of a decree issued by the French Ministry
of National Education, dated 24 September 2014.

Credits 
--------

FUN `site <https://www.fun-mooc.fr/>`__ uses Open edX technology.

The project is covered by an
 `AGPL <https://gipfunmooc-my.sharepoint.com/personal/angele-lydie_kande_fun-mooc_fr/Documents/Pièces%20jointes%20de%20courrier/AGPL>`__ license,
which is viewable at the following address: \ https://github.com/openfun

| Hosting provider: Orange, Cloud for Business, 75015 Paris - France
| Graphic Charter: S.Q.L.I. Group, 268, avenue du Président Wilson -
  93210 Saint-Denis 

*Effective Date: October 28*\ :sup:`*th*`\ * 2013*

*Most recent update: June 13*\ :sup:`*th*`\ * 2017*

The processing is pending review by the CNIL.
"""

LICENCE_FR="""
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
    new = TermsAndConditions(name=last.name,
        version = last.version + ".2",
    )
    new.save()
    print "used %s with id %r as a template" % (last, last.id)
    print "%s created with id %r" % (new, new.id)
    new.texts.add(
        TranslatedTerms(
            tr_text = LICENCE_FR,
            language = "fr",
        )
    )
    new.texts.add(
        TranslatedTerms(
            tr_text = LICENCE_EN,
            language = "en",
        )
    )
    new.save()

class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial',),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslatedTerms',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tr_text', models.TextField(default=b"\n.. Ce champs est dans un format ReST (comme un wiki)\n.. Ceci est un commentaire\n.. http://deusyss.developpez.com/tutoriels/Python/SphinxDoc/#LIV-G\n\n\n.. Les 4 lignes finales (honor, privacy, tos, legal)\n.. permettent la navigation dans le contrat au niveau des ancres\n.. Pri\xc3\xa8re de les ins\xc3\xa9rer avant les titres correspondant\n.. honor = Charte utilisateurs\n.. privacy = Politique de confidentialit\xc3\xa9\n.. tos = Conditions g\xc3\xa9n\xc3\xa9rales d'utilisation\n.. legal =  Mentions l\xc3\xa9gales\n\n.. Ces commentaires ci dessus peuvent \xc3\xaatre retir\xc3\xa9s\n.. ils sont juste l\xc3\xa0 comme aide m\xc3\xa9moire :)\n\n\n.. _honor:\n\n.. _privacy:\n\n.. _tos:\n\n.. _legal:\n\n", verbose_name='Terms and conditions. (ReStructured Text)')),
                ('language', models.CharField(default={'french': b'fr'}, max_length=5, verbose_name='Language', choices=[(b'fr', b'Fran\xc3\xa7ais'), (b'en', b'English'), (b'de-de', b'Deutsch')])),
            ],
        ),
        migrations.AlterModelOptions(
            name='termsandconditions',
            options={'ordering': ('-datetime',), 'verbose_name': 'Terms and conditions', 'verbose_name_plural': 'Terms and conditions'},
        ),
        migrations.AlterField(
            model_name='termsandconditions',
            name='datetime',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Acceptance date', db_index=True),
        ),
        migrations.AlterField(
            model_name='termsandconditions',
            name='name',
            field=models.CharField(default=b'verified_certificate', max_length=100, verbose_name='Name', db_index=True),
        ),
        migrations.AddField(
            model_name='translatedterms',
            name='term',
            field=models.ForeignKey(related_name='texts', to='payment.TermsAndConditions'),
        ),
        migrations.AlterUniqueTogether(
            name='translatedterms',
            unique_together=set([('term', 'language')]),
        ),
        migrations.RunPython(add_new_lience),
    ]


