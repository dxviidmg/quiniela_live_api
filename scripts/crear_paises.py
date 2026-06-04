from quinielas.models import Bombo, Seleccion

BOMBOS = {
    1: [
        "México", "Canadá", "Estados Unidos", "España", "Argentina",
        "Francia", "Inglaterra", "Brasil", "Portugal", "Países Bajos",
        "Bélgica", "Alemania",
    ],
    2: [
        "Croacia", "Marruecos", "Colombia", "Uruguay", "Suiza",
        "Japón", "Senegal", "Irán", "Corea del Sur", "Ecuador",
        "Austria", "Australia",
    ],
    3: [
        "Noruega", "Panamá", "Egipto", "Argelia", "Escocia",
        "Paraguay", "Túnez", "Costa de Marfil", "Uzbekistán", "Catar",
        "Arabia Saudita", "Sudáfrica",
    ],
    4: [
        "Jordania", "Cabo Verde", "Ghana", "Curazao", "Haití",
        "Nueva Zelanda", "Bosnia y Herzegovina", "Suecia", "Turquía",
        "República Checa", "R.D del Congo", "Irak",
    ],
}


def run():
    for numero, paises in BOMBOS.items():
        bombo, _ = Bombo.objects.get_or_create(numero=numero)
        for pais in paises:
            Seleccion.objects.get_or_create(nombre=pais, defaults={"bombo": bombo})
    print(f"Se cargaron {Seleccion.objects.count()} selecciones en {Bombo.objects.count()} bombos.")
