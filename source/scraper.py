#https://www.meteogalicia.gal/Caire/visualizarDatosConsulta.action


# python -m pip install selenium
# python -m pip install beautifulsoup4

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import csv


#
# Función establece el valor estacion en el campo Estacións del formulario
# 
def set_browser_field_estacion(browser, estacion):

	if estacion == 'Lalin':
		n = 4
	else: 
		n = 0

	if (n != 0):
		estacion_table = browser.find_element_by_id('estacion')

		action = ActionChains(browser)
		action.click(estacion_table).perform()
	
		for i in range(0, n):
			action.send_keys_to_element(estacion_table, Keys.ARROW_DOWN).perform()
			# action.send_keys_to_element(estacion_table, Keys.DOWN).perform()

		action.send_keys_to_element(estacion_table, Keys.SPACE).perform()

#
# Función establece el valor periodo en el campo Período del formulario
# 
def set_browser_field_periodo(browser, periodo):
	
	periodo_table = browser.find_element_by_id('periodo')

	if periodo =='Diarios':
		
		action = ActionChains(browser)
		action.click(periodo_table).perform()
	
		action.send_keys_to_element(periodo_table, Keys.ARROW_DOWN).perform()
		# action.send_keys_to_element(periodo_table, Keys.DOWN).perform()

		action.send_keys_to_element(periodo_table, Keys.SPACE).perform()

	elif periodo == 'Horarios':
		# valor por defecto
		return
	else: 
		print('La opción escogida para el campo "Periodo" no es valida. Opciones válidas: [Diarios|Horarios]')

#
# Función que a partir de los parámetros estacion, periodo, fecha_desde
# y fecha_hasta obtiene el objeto BeautifulSoup de la página base_url
# 
def getPageSoup(link, estacion, periodo, fecha_desde, fecha_hasta):

	browser = webdriver.Firefox(executable_path='./geckodriver')

	browser.get(link)

	set_browser_field_estacion(browser, estacion)

	set_browser_field_periodo(browser, periodo)

	browser.find_element_by_id("sendButton").click()

	page_soup = BeautifulSoup(browser.page_source, 'html.parser')

	# browser.close()

	return page_soup

#
# Función que scrapea la página para obtener los valores
# de nombre de la estación, fecha y valores y estados
# de los diferentes indicadores
# 
def get_content_values(page_soup):
	
	content = page_soup.find(id = 'resultado')

	header = content.find('div', {'class': 'cabeceraSec'})

	station = header.text.strip()[len('Datos da Estación '):]

	measurements_list = []

	estacion = header.text.strip()[len('Datos da Estación '):]

	tabs = content.find(id = 'tabs')

	table = tabs.find(id='gridview-1037-table').tbody

	rows = table.findAll('tr')

	for row in rows:

		columns = row.findAll('td')

		measurements = {'estacion': estacion}
		measurements['fecha'] 		= columns[0].text
		measurements['SO2-valor'] 	= columns[1].text
		measurements['SO2-estado'] 	= columns[2].text
		measurements['NO-valor'] 	= columns[3].text
		measurements['NO-estado'] 	= columns[4].text
		measurements['NO2-valor'] 	= columns[5].text
		measurements['NO2-estado'] 	= columns[6].text
		measurements['NOX-valor'] 	= columns[7].text
		measurements['NOX-estado'] 	= columns[8].text
		measurements['CO-valor'] 	= columns[9].text
		measurements['CO-estado'] 	= columns[10].text
		measurements['O3-valor'] 	= columns[11].text 
		measurements['O3-estado'] 	= columns[12].text 
		measurements['PM10-valor'] 	= columns[13].text 
		measurements['PM10-estado'] = columns[14].text 
		measurements['PM25-valor'] 	= columns[15].text	
		measurements['PM25-estado'] = columns[16].text 

		measurements_list.append(measurements)

	return measurements_list


#
# Función que vuelca el contenido de la lista list_data al
# fichero de salida csv_file con formato CSV
# 
def to_csv(csv_file, list_data):

	csv_columns = ['estacion','fecha',
		'SO2-valor', 'SO2-estado',
		'NO-valor', 'NO-estado',
		'NO2-valor', 'NO2-estado',
		'NOX-valor', 'NOX-estado',
		'CO-valor', 'CO-estado',
		'O3-valor', 'O3-estado',
		'PM10-valor', 'PM10-estado',
		'PM25-valor', 'PM25-estado',]

	try:
	    with open(csv_file, 'w') as csvfile:
	        
	        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
	        writer.writeheader()

	        for dict_data in list_data:
	        	writer.writerow(dict_data)

	except IOError:
	    print("I/O error")


# ##########################################################
# PARAMETROS 
# ##########################################################

base_url = 'https://www.meteogalicia.gal/Caire/datos.action?request_locale=gl'

estacion = '' 

periodo = 'Horarios' # Diarios | Horarios

fecha_desde = ''

fecha_hasta = ''

csv_file = 'Galician_Quality_Air_Data.csv'

# ##########################################################
# PARAMETROS 
# ##########################################################

page_soup = getPageSoup(base_url, estacion, periodo, fecha_desde, fecha_hasta)

list_data = get_content_values(page_soup)

to_csv(csv_file, list_data)

