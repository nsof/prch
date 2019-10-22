import requests
from lxml import html

def _find_location_in_html(doc):
    section_title_elements = doc.cssselect("#ctl00_Contenido_tblFinca > div > span")
    location = None
    for section_title_element in section_title_elements:
        if section_title_element.text == "Localización":
            enclosing_element = section_title_element.getnext().find(".//label")
            street = enclosing_element.text
            br_element = enclosing_element.find("br")
            city = br_element.tail
            # location = section_title_element.getnext().text_content()
            location = street + ", " + city
            location = location.replace(" (", ", ")
            location = location.replace(")", "")
            location = location.strip()
            break
    return location

def get_property_from_catastro(catastral_reference):
    from Property import Property
    property = Property(None, catastral_reference)
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
            "ctl00$Contenido$txtRC2" : catastral_reference,
            "ctl00$Contenido$btnDatos" : "DATOS",
        }

        response = session.post(url, headers=headers, data=payload)

        if response.status_code != 200:
            print(f"Failed to update property from sedecatastro. Url: {response.request.url}")
            return None

        doc = html.fromstring(response.text)

        property.location = _find_location_in_html(doc)

        matched_elements = doc.cssselect("#ctl00_Contenido_tblInmueble > div:nth-child(6) > div > span > label")
        if matched_elements:
            property.construction_year = matched_elements[0].text.strip() if matched_elements[0].text else ""

        matched_elements = doc.cssselect("#ctl00_Contenido_tblLocales > tr:nth-child(2) > td:nth-child(2) > span")
        if matched_elements:
            property.stairs = matched_elements[0].text.strip() if matched_elements[0].text else ""

        matched_elements = doc.cssselect("#ctl00_Contenido_tblLocales > tr:nth-child(2) > td:nth-child(3) > span")
        if matched_elements:
            property.floor = matched_elements[0].text.strip() if matched_elements[0].text else ""

        matched_elements = doc.cssselect("#ctl00_Contenido_tblLocales > tr:nth-child(2) > td:nth-child(4) > span")
        if matched_elements:
            property.door = matched_elements[0].text.strip() if matched_elements[0].text else ""

        matched_elements = doc.cssselect("#ctl00_Contenido_tblLocales > tr:nth-child(2) > td:nth-child(5) > span")
        if matched_elements:
            property.private_area = matched_elements[0].text.strip() if matched_elements[0].text else ""

        matched_elements = doc.cssselect("#ctl00_Contenido_tblLocales > tr:nth-child(3) > td:nth-child(5) > span")
        if matched_elements:
            property.common_area = matched_elements[0].text.strip() if matched_elements[0].text else ""

    except Exception as e:
        print("Error while updating property from sedecatastro. Error message: ", e)

    return property


def _find_a_catastral_reference_in_html(text):
    doc = html.fromstring(text)
    first_catastral_reference_anchor_element = doc.cssselect("#heading0 > b > a")
    catastral_reference = None

    if first_catastral_reference_anchor_element != None and len(first_catastral_reference_anchor_element) > 0:
        catastral_reference = first_catastral_reference_anchor_element[0].text.strip()

    if catastral_reference == None or len(catastral_reference) < 20:
        #find plot's catastral reference
        main_heading_element = doc.cssselect("#ctl00_Contenido_HtmlTodos > div > div.panel-heading.amarillo")
        if main_heading_element != None and len(main_heading_element) > 0:
            catastral_reference = main_heading_element[0].text
            catastral_reference = catastral_reference.replace("PARCELA CATASTRAL", "")
            catastral_reference = catastral_reference.strip()
        else:
            yet_another_case_element = doc.cssselect("#ctl00_Contenido_tblInmueble > div:nth-child(1) > div > span > label")
            if yet_another_case_element != None and len(yet_another_case_element) > 0:
                catastral_reference = yet_another_case_element[0].text.strip()
            

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


def test_get_property_from_catastro():
    catastral_reference = "8931108DF2883B0001SO"
    print(f"test get property data for catastro {catastral_reference}")
    property = get_property_from_catastro(catastral_reference)
    if (property != None and property.location == "AV DIAGONAL 572, BARCELONA, BARCELONA" and
        property.construction_year == "1930" and
        property.stairs == "" and
        property.floor == "0" and
        property.door == "01" and
        property.private_area == "52" and
        property.common_area == "5"):
        print(f"passed")
    else:
        print(f"failed")

    catastral_reference = "0603803DF3900D0012SG"
    print(f"test get property data for catastro {catastral_reference}")
    property = get_property_from_catastro(catastral_reference)
    if (property != None and property.location == "AV RASOS DE PEGUERA 153, BARCELONA, BARCELONA" and
        property.construction_year == "1968" and
        property.stairs == "" and
        property.floor == "05" and
        property.door == "01" and
        property.private_area == "60" and
        property.common_area == "5"):
        print(f"passed")
    else:
        print(f"failed")

    catastral_reference = "0875106DF3807F0024YK"
    print(f"test get property data for catastro {catastral_reference}")
    property = get_property_from_catastro(catastral_reference)
    if (property != None and property.location == "PS URRUTIA 102, BARCELONA, BARCELONA" and
        property.construction_year == "1965" and
        property.stairs == "" and
        property.floor == "04" and
        property.door == "04" and
        property.private_area == "75" and
        property.common_area == "9"):
        print(f"passed")
    else:
        print(f"failed")

def test_single_get_catastral_reference(lat, lng, expected):
    print(f"testing get catastral reference for {(lat, lng)}")
    catastral_reference = get_catastral_reference(lat, lng)
    if catastral_reference == expected:
        print(f"passed")
    else:    
        print(f"failed. Should be {expected}, recieved {catastral_reference}")

def test_get_catastral_reference():
    test_single_get_catastral_reference(41.39409684378864, 2.1487222098593293, "8931108DF2883B0001SO")
    test_single_get_catastral_reference(41.394096, 2.148722, "8931108DF2883B0001SO")
    test_single_get_catastral_reference(41.445460, 2.172483, "1087308DF3818G0001XI")
    test_single_get_catastral_reference(41.383864, 2.183984, "1819806DF3811H0001QD")
    test_single_get_catastral_reference(39.46744030137543, -0.3307932139520062, "9722108YJ2792D0002SA")
 
if __name__ == "__main__":
    # test_get_property_from_catastro()
    test_get_catastral_reference()

