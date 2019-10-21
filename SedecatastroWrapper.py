import requests
from lxml import html

def _find_location_in_html(text):
    doc = html.fromstring(text)
    section_title_elements = doc.cssselect("#ctl00_Contenido_tblFinca > div > span")
    location = None
    for section_title_element in section_title_elements:
        if section_title_element.text == "Localización":
            enclosing_element = section_title_element.getnext().find(".//label")
            street = enclosing_element.text
            br_element = enclosing_element.find("br")
            city = br_element.tail
            # address = section_title_element.getnext().text_content()
            location = street + ", " + city
            location = location.replace("(", ",")
            location = location.replace(")", "")
            location = location.strip()
            break
    return location

def _find_construction_year_in_html(text):
    return ""

def update_property_from_catastro(catastro, property):
    try:
        url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCBusqueda.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
        }
        session = requests.Session()
        session.headers = headers
        response = session.get(url)
        doc = html.fromstring(response.text)
        form = doc.forms[0]

        payload = {
            "__VIEWSTATE" : form.inputs["__VIEWSTATE"].value,
            "__VIEWSTATEGENERATOR" : form.inputs["__VIEWSTATEGENERATOR"].value,
            "__EVENTVALIDATION" : form.inputs["__EVENTVALIDATION"].value,
            "ctl00$Contenido$pestañaActual" : "rc",
            "ctl00$Contenido$txtRC2" : catastro,
            "ctl00$Contenido$btnDatos" : "DATOS",
        }

        response = session.post(url, headers=headers, data=payload)

        if response.status_code != 200:
            print(f"Failed to update property from sedecatastro. Url: {response.request.url}")
            return False

        property.location = _find_location_in_html(response.text)
        property.construction_year = _find_construction_year_in_html(response.text)
      

    except Exception as e:
        print(f"Failed to update property from sedecatastro")
        print("Error message: ", e)
        return False

    return True


def _find_a_catastral_reference_in_html(text):
    doc = html.fromstring(text)
    first_catastral_reference_anchor_element = doc.cssselect("#heading0 > b > a")
    catastral_reference = None

    if first_catastral_reference_anchor_element != None and len(first_catastral_reference_anchor_element) > 0:
        catastral_reference = first_catastral_reference_anchor_element[0].text_content().strip()

    if catastral_reference == None or len(catastral_reference) < 20:
        #find plot's catastral reference
        main_heading_element = doc.cssselect("#ctl00_Contenido_HtmlTodos > div > div.panel-heading.amarillo")
        if main_heading_element != None and len(main_heading_element) > 0:
            catastral_reference = main_heading_element[0].text_content()
            catastral_reference = catastral_reference.replace("PARCELA CATASTRAL", "")
            catastral_reference = catastral_reference.strip()
        else:
            yet_another_case_element = doc.cssselect("#ctl00_Contenido_tblInmueble > div:nth-child(1) > div > span > label")
            if yet_another_case_element != None and len(yet_another_case_element) > 0:
                catastral_reference = yet_another_case_element[0].text_content().strip()
            

    return catastral_reference


def get_catastral_reference(lat, lng):
    try:
        url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        parameters = {
            "latitud": lat,
            "longitud": lng,
            "pest": "coordenadas",
            "huso": "0",
            "tipoCoordenadas": "2",
            "TipUR": "Coor",
        }

        session = requests.Session()
        response = session.get(url, params=parameters, headers=headers)

        if response.status_code != 200:
            print(f"Failed to get catasral reference number from {response.request.url}")
            return None

        catastral_reference = _find_a_catastral_reference_in_html(response.text)

    except Exception as e:
        print("Failed to get catasral reference number")
        print("Error message: ", e)
        catastral_reference = None

    return catastral_reference


def test_get_address():
    catastral_reference = "8931108DF2883B0001SO"
    expected = "AV DIAGONAL 572, BARCELONA ,BARCELONA"
    actual = get_address(catastral_reference)
    print(f"test get_address for catastro {catastral_reference}")
    print(f'address should be\n\t"{expected}"\nrecieved\n\t"{actual}"')
    print(f"addresses { 'match' if expected == actual else 'do not match'}")

    catastral_reference = "1819806DF3811H0001QD"
    expected = "AV MARQUES DE L'ARGENTERA 5, BARCELONA ,BARCELONA"
    actual = get_address(catastral_reference)
    print(f"test get_address for catastro {catastral_reference}")
    print(f'address should be\n\t"{expected}"\nrecieved\n\t"{actual}"')
    print(f"addresses { 'match' if expected == actual else 'do not match'}")

    catastral_reference = "9722108YJ2792D0002SA"
    expected = "CL JOSE BENLLIURE 119, VALENCIA ,VALENCIA"
    actual = get_address(catastral_reference)
    print(f"test get_address for catastro {catastral_reference}")
    print(f'address should be\n\t"{expected}"\nrecieved\n\t"{actual}"')
    print(f"addresses { 'match' if expected == actual else 'do not match'}")


def test_single_get_catastral_reference(lat, lng, expected):
    catastral_reference = get_catastral_reference(lat, lng)
    if catastral_reference == expected:
        print(f"catastral reference which was retrieved for {(lat, lng)} matched the expected {expected}")
    else:    
        print(f"catastral reference which was retrieved for {(lat, lng)} does NOT match the expected. Should be {expected}, recieved {catastral_reference}")

def test_get_catastral_reference():
    test_single_get_catastral_reference(41.39409684378864, 2.1487222098593293, "8931108DF2883B0001SO")
    test_single_get_catastral_reference(41.394096, 2.148722, "8931108DF2883B0001SO")
    test_single_get_catastral_reference(41.445460, 2.172483, "1087308DF3818G0001XI")
    test_single_get_catastral_reference(41.383864, 2.183984, "1819806DF3811H0001QD")
    test_single_get_catastral_reference(39.46744030137543, -0.3307932139520062, "9722108YJ2792D0002SA")
 
if __name__ == "__main__":
    test_get_address()
    test_get_catastral_reference()

