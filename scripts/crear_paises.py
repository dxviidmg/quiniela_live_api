from quinielas.models import Seleccion

PAISES = {
    "España": "es",
    "Argentina": "ar",
    "Francia": "fr",
    "Inglaterra": "gb",
    "Portugal": "pt",
    "Brasil": "br",
    "Países Bajos": "nl",
    "Marruecos": "ma",
    "Bélgica": "be",
    "Alemania": "de",
    "Croacia": "hr",
    "Colombia": "co",
    "Senegal": "sn",
    "México": "mx",
    "Estados Unidos": "us",
    "Uruguay": "uy",
    "Japón": "jp",
    "Suiza": "ch",
    "Irán": "ir",
    "Turquía": "tr",
    "Austria": "at",
    "Ecuador": "ec",
    "Corea del Sur": "kr",
    "Australia": "au",
    "Argelia": "dz",
    "Egipto": "eg",
    "Canadá": "ca",
    "Túnez": "tn",
    "Costa de Marfil": "ci",
    "Paraguay": "py",
    "Escocia": "gb",
    "Suecia": "se",
    "Arabia Saudita": "sa",
    "Sudáfrica": "za",
    "Ghana": "gh",
    "Panamá": "pa",
    "Noruega": "no",
    "Bosnia y Herzegovina": "ba",
    "República Checa": "cz",
    "Catar": "qa",
    "Uzbekistán": "uz",
    "Jordania": "jo",
    "R.D del Congo": "cd",
    "Cabo Verde": "cv",
    "Irak": "iq",
    "Haití": "ht",
    "Curazao": "cw",
    "Nueva Zelanda": "nz",
}


def run():
    for nombre, codigo in PAISES.items():
        sel, _ = Seleccion.objects.get_or_create(nombre=nombre)
        sel.codigo = codigo
        sel.save()
    print(f"Se actualizaron {Seleccion.objects.count()} selecciones.")