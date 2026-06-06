from quinielas.models import Seleccion

PAISES = {
    "México": "mx",
    "Canadá": "ca",
    "Estados Unidos": "us",
    "España": "es",
    "Argentina": "ar",
    "Francia": "fr",
    "Inglaterra": "gb",
    "Brasil": "br",
    "Portugal": "pt",
    "Países Bajos": "nl",
    "Bélgica": "be",
    "Alemania": "de",
    "Croacia": "hr",
    "Marruecos": "ma",
    "Colombia": "co",
    "Uruguay": "uy",
    "Suiza": "ch",
    "Japón": "jp",
    "Senegal": "sn",
    "Irán": "ir",
    "Corea del Sur": "kr",
    "Ecuador": "ec",
    "Austria": "at",
    "Australia": "au",
    "Noruega": "no",
    "Panamá": "pa",
    "Egipto": "eg",
    "Argelia": "dz",
    "Escocia": "gb",
    "Paraguay": "py",
    "Túnez": "tn",
    "Costa de Marfil": "ci",
    "Uzbekistán": "uz",
    "Catar": "qa",
    "Arabia Saudita": "sa",
    "Sudáfrica": "za",
    "Jordania": "jo",
    "Cabo Verde": "cv",
    "Ghana": "gh",
    "Curazao": "cw",
    "Haití": "ht",
    "Nueva Zelanda": "nz",
    "Bosnia y Herzegovina": "ba",
    "Suecia": "se",
    "Turquía": "tr",
    "República Checa": "cz",
    "R.D del Congo": "cd",
    "Irak": "iq",
}


def run():
    for nombre, code in PAISES.items():
        sel, _ = Seleccion.objects.get_or_create(nombre=nombre)
        sel.code = code
        sel.save()
    print(f"Se actualizaron {Seleccion.objects.count()} selecciones.")