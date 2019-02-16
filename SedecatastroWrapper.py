import requests


def _find_address_in_text(text):
    text_anchor = "Localización"
    start = text.find(text_anchor, text.find(text_anchor) + len(text_anchor))
    if start == -1:
        return None
    start += len(text_anchor)
    text_anchor = "<label"
    start = text.find(text_anchor, start)
    if start == -1:
        return None
    start += len(text_anchor)
    text_anchor = ">"
    start = text.find(text_anchor, start)
    if start == -1:
        return None
    start += 1
    end = text.find("</l", start)
    if end == -1:
        return None

    address = text[start:end]
    address = address.replace("<br>", " ")
    address = address.replace("(", ",")
    address = address.replace(")", "")
    address = address.strip()
    return address


def _find_plot_catastral_reference_in_text(text):
    text_anchor = "PARCELA CATASTRAL"
    start = text.find(text_anchor)
    if start == -1:
        return None

    start = start + len(text_anchor)
    end = text.find("<", start)

    catastral_reference = text[start:end]
    catastral_reference = catastral_reference.strip()
    return catastral_reference


def _find_a_single_catastral_reference_in_text(text):
    text_anchor = 'target="_top" >'
    start = text.find(text_anchor)
    if start == -1:
        return None

    start = start + len(text_anchor)
    end = text.find("<", start)

    catastral_reference = text[start:end]
    catastral_reference = catastral_reference.strip()
    return catastral_reference


def _find_catastral_reference_in_redirected_url(text):
    start = text.find("RefC=")
    if start == -1:
        return None

    start = start + len("RefC=")
    end = text.find("&", start)

    catastral_reference = text[start:end]
    catastral_reference = catastral_reference.strip()
    return catastral_reference


def get_address(catastral_reference):
    try:
        url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCBusqueda.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
        }
        parameters = {
            "fromVolver": "ListaBienes", 
            "pest" : "rc",
            "RCCompleta": catastral_reference,
            "tipoVia" : "",
            "via" : "",
            "num" : "",
            "blq" : "",
            "esc" : "",
            "plt" : "",
            "pta" : "",
            "descProv" : "",
            "prov" : "",
            "mun" : "",
            "descMuni" : "",
            "TipUR" : "",
            "codVia" : "",
            "comVia" : "",
            "final" : "",
            "pol" : "",
            "par" : "",
            "Idufir" : "",
            "latitud" : "",
            "longitud" : "",
            "gradoslat" : "",
            "minlat" : "",
            "seglat" : "",
            "gradoslon" : "",
            "minlon" : "",
            "seglon" : "",
            "x" : "",
            "y" : "",
            "huso" : "",
            "tipoCoordenadas" : ""
        }

        session = requests.Session()
        response = session.post(url, params=parameters, headers=headers)

        if response.status_code != 200:
            print(f"Failed to get address from {response.request.url}")
            return None

        address = _find_address_in_text(response.text)

    except Exception as e:
        print("Failed to get address from catasral reference")
        print("Error message: ", e)
        address = None

    return address


def get_catastral_reference(lat, lng):
    try:
        url = "https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx"
        headers = {
            # "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # "Accept-Encoding" : "gzip, deflate, br"
            # Accept-Language: en-GB,en;q=0.9,en-US;q=0.8,he;q=0.7
            # Connection: keep-alive
            # Cookie: ASP.NET_SessionId=kirnbuffprhok1yfobovdpk5; Lenguaje=es
            # Host: www1.sedecatastro.gob.es
            # Upgrade-Insecure-Requests: 1
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

        if len(response.history) > 0:
            catastral_reference = _find_catastral_reference_in_redirected_url(response.url)
        else:
            catastral_reference = _find_a_single_catastral_reference_in_text(response.text)
            if catastral_reference == None:
                catastral_reference = _find_plot_catastral_reference_in_text(response.text)

    except Exception as e:
        print("Failed to get catasral reference number")
        print("Error message: ", e)
        catastral_reference = None

    return catastral_reference


def test_find_address_in_text():
    text = (
        ' <DIV class="form-group"><span class="col-md-4 control-label ">Referencia catastral</span><DIV class="col-md-8 "><span class="control-label black"><label  class="control-label black text-left">1819806DF3811H0001QD&nbsp;<span data-toggle="tooltip" data-placement="bottom" title="Copiar referencia catastral al portapapeles"><a href="javascript:copiarPortapapeles("1819806DF3811H0001QD")" ><span class="fa fa-clipboard"></span></a></span>&nbsp;&nbsp;&nbsp;<span data-toggle="tooltip" data-placement="bottom" title="Obtener etiqueta"> <a href="javascript:abreVentanaCodBar()"  ><span class="glyphicon glyphicon-barcode" ></span></a></span></label></span></DIV></DIV><DIV class="form-group"><span class="col-md-4 control-label ">Localización</span><DIV class="col-md-8 "><span class="control-label black"><label  class="control-label black text-left">AV MARQUES DE L'
        'ARGENTERA 5<br>08003 BARCELONA (BARCELONA)</label></span></DIV></DIV><DIV class="form-group"><span class="col-md-4 control-label ">Clase</span><DIV class="col-md-8 "><span class="control-label black"><label  class="control-label black text-left">Urbano</label></span></DIV></DIV><DIV class="form-group"><span class="col-md-4 control-label ">Uso principal</span><DIV class="col-md-8 "><span class="control-label black"><label  class="control-label black text-left">Residencial</label></span></DIV></DIV><DIV class="form-group"><span class="col-md-4 control-label ">Superficie construida <a href="" data-toggle="modal" data-target=".bs-example-modal-sm "><span class="glyphicon glyphicon-info-sign gray9"></span></a></span><DIV class="col-md-8 "><span class="control-label black"><label  class="control-label black text-left">1.740 m<sup>2</sup></label></span></DIV></DIV><DIV class="form-group"><span class="col-md-4 control-label ">Año construcción </span><DIV class="col-md-8 "><span class="control-label black"><label  class="control-label black text-left"> 2009</label></span></DIV></DIV></div> '
    )
    text += (
        ' <div id="ctl00_Contenido_tblFinca" class="col-md-10 form-horizontal">                        <DIV class="form-group"><DIV class="col-md-12"><span class="control-label black">Parcela construida sin división horizontal</span></DIV></DIV><DIV class="form-group"><span class="col-md-3 control-label ">Localización</span><DIV class="col-md-9 "><span class="control-label black"><label  class="control-label black text-left">AV MARQUES DE L'
        'ARGENTERA 5<br>BARCELONA (BARCELONA)</label></span></DIV></DIV><DIV class="form-group"><span class="col-md-3 control-label ">Superficie gráfica</span><DIV class="col-md-9 "><span class="control-label black"><label  class="control-label black text-left">367 m<sup>2</sup></label></span></DIV></DIV></div> </div> </div>    '
    )

    expected = "AV MARQUES DE L'ARGENTERA 5 BARCELONA ,BARCELONA"
    address = _find_address_in_text(text)
    print (f"addresses { 'match' if expected == address else 'do not match'}")
    print(f'address should be\n"{expected}", recieved\n"{address}"')


def test_get_address():
    catastral_reference = "1819806DF3811H0001QD"
    expected = "AV MARQUES DE L'ARGENTERA 5 BARCELONA ,BARCELONA"
    actual = get_address(catastral_reference)

    print(f'Address for {catastral_reference} should be {expected}, recieved {actual}')

    catastral_reference = "9722108YJ2792D0002SA"
    expected = "CL JOSE BENLLIURE 119 VALENCIA ,VALENCIA"
    actual = get_address(catastral_reference)
    print(f'Address for {catastral_reference} should be {expected}, recieved {actual}')


def test_get_catastral_reference():
    lat, lng = 41.394_096_843_788_64, 2.148_722_209_859_329_3
    expected = "8931108DF2883B0001SO"
    catastral_reference = get_catastral_reference(lat, lng)
    print(f"catastral reference for {(lat, lng)} should be {expected}, recieved {catastral_reference}")

    lat, lng = 41.394_096, 2.148_722
    expected = "8931108DF2883B0001SO"
    catastral_reference = get_catastral_reference(lat, lng)
    print(f"catastral reference for {(lat, lng)} should be {expected}, recieved {catastral_reference}")

    lat, lng = 41.445_460, 2.172_483
    expected = "1087308DF3818G0001XI"
    catastral_reference = get_catastral_reference(lat, lng)
    print(f"catastral reference for {(lat, lng)} should be {expected}, recieved {catastral_reference}")

    lat, lng = 39.467_440_301_375_43, -0.330_793_213_952_006_2
    expected = "9722108YJ2792D0002SA"
    catastral_reference = get_catastral_reference(lat, lng)
    print(f"catastral reference for {(lat, lng)} should be {expected}, recieved {catastral_reference}")

    lat, lng = 41.383_864, 2.183_984
    expected = "1819806DF3811H0001QD"
    catastral_reference = get_catastral_reference(lat, lng)
    print(f"catastral reference for {(lat, lng)} should be {expected}, recieved {catastral_reference}")

if __name__ == "__main__":
    # test_find_address_in_text()
    test_get_address()
    # test_get_catastral_reference()

