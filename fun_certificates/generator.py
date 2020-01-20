# -*- coding: utf-8 -*-
import datetime
import os

from django.conf import settings
from django.utils.translation.trans_real import translation

from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))
FONT_FILE = os.path.join(CURRENT_DIR, 'Arial.ttf')
pdfmetrics.registerFont(TTFont("Arial", FONT_FILE))

### Variables ###


width, height = landscape(A4) # width and height of A4 Landscape format

marginX, marginY = 0, 0

titleX, titleY = 3.57*cm + 100, 9.95*cm + 100

nameX, nameY = 2.17*cm + 100, 7.71*cm + 100

mainContentX, mainContentY = 2.17*cm + 100, 7.04*cm + 100

dateX, dateY = 2.17*cm + 100, 3.74*cm + 100

legalMentionsX, legalMentionsY = 2.17*cm + 100, 0.8*cm + 105

logoX, logoY = 2.17*cm + 100, 11.6*cm + 100

logoOrganizationX, logoOrganizationY = 18*cm + 100, 11.6*cm + 100

listProfessorsX, listProfessorsY = width - 150, height - 190

URLFunX, URLFunY = 100 + 7.57*cm, 2.25*cm + 100

MoocX, MoocY = 2.17*cm + 100, 1.47*cm + 100

#################

class CertificateInfo(object):

    def __init__(
        self, full_name, course_name,
        organization,
        filename, teachers, language
    ):
        self.full_name = full_name
        self.course_name = course_name
        self.organization = organization
        self.filename = filename
        self.teachers = teachers
        self._ = translation(language if language else "fr").ugettext

    @property
    def organization_logo(self):
        if self.organization and self.organization.certificate_logo:
            return os.path.join(self.organization.certificate_logo.url,
                                self.organization.certificate_logo.path)
        return None

    @property
    def organization_name(self):
        return self.organization.name or ""

    @property
    def pdf_file_name(self):
        return os.path.join(settings.MEDIA_ROOT, settings.CERTIFICATES_DIRECTORY_NAME, self.filename)

    @property
    def organizationNameTooLong(self):
        return len(self.organization_name) > 33

    @property
    def courseNameTooLong(self):
        return len(self.course_name) > 33

    def generate(self):
        c = self.get_prepared_canvas()

        self.write_full_name(c)
        self.write_main_content(c)
        self.write_legal_mentions(c)
        self.write_fun_logo(c)
        self.write_organization_logo(c)
        self.write_professor_list(c)
        self.write_fun_url(c)
        self.write_mooc(c)

        c.showPage()
        c.save()

    def get_prepared_canvas(self):
        c = canvas.Canvas(self.pdf_file_name, pagesize=landscape(A4))

        #border
        c.setStrokeColorRGB(221./256, 221./256, 221./256)
        c.setLineWidth(cm * 0.13)
        c.rect(100, 100, cm * 23.84, cm * 15)

        #title
        textobject = c.beginText()
        textobject.setTextOrigin(titleX, titleY)
        textobject.setFont("Arial", 24)
        textobject.setFillColorRGB(59./256, 118./256, 188./256)

        textobject.textLine(self._("ATTESTATION OF ACHIEVEMENT"))
        c.drawText(textobject)

        c.setFillColorRGB(221./256, 221./256, 221./256)
        if (self.organizationNameTooLong):
            if (self.courseNameTooLong):
                c.rect(100, 2.43*cm + 100, 400, 6.41*cm, fill=1, stroke=0)
                c.rect(cm*22.6+100, 2.43*cm+100, 1.24*cm, 6.41*cm, fill=1, stroke=0)
            else:
                c.rect(100, 2.73*cm + 100, 400, 6.11*cm, fill=1, stroke=0)
                c.rect(cm*22.6 + 100, 2.73*cm + 100, 1.24*cm, 6.11*cm, fill=1, stroke=0)
        else:
            c.rect(100, 3.23*cm+100, 400, 5.61*cm, fill=1, stroke=0)
            c.rect(cm*22.6 + 100, 3.23*cm + 100, 1.24*cm, 5.61*cm, fill=1, stroke=0)

        return c

    def write_full_name(self, c):
        textobject = c.beginText()
        textobject.setTextOrigin(nameX, nameY)
        textobject.setFont("Arial", 24)
        textobject.setFillColorRGB(0, 0, 0)
        textobject.textLine(self.full_name)
        c.drawText(textobject)

    def write_main_content(self, c):
        textobject = c.beginText()
        textobject.setTextOrigin(mainContentX, mainContentY)
        textobject.setFont("Arial", 16)
        textobject.setFillColorRGB(127./256, 127./256, 127./256)
        textobject.textOut(self._("has successfully completed the MOOC"))
        textobject.setFillColorRGB(59./256, 118./256, 188./256)
        textobject.textLine("*")

        textobject.setFillColorRGB(0, 0, 0)
        textobject.moveCursor(0, 10)
        if (self.courseNameTooLong):
            indexReturnLine = self.course_name.rfind(" ", 0, 43)
            textobject.textLine(self.course_name[:indexReturnLine])
            textobject.textLine(self.course_name[indexReturnLine+1:])
        else:
            textobject.textLine(self.course_name)

        textobject.setFillColorRGB(127./256, 127./256, 127./256)
        if (self.organizationNameTooLong):
            indexReturnLine = self.organization_name.rfind(" ", 0, 33)
            textobject.textOut(self._("proposed by "))
            textobject.setFillColorRGB(0, 0, 0)
            textobject.textLine(self.organization_name[:indexReturnLine])
            textobject.textLine(self.organization_name[indexReturnLine+1:])
        else:
            textobject.textOut(self._("proposed by "))
            textobject.setFillColorRGB(0, 0, 0)
            textobject.textLine(self.organization_name)
        textobject.setFillColorRGB(0, 0, 0)

        textobject.setFillColorRGB(127./256, 127./256, 127./256)
        textobject.textOut(self._("and published on the platform "))
        textobject.setFillColorRGB(0, 0, 0)
        textobject.textLine(self._("FUN"))
        textobject.setFillColorRGB(59./256, 118./256, 188./256)
        textobject.textLine(datetime.date.today().strftime(self._("On the %m/%d/%Y")))
        c.drawText(textobject)

    def write_legal_mentions(self, c):
        textobject = c.beginText()
        textobject.setTextOrigin(legalMentionsX, legalMentionsY)
        textobject.setFont("Arial", 8)
        textobject.setFillColorRGB(0, 0, 0)

        textobject.textLine(self._("The current document is not a degree or diploma and does not award credits (ECTS)."))
        textobject.textLine(self._("It does not certify that the learner was registered with {}.").format(self.organization_name))
        textobject.textLine(self._("The learner's identity has not been verified."))

        c.drawText(textobject)

    def write_fun_logo(self, c):
        c.drawImage(
            settings.FUN_ATTESTATION_LOGO_PATH,
            logoX, logoY, width=170, height=77, mask='auto')

    def write_organization_logo(self, c):
        if self.organization_logo:
            c.drawImage(self.organization_logo, logoOrganizationX, logoOrganizationY, width=140, height=80, mask='auto')

    def write_professor_list(self, c):
        c.setFont("Arial", 16)
        c.setFillColorRGB(59./256, 118./256, 188./256)
        c.drawRightString(100+21.70*cm, 100+8.40*cm, self._("Instructors"))
        y = 7.5
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Arial", 12)
        for teacher in self.teachers:
            teacherNameAndJob = teacher.split("/")
            teacherName = teacherNameAndJob[0]
            teacherJob = teacherNameAndJob[1]
            c.setFillColorRGB(0, 0, 0)
            c.drawRightString(100+21.70*cm, 100+y*cm, teacherName)
            c.setFillColorRGB(127./256, 127./256, 127./256)
            c.drawRightString(100+21.70*cm, 100+(y-0.53)*cm, teacherJob)
            y = y-1.24

    def write_fun_url(self, c):
        textobject = c.beginText()
        if self.organizationNameTooLong:
            textobject.setTextOrigin(URLFunX, URLFunY-10)
        else:
            textobject.setTextOrigin(URLFunX, URLFunY)
        textobject.setFont("Arial", 12)
        textobject.setFillColorRGB(59./256, 118./256, 188./256)
        textobject.textLine(u"https://www.fun-mooc.fr")
        c.drawText(textobject)

    def write_mooc(self, c):
        textobject = c.beginText()
        textobject.setTextOrigin(MoocX, MoocY)
        textobject.setFont("Arial", 8)
        textobject.setFillColorRGB(59./256, 118./256, 188./256)
        textobject.textOut("* ")
        textobject.setFillColorRGB(127./256, 127./256, 127./256)
        textobject.textLine(self._("MOOC: Massive Open Online Course"))
        c.drawText(textobject)

