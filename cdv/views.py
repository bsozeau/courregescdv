from django.shortcuts import render
import random

# Create your views here.
from django.http import HttpResponse

from django.http import FileResponse, Http404

from cdv.models import Post
from django import forms

import os
from pyairtable import Table
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT

from reportlab.platypus import Paragraph, SimpleDocTemplate

from reportlab.lib.units import inch
import textwrap


# Registered font family
pdfmetrics.registerFont(TTFont('Graphik-Regular', 'cdv/dev/Graphik-Regular.ttf'))
# Registered fontfamily
registerFontFamily('Graphik-Regular',normal='Graphik-Regular')



def draw_paragraph(canvas, msg, x, y, max_width, max_height):
	message_style = ParagraphStyle(
		name='Normal',
		fontName='Graphik-Regular',
		alignment=TA_CENTER,
		leading=10,
		fontSize=7,
	#	backColor= "#2cDf2f"
	)
	message = msg.replace('\n', '<br />')
	message = Paragraph(message, style=message_style)
	w, h = message.wrap(max_width, max_height)
	message.drawOn(canvas, x, y - h)


teamMember = Table('keyUn385Sk8pP3Am7', 'appddWm2tbNXoJu09', 'Team Courrèges')



def pdf_view(request):
    try:
        return FileResponse(open('foobar.pdf', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


def cdv_index(request):
	posts = Post.objects.order_by('-id')
	context = {
		"posts": posts,
	}
	return render(request, "index.html", context)

def submit(request):
	result = {}
	resultbin = []
	if request.method == 'POST':


		for records in teamMember.iterate(page_size=100, max_records=1000,view='By Org group' ):
			for item in records:
		
		
				Nom = item['fields']['Nom']
				Titre = item['fields']['Titre']
				Email = item['fields']['Email']
				Fixe = ''
				Portable = ''
				if 'Poste fixe' in item['fields']:
					Fixe = 'T'+item['fields']['Poste fixe']
				if 'Portable' in item['fields']:
					Portable = 'M'+item['fields']['Portable']
				Adresse = "40 rue François I<font size=5><super>er</super></font>, 75008 Paris"


				profilHtml = '<div class="profil">'
				profilHtml += '<div class="profilpic" style="width: 160px;height: 160px;border-radius: 200px;background-size: cover;background-image:url('
				profilHtml += item['fields']['Trombi'][0]['thumbnails']['large']['url']
				profilHtml += ')"></div>'
				profilHtml += '<div>'+Nom+'</div></div>'


		
				packet = io.BytesIO()
		
				# create a new PDF with Reportlab
				can = canvas.Canvas(packet, pagesize=letter)
		
		
		
				contentText = str(Nom)+'<br />'+str(Titre)+'<br /><br />'+str(Email)+'<br />'
				if len(Fixe) > 1:
					contentText += str(Fixe)+'<br />'
		
				if len(Portable) > 1:
					contentText += str(Portable)+'<br />'
		
				contentText += '<br />'
				contentText += str(Adresse)
		
		
				draw_paragraph(can, contentText,40, 232, 120, 500)
		
		
		
				can.save()
		
				#move to the beginning of the StringIO buffer
				packet.seek(0)
				new_pdf = PdfFileReader(packet)
		
				# read your existing PDF
				existing_pdf = PdfFileReader(open("cdv/dev/cdv_empty.pdf", "rb"),strict=False)
				output = PdfFileWriter()
		
				# add the "COURREGES" (which is the new pdf) on the existing page
				page = existing_pdf.getPage(0)
				page.mergePage(new_pdf.getPage(0))
				output.addPage(page)
		
				# add the "watermark" (which is the new pdf) on the existing page
				page2 = existing_pdf.getPage(1)
				output.addPage(page2)
		
				# finally, write "output" to a real file
				outputStream = open('media/cdv_'+Email.split('@')[0].replace('.','_').lower()+'.pdf', "wb+")
				output.write(outputStream)
				outputStream.close()
				resultbin.append('<a target="_blank" href="media/cdv_'+Email.split('@')[0].replace('.','_').lower()+'.pdf">'+profilHtml+'</a>')

		result = { 'resultbin' : ' '.join(resultbin) }
	return render(request, "submit.html",result )