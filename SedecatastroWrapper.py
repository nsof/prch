import requests

def _find_plot_cadastral_reference_in_text(text):
   text_anchor = "PARCELA CATASTRAL"
   start = text.find(text_anchor)
   if start == -1:
      return None

   start = start + len(text_anchor)
   end = text.find('<', start)

   cadastral_reference = text[start:end]
   cadastral_reference = cadastral_reference.strip()
   return cadastral_reference


def _find_a_single_cadastral_reference_in_text(text):
   text_anchor = 'target="_top" >'
   start = text.find(text_anchor)
   if start == -1:
      return None

   start = start + len(text_anchor)
   end = text.find('<', start)

   cadastral_reference = text[start:end]
   cadastral_reference = cadastral_reference.strip()
   return cadastral_reference


def _find_cadastral_reference_in_redirected_url(text):
   start = text.find("RefC=")
   if start == -1:
      return None

   start = start + len("RefC=")
   end = text.find('&', start)

   cadastral_reference = text[start:end]
   cadastral_reference = cadastral_reference.strip()
   return cadastral_reference


def get_cadastral_reference(lat, lng):
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
         "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
      }
      parameters = { 
            "latitud" : lat, "longitud" : lng, 
            "pest" : "coordenadas", "huso" : "0", "tipoCoordenadas" : "2", "TipUR" : "Coor",
      }

      session = requests.Session()
      response = session.get(url, params = parameters, headers=headers)
      

      if response.status_code != 200:
         print (f"Failed to get catasral reference number from {response.request.url}")
         return None

      if len(response.history) > 0:
         cadastral_reference = _find_cadastral_reference_in_redirected_url(response.url)
      else:
         cadastral_reference = _find_a_single_cadastral_reference_in_text(response.text)
         if cadastral_reference == None:
            cadastral_reference = _find_plot_cadastral_reference_in_text(response.text)

   except Exception as e:
      print ("Failed to get catasral reference number")
      print ("Error message: ", e)
      cadastral_reference = None

   return cadastral_reference


def Sedecatastro_test():
   lat, lng = 41.39409684378864, 2.1487222098593293
   expected = "8931108DF2883B0001SO"
   cadastral_reference = get_cadastral_reference(lat, lng)
   print (f"cadastral reference for {(lat, lng)} should be {expected}, recieved {cadastral_reference}")

   lat, lng = 41.394096, 2.148722
   expected = "8931108DF2883B0001SO"
   cadastral_reference = get_cadastral_reference(lat, lng)
   print (f"cadastral reference for {(lat, lng)} should be {expected}, recieved {cadastral_reference}")

   lat, lng = 41.445460, 2.172483
   expected = "1087308DF3818G0001XI"
   cadastral_reference = get_cadastral_reference(lat, lng)
   print (f"cadastral reference for {(lat, lng)} should be {expected}, recieved {cadastral_reference}")

   lat, lng = 39.46744030137543, -0.3307932139520062
   expected = "9722108YJ2792D0002SA"
   cadastral_reference = get_cadastral_reference(lat, lng)
   print (f"cadastral reference for {(lat, lng)} should be {expected}, recieved {cadastral_reference}")

   lat, lng = 41.383864, 2.183984
   expected = "1819806DF3811H0001QD"
   cadastral_reference = get_cadastral_reference(lat, lng)
   print (f"cadastral reference for {(lat, lng)} should be {expected}, recieved {cadastral_reference}")
