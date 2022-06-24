import os
import io
import random

from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse, Http404
from django import forms
from cdv.models import Post

from pyairtable import Table
from PyPDF2 import PdfFileWriter, PdfFileReader
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
def deep_get(d, keys):
	if not keys or d is None:
		return d
	return deep_get(d.get(keys[0]), keys[1:])

def cdv_index(request):
	posts = Post.objects.order_by('-id')
	context = {
		"posts": posts,
	}
	return render(request, "index.html", context)

teamMember = Table('keyUn385Sk8pP3Am7', 'appddWm2tbNXoJu09', 'Team Courrèges')
departements = Table('keyUn385Sk8pP3Am7', 'appddWm2tbNXoJu09', 'Départements')
departementsNames = {}
departementsSize = {}
managerNames = {}
peopleNames = {}

# Registered font family
pdfmetrics.registerFont(TTFont('Graphik-Regular', 'cdv/dev/Graphik-Regular.ttf'))
registerFontFamily('Graphik-Regular',normal='Graphik-Regular')

def submit(request):
	result = {}
	resultbin = []
	deptList = []
	for records in departements.iterate(page_size=100, max_records=1000):
		for item in records:
			departementsNames[item['id']] = item['fields']['Name']

	if request.method == 'POST':
		for records in teamMember.iterate(page_size=100, max_records=1000,view='Assets',sort=['Départment', 'Reporting to'] ):
			for item in records:

				Nom = ''
				Titre = ''
				Email = ''
				Depart = ''
				Fixe = ''
				Portable = ''
				Trombi = ''

				if 'Nom' in item['fields']:
					Nom = item['fields']['Nom']

				if 'Titre' in item['fields']:
					Titre = item['fields']['Titre']

				if 'Email' in item['fields']:
					Email = item['fields']['Email']


				if 'Poste fixe' in item['fields']:
					Fixe = 'T'+item['fields']['Poste fixe']

				if 'Portable' in item['fields']:
					Portable = 'M'+item['fields']['Portable']

				if 'Départment' in item['fields']:
					Depart = departementsNames[ str(item['fields']['Départment'][0]) ]

				if 'Trombi' in item['fields']:
					Trombi = item['fields']['Trombi'][0]['thumbnails']['large']['url']

				if 'Adresse' in item['fields']:
					Adresse = item['fields']['Adresse']
					if Adresse == '40 rue François Ier, 75008 Paris' :
						Adresse = "40 rue François I<font size=5><super>er</super></font>, 75008 Paris"
					if Adresse == 'Ier étage – 40 boulevard Haussmann 75009' :
						Adresse = "I<font size=5><super>er</super></font> étage – 40 boulevard Haussmann, 75009 Paris"

				if Depart not in deptList:
					resultbin.append('<div class="dept" style="margin-top: 3em;"><h4>'+Depart+'</h4></div>')
				deptList.append(Depart)

				profilHtml = '<div class="profil">'
				profilHtml += '<div class="profilpic" style="width: 160px;height: 160px;border-radius: 200px;background-size: cover;background-image:url('
				profilHtml += Trombi
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
				if Nom != 'Christelle Guerniou':
					resultbin.append('<a target="_blank" href="media/cdv_'+Email.split('@')[0].replace('.','_').lower()+'.pdf">'+profilHtml+'</a>')

		result = { 'resultbin' : ' '.join(resultbin) }
	return render(request, "submit.html",result )

def cdv_orga(request):

	for records in departements.iterate(page_size=100, max_records=1000,sort=['Chart order'] ):
		for item in records:
			if item['fields']['Name'] != 'Lectra':
				if item['fields']['Name'] != 'Image':
					if item['fields']['Name'] != 'Collection / Production':
						if item['fields']['Name'] != 'Boutique':
							departementsNames[item['id']] = item['fields']['Name']
							departementsSize[item['id']] = item['fields']['Overall team size']

	deptList = []

	contentHtml = '''
<div style="position:fixed; top:0;width:100%; height:100vh;" id="orga"/>
	<div style="width:100%; height:100vh;" id="tree"/></div>
</div>
<script type="text/javascript"">
	OrgChart.templates.myTemplate = Object.assign({}, OrgChart.templates.ula);
	OrgChart.templates.myTemplate.size = [180, 300];
	OrgChart.templates.myTemplate.img_0 = '<clipPath id="{randId}"><circle cx="90" cy="90" r="80"></circle></clipPath>'
		+ '<image preserveAspectRatio="xMidYMid slice" clip-path="url(#{randId})" xlink:href="{val}" x="0" y="0" width="170" height="170"></image>';
	OrgChart.templates.myTemplate.nodeMenuButton =
	'<g style="cursor:pointer;" transform="matrix(1,0,0,1,155,250)" data-ctrl-n-menu-id="{id}">'
	+ '<rect x="-4" y="-10" fill="#000000" fill-opacity="0" width="22" height="22">'
	+ '</rect>'
	+ '<line x1="0" y1="0" x2="0" y2="3" stroke-width="3" stroke="rgb(200, 200, 200)" />'
	+ '<line x1="7" y1="0" x2="7" y2="3" stroke-width="3" stroke="rgb(200, 200, 200)" />'
	+ '<line x1="14" y1="0" x2="14" y2="3" stroke-width="3" stroke="rgb(200, 200, 200)" />'
	+ '</g>';
	OrgChart.templates.group.min = Object.assign({}, OrgChart.templates.group);
	OrgChart.templates.group.min.imgs = "{val}";
	OrgChart.templates.group.min.img_0 = "";
	OrgChart.templates.group.min.description = '<text data-width="230" data-text-overflow="multiline" style="font-size: 14px;" fill="#aeaeae" x="125" y="100" text-anchor="middle">{val}</text>';
	OrgChart.templates.myTemplate.node = '<rect x="0" y="0" height="{h}" width="{w}" fill="#ffffff" stroke-width="1" stroke="#aeaeae" rx="4" ry="4"></rect>'
	+ '<rect x="5" y="266" height="20" width="170" fill="#e1e1e1" stroke-width="0" stroke="#039BE5"></rect>'
	OrgChart.templates.myTemplate.field_0 = '<text style="font-size: 15px;" data-width="170" data-text-overflow="multiline" fill="#000" x="10" y="200" text-anchor="left" class="card_text">{val}</text>';
	OrgChart.templates.myTemplate.field_1 = '<text style="font-size: 12px;" data-width="170" data-text-overflow="multiline" fill="#000" x="10" y="220" text-anchor="left" class="card_text card_text-titre">{val}</text>';
	OrgChart.templates.myTemplate.field_2 = '<text style="font-size: 10px;" data-width="180" data-text-overflow="multiline" fill="#000" x="10" y="280" text-anchor="left" class="card_text card_text-dept">{val}</text>';
	OrgChart.scroll.smooth = 12;
	OrgChart.scroll.speed = 20;
	OrgChart.LINK_ROUNDED_CORNERS = 20;
	OrgChart.templates.myTemplate.link = '<path stroke-linejoin="round" stroke="#aeaeae" stroke-width="1px" fill="none" d="{rounded}" />';

	var chart = new OrgChart(document.getElementById("tree"), {
		template: "myTemplate",
		scaleInitial: 0.5,
//		scaleInitial: OrgChart.match.width,
		enableSearch: true,
		enableDragDrop: true,
		filterBy: ['dept'],
		orderBy: "myOrderId",
		levelSeparation: 41,
		mouseScrool: OrgChart.action.scroll,
		showYScroll: OrgChart.scroll.visible,
		showXScroll: OrgChart.scroll.visible,
		toolbar: {
			zoom: true,
		},
		nodeMenu: {
			details: { text: "Details" },
			edit: { text: "Edit" },
			remove: { text: "Remove" }
		},
		menu: {
			pdfPreview: {
				text: "PDF Preview",
				icon: OrgChart.icon.pdf(24, 24, '#7A7A7A'),
				onClick: preview
			},
//			pdf: { text: "Export PDF" }
		},
		editForm: {
			buttons:  {
				pdf: null,
				share: null
			},
			generateElementsFromFields: false,
			elements: [
				{ type: 'textbox', label: 'Nom', binding: 'name'},
				{ type: 'textbox', label: 'Titre', binding: 'title'},
				{ type: 'textbox', label: 'Departement', binding: 'deptartement'}
			]
		},
		nodeBinding: {
			imgs: "img",
			field_0: "name",
			field_1: "title",
			field_2: "deptartement",
			img_0: "img"
		},
		tags: {
			"assistant": {
				template: "myTemplate"
			},
			filter: {
				template: 'dot'
			},
	'''

	for id, dept in departementsNames.items():
		contentHtml += '"'+''.join(x for x in dept if x.isalnum())+'''-group": {
				template: "group",
				subTreeConfig: {
					siblingSeparation: 10,
					columns: 
					'''
#		if int(departementsSize[id]) > 20 :
#			contentHtml += str( int(int(departementsSize[id])/2) )
#		else:
		contentHtml += str( (int(departementsSize[id])) ) 
		contentHtml += '''
				}
			},'''
	contentHtml += '//'+str(departementsNames)+'\n'
	contentHtml += '''
		"Image-group": {
				template: "group",
				subTreeConfig: {
					siblingSeparation: 10,
					columns: 
					2
				}
			},
		},
		slinks: [
			{ from: 22, to: 15, template: 'blue', label: '' },
		],
		nodes: [
'''
	count = 0
	for records in teamMember.iterate(page_size=100, max_records=1000, view='Assets',sort=['Reporting to']  ):
		for item in records:
			count = count+1

			if 'Nom' in item['fields']:
				Nom = item['fields']['Nom']

			if "Courrèges" not in Nom:
				if 'Départment' in item['fields']:
					Depart = departementsNames[ str(item['fields']['Départment'][0]) ]
			
				if "Boutique" not in Depart:


					managerNames[item['id']] = {}
					managerNames[item['id']]['name'] = item['fields']['Nom']
					if 'Reporting to' in item['fields']:
						managerNames[item['id']]['report'] = item['fields']['Reporting to'][0]
					else : 
						managerNames[item['id']]['report'] = ''

					if 'Départment' in item['fields']:
						managerNames[item['id']]['dept'] = departementsNames[ str(item['fields']['Départment'][0]) ]
									
					managerNames[item['id']]['id'] = count
		
					peopleNames[item['fields']['Nom']] = {}
					peopleNames[item['fields']['Nom']]['id'] = count
					peopleNames[item['fields']['Nom']]['airId'] = item['id']
			
	totalMember = count
	totalMemberFreeze = count+1
	count = 0
	contentHtml += '//'+str(managerNames)+'\n'
	contentHtml += '//'+str(peopleNames)+'\n'
	
	
	for records in teamMember.iterate(page_size=100, max_records=1000, view='Assets',sort=['Reporting to'] ):
		for item in records:

			if 'Nom' in item['fields']:
				Nom = item['fields']['Nom']

			if "Courrèges" not in Nom:
			
				if 'Départment' in item['fields']:
					Depart = departementsNames[ str(item['fields']['Départment'][0]) ]

				if "Archives" not in Depart :

					if 'Départment' in item['fields']:
						Depart = departementsNames[ str(item['fields']['Départment'][0]) ]
		
					if Depart not in deptList:
						totalMember = totalMember+1
						count = count+1

						if "Direction" not in Depart:
	
							contentHtml += '{ id: '+str(totalMember)+','
							if Nom == 'Carmen Druais':
								contentHtml += 'pid: 18, '
							else:
								if 'Reporting to' in item['fields']:
									contentHtml += 'pid: '+str(peopleNames[ str(item['fields']['Nom'])]['id'] )+', '
							contentHtml += 'myOrderId : '+str(count)+', name : "'+str(Depart)+'", tags:["'+str(''.join(x for x in Depart if x.isalnum()))+'-group", "group"] },\n'
		
					deptList.append(Depart)

	deptList = []

	contentHtml += '{ id: 0, pid: 13, myOrderId : 0, name : "Image", tags:["Image-group", "group"] },'


	#sort=['Départment', 'Reporting to']
	for records in teamMember.iterate(page_size=100, max_records=1000, view='Assets',sort=['Org Chart Group'] ):
		for item in records:
			count = count+1
			Nom = ''
			Titre = ''
			Email = ''
			Depart = ''
			Fixe = ''
			Portable = ''
			reportingToID = ''
			reportingToName = ''
			reportingTo = ''
			reportingToDept = ''
			reportingToManagerAirID = ''
			reportingToManagerName = ''
			if 'Nom' in item['fields']:
				Nom = item['fields']['Nom']

			if 'Titre' in item['fields']:
				Titre = item['fields']['Titre']

			if 'Email' in item['fields']:
				Email = item['fields']['Email']


			if 'Poste fixe' in item['fields']:
				Fixe = 'T'+item['fields']['Poste fixe']

			if 'Portable' in item['fields']:
				Portable = 'M'+item['fields']['Portable']

			if "Courrèges" not in Nom:
	
				if 'Départment' in item['fields']:
					Depart = departementsNames[ str(item['fields']['Départment'][0]) ]
					departRef = int(totalMemberFreeze) + int(list(departementsNames.values()).index(Depart))
	
				if "Boutique" not in Depart:
					if 'Reporting to' in item['fields']:
						reportingToID = item['fields']['Reporting to'][0]
						reportingTo = str(managerNames[reportingToID]['id'] )

						reportingToName = str(managerNames[reportingToID]['name'] )
						reportingToDept = str(managerNames[reportingToID]['dept'] )

						if Nom != 'Adrien Da Maia':
							reportingToManagerAirID = str( managerNames[reportingToID]['report'] )

						if reportingToManagerAirID != '':
							reportingToManagerName = str(managerNames[reportingToManagerAirID]['name']  )
							reportingToManagerId = str(managerNames[reportingToManagerAirID]['id']  )


				if Nom != 'Christelle Guerniou':
					contentHtml += '{ id: '+str(peopleNames[ str(item['fields']['Nom'])]['id'] )+', '
		
					if Depart not in deptList:
						inAGroup = False
					else:
						inAGroup = True
					deptList.append(Depart)
		
		
		
					if Nom == 'Adrien Da Maia':
						relations = ''
					elif Nom == 'Bastien Sozeau':
						relations = 'stpid: 0, '
					elif Nom == 'Isabel Pelaez':
						relations = 'stpid: 0, '
					elif Nom == 'Xavier Landrit':
						relations = 'pid: '+reportingTo+', '
					else :
						if reportingToDept == Depart and reportingToManagerName == 'Adrien Da Maia':
							relations = 'stpid: '+str(departRef)+', '
						elif reportingToDept == Depart and reportingToManagerName == 'Barbara Lozet Lehmann':					
							if reportingToName == 'William Dugain':
								relations = 'stpid: '+str(departRef)+', '
							else:
								relations = 'pid: '+reportingTo+', '
						else :	
							relations = 'pid: '+reportingTo+', '
			
						if inAGroup == True:
							relations += 'inagroup: true, '
	
					contentHtml += relations
	
		
					if Nom == 'Romain Levy':
						contentHtml += 'tags: ["partner"], '
		
			
			
					contentHtml += 'myOrderId : '+str(count)+', '
					contentHtml += 'name : "'+Nom+'", '
					contentHtml += 'title : "'+Titre+'" ,'
					#report to '+str(reportingToName)+' that report to '+str(reportingToManagerName)+'", '
					contentHtml += 'dept : "'+Depart+'", '
					contentHtml += 'deptartement : "'+Depart+'", '
					contentHtml += 'img : "'+str(item['fields']['Trombi'][0]['thumbnails']['large']['url'])+'" },\n'
						
			
	contentHtml += ''']});

	chart.on('drop', function (sender, draggedNodeId, droppedNodeId) {
		var draggedNode = sender.getNode(draggedNodeId);
		var droppedNode = sender.getNode(droppedNodeId);
		
		if (droppedNode.tags.indexOf("group") != -1 && draggedNode.tags.indexOf("group") == -1) {
			var draggedNodeData = sender.get(draggedNode.id);
			draggedNodeData.pid = null;
			draggedNodeData.stpid = droppedNode.id;
			sender.updateNode(draggedNodeData);
			return false;
		}
	 if (draggedNode.level == droppedNode.level){

		var draggedNodeData = sender.get(draggedNodeId);
		var droppedNodeData = sender.get(droppedNodeId);

		var orderID = draggedNodeData.myOrderId;
		draggedNodeData.myOrderId = droppedNodeData.myOrderId;
		droppedNodeData.myOrderId = orderID;
		sender.update(draggedNodeData);
		sender.update(droppedNodeData);
		sender.draw();
		return false; 
	}

	});
	chart.on('field', function (sender, args) {
		if (args.node.min) {
			if (args.name == "img") {
				var count = args.node.stChildrenIds.length > 5 ? 5 : args.node.stChildrenIds.length;
				var x = args.node.w / 2 - (count * 32) / 2;
				for (var i = 0; i < count; i++) {
					var data = sender.get(args.node.stChildrenIds[i]);
					args.value += '<image xlink:href="' + data.img + '" x="' + (x + i * 32) + '" y="45" width="32" height="32" ></image>';
				}
			}
		}
	});
	chart.on('click', function (sender, args) {
		if (args.node.tags.indexOf("group") != -1) {
			if (args.node.min) {
				sender.maximize(args.node.id);
			}
			else {
				sender.minimize(args.node.id);
			}
		}
		return false;
	});
	function preview() {
		let organigrammeHeader = 'Organigramme courrèges';

		var markedCheckbox = document.querySelectorAll('input[type="checkbox"]:checked');

		var len = markedCheckbox.length;
		for (var i=0; i<len; i++) {
			if(markedCheckbox[i].name != 'Direction'){
				organigrammeHeader += ' - ';
				organigrammeHeader += markedCheckbox[i].name;
			}
		}
		
		
		OrgChart.pdfPrevUI.show(chart, {
			format: "A3",
			landscape: 'true',
			header: organigrammeHeader,
			footer: '<svg width="13" height="8" preserveAspectRatio="xMaxYMax meet" id="logoAC" data-name="logoAC" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 665.29 425.2" ><title>logoAC</title><path d="M348.38,425.2V79.09C348.38,30.61,381.54,0,435.12,0H583.65C574.3,31.47,570.9,64.63,570.9,98.93a380.23,380.23,0,0,0,10.2,88.72H492.38c-76,0-112.82,43.66-112.82,98.37,0,71.71,71.15,106,147.12,106,49.89,0,98.64-17,138.61-45.07V425.2Zm-307,0c3.68-47.91,43.37-86.46,91.84-86.46,48.75,0,88.16,38.27,91.84,86.46H327.4V79.09C327.4,30.61,294.24,0,240.66,0H129.26V187.65H270.14c15.31,0,26.08,8.79,26.08,24.38,0,22.11-21.26,30.33-55.27,41.1L103.18,297.07C49,314.36,4.82,358,0,425.2Z"/></svg>'
		});
	}	
	chart.on('exportstart', function (sender, args) {
		args.styles = document.getElementById('myStyles').outerHTML;

	});
	

	</script>
</div>'''

	context = {
		"contentHtml": contentHtml,
	}
	return render(request, "orga.html", context)
