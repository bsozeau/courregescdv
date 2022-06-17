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
	
	
def cdv_orga(request):
	
	teamMember = Table('keyUn385Sk8pP3Am7', 'appddWm2tbNXoJu09', 'Team Courrèges')
	departements = Table('keyUn385Sk8pP3Am7', 'appddWm2tbNXoJu09', 'Départements')
	departementsNames = {}
	managerNames = {}
	peopleNames = {}
	
	
	for records in departements.iterate(page_size=100, max_records=1000):
		for item in records:
			departementsNames[item['id']] = item['fields']['Name']
	
	
	
	contentHtml = '''
		<div id="wrapper">
	        <div style="width:100%; height:100vh;" id="tree"/></div>
		</div>
	<script type="text/javascript"">
	
	//JavaScript
	OrgChart.templates.myTemplate = Object.assign({}, OrgChart.templates.ula);
	OrgChart.templates.myTemplate.size = [180, 300];
	OrgChart.templates.myTemplate.img_0 = '<clipPath id="{randId}"><circle cx="90" cy="90" r="80"></circle></clipPath>'
	    + '<image preserveAspectRatio="xMidYMid slice" clip-path="url(#{randId})" xlink:href="{val}" x="0" y="0" width="170" height="170"></image>';
	
	
	OrgChart.templates.myTemplate.node = '<rect x="0" y="0" height="{h}" width="{w}" fill="#ffffff" stroke-width="1" stroke="#aeaeae" rx="4" ry="4"></rect>'
	+ '<rect x="5" y="266" height="20" width="170" fill="#e1e1e1" stroke-width="0" stroke="#039BE5"></rect>'
	
	
	OrgChart.templates.myTemplate.field_0 = '<text style="font-size: 15px;" data-width="170" data-text-overflow="multiline" fill="#000" x="10" y="200" text-anchor="left" class="card_text">{val}</text>';
	
	OrgChart.templates.myTemplate.field_1 = '<text style="font-size: 12px;" data-width="170" data-text-overflow="multiline" fill="#000" x="10" y="220" text-anchor="left" class="card_text card_text-titre">{val}</text>';
	
	OrgChart.templates.myTemplate.field_2 = '<text style="font-size: 10px;" data-width="180" data-text-overflow="multiline" fill="#000" x="10" y="280" text-anchor="left" class="card_text card_text-dept">{val}</text>';
	
	
	var chart = new OrgChart(document.getElementById("tree"), {
		template: "myTemplate",	
		enableSearch: true,
		enableDragDrop: true, 
		filterBy: ['title', 'dept'],
	 	tags: {
			"assistant": {
				template: "ula"
			},
			filter: {
				template: 'dot'
			},
	        "subLevels0": {
	            subLevels: 0
	        },
	        "subLevels1": {
	            subLevels: 1
	        },
	        "subLevels2": {
	            subLevels: 2
	        },
	        "subLevels3": {
	            subLevels: 3
	        },
	        "subLevels4": {
	            subLevels: 4
	        },
			"subLevels5": {
	            subLevels: 5
	        }
		},
		menu: {
			pdf: { text: "Export PDF" },
			png: { text: "Export PNG" },
			svg: { text: "Export SVG" },
			csv: { text: "Export CSV" }
		},	
		nodeBinding: {
			field_0: "name",
			field_1: "title",
			field_2: "dept",
			img_0: "img"
		},
		tags: { 
	'''
	for id, dept in departementsNames.items():
		contentHtml += '"'+''.join(x for x in dept if x.isalnum())+'''-group": {
	            template: "group",
	            subTreeConfig: {
	            }
	        },'''
	contentHtml += '''
	    },    
	    nodes: [
	'''
	    
	#for id, dept in departementsNames.items():
	#	contentHtml += '''{ id: "'''+''.join(x for x in dept if x.isalnum())+'''", name: "'''+str(dept)+'''", tags: ["'''+''.join(x for x in dept if x.isalnum())+'''-group", "group"], description: "'''+str(dept)+'''" },'''
	
	
	
	count = 1
	for records in teamMember.iterate(page_size=100, max_records=1000):
		for item in records:
			count = count+1
			managerNames[item['id']] = {}
			managerNames[item['id']]['name'] = item['fields']['Nom']
			managerNames[item['id']]['id'] = count
	
	count = 1
	for records in teamMember.iterate(page_size=100, max_records=1000):
		for item in records:
			count = count+1
			peopleNames[item['fields']['Nom']] = {}
			peopleNames[item['fields']['Nom']]['id'] = count
			 
	count = 1
	#sort=['Départment', 'Reporting to']
	for records in teamMember.iterate(page_size=100, max_records=1000,view='By Org group' ):
		for item in records:
			count = count+1
			
			Nom = item['fields']['Nom']
			Titre = item['fields']['Titre']
			Depart = departementsNames[ str(item['fields']['Départment'][0]) ]
			
			contentHtml += '{ id: '+str(peopleNames[ str(item['fields']['Nom'])]['id'] )+', '
			if 'Reporting to' in item['fields']:
				contentHtml += ' pid: '+str(managerNames[ str(item['fields']['Reporting to'][0])]['id'] )+', '
	
	
			if Nom == 'Romain Levy':
				contentHtml += 'tags: ["assistant"], '
			if Nom == 'Christophe Crochet':
				contentHtml += 'tags: ["subLevels2"], '
			contentHtml += 'name : "'+Nom+'", '
			contentHtml += 'title : "'+Titre+'", '
			contentHtml += 'dept : "'+Depart+'", '
			contentHtml += 'stpid : "'+''.join(x for x in Depart if x.isalnum())+'", '
			contentHtml += 'img : "'+str(item['fields']['Trombi'][0]['thumbnails']['large']['url'])+'" }, '
	
	contentHtml += ''']
	});
	</script>
	'''
	
	
	'''		
	
	for records in teamMember.iterate(page_size=100, max_records=1000, sort=['Départment', 'Reporting to']):
		for item in records:
			count = count+1
			
			print( managerNames[ str(item['fields']['Reporting to'][0]) ] )
			contentHtml += '<div class="profil">'
			contentHtml += '<div class="profilpic" style="background-image:url('
			contentHtml += item['fields']['Trombi'][0]['thumbnails']['large']['url']
			contentHtml += ')"></div>'
	
			contentHtml += '<div class="profil-nom">'
			contentHtml += item['fields']['Nom']
			contentHtml += '\n'
	
			contentHtml += '<div class="profil-titre">'
			contentHtml += 'TITRE'
			contentHtml += '\n'
			contentHtml += item['fields']['Titre']
			contentHtml += '\n'
			contentHtml += item['fields']['Email']
			contentHtml += '\n'
	
			contentHtml += '<div class="profil-dep">'
			contentHtml += 'DÉPARTEMENT'
			contentHtml += '\n'
			contentHtml += departementsNames[ str(item['fields']['Départment'][0]) ]
			contentHtml += '</div>'
			contentHtml += '</div>'
	'''
	
	contentHtml += 'Total : '+str(count)+''
	contentHtml += '''</div>
	</body></html>'''
	

	context = {
		"contentHtml": contentHtml,
	}
	return render(request, "orga.html", context)
