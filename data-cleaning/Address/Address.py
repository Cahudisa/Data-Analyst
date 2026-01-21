import pandas as pd
import re

def cargar_diccionario(archivo):
    diccionario = {}
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            for linea in f:
                partes = linea.strip().split(":")
                if len(partes) == 2:
                    variantes = partes[0].split(",")
                    for variante in variantes:
                        diccionario[rf"\b{variante}\b"] = partes[1].upper()
    except FileNotFoundError:
        print(f" Archivo '{archivo}' no encontrado. Se usará un diccionario vacío.")
    return diccionario

abreviaturas = cargar_diccionario("abreviaturas.txt")

normalizar_orientacion = {
    "NORTE": "NORTE", "SUR": "SUR",
    "ESTE": "ESTE", "OESTE": "OESTE"
}

def limpiar_vias_duplicadas(direccion):
    direccion = direccion.upper().strip()
    # Expresión regular para detectar los tipos de vía en la dirección
    vias = re.findall(r"\b(CL|CLL|KR|KRA|DG|TV|AC|CARRERA|CALLE|DIAGONAL|TRANSVERSAL|AV|AVENIDA)\b", direccion)
    if len(vias) > 1:
        primera_via = vias[0]  # La primera vía es la que conservamos
        # Eliminamos todas las demás vías después de la primera
        direccion = re.sub(rf"\b({'|'.join(vias[1:])})\b", "", direccion).strip()
        direccion = re.sub(r"\s+", " ", direccion)  # Eliminar espacios dobles
    return direccion

def normalizar_direccion(direccion, abreviaturas):
    if pd.isna(direccion):
        return "NULL"

    direccion = direccion.upper().strip()
    
    # **Reemplazar LC seguido de números por LOCAL**
    direccion = re.sub(r"\bLC(\d+)\b", r"LOCAL \1", direccion)

    # Si la dirección empieza con "LOCAL", "LC" o "LCL", solo aplicar reemplazo de abreviaturas
    if re.match(r"^(LOCAL|LC|LCL)\b", direccion):
        for abreviatura, reemplazo in abreviaturas.items():
            direccion = re.sub(abreviatura, reemplazo, direccion)
        return direccion  # Devolver sin más cambios

    # **Reemplazar CR seguido de números por CARRERA**
    direccion = re.sub(r"\bCR(\d+)\b", r"CARRERA \1", direccion)

    # **Eliminar caracteres especiales o palabras no deseadas al inicio**
    direccion = re.sub(r"^[-\s]*(DIR\s+)?", "", direccion)

    # **Si la dirección comienza con un número, marcar como NULL**
    if re.match(r"^\d", direccion):
        return "NULL"

    # **Eliminar caracteres especiales dentro de la dirección**
    direccion = re.sub(r"\bRTE\b", "", direccion)  # Eliminar la palabra "RTE"
    direccion = re.sub(r"[^a-zA-Z0-9\s#]", " ", direccion)
    direccion = re.sub(r"[^\w\s#]", " ", direccion)
    direccion = re.sub(r"\s+", " ", direccion).strip()

    # Si la dirección solo tiene un tipo de vía y un número, devolver NULL
    if re.fullmatch(r"\b(CL|KR|KRA|DG|TV|AC|CARRERA|CALLE|DIAGONAL|TRANSVERSAL|AV|AVENIDA)\s+\d+\b", direccion):
        return "NULL"

    # **Eliminar vía secundaria si hay dos**
    direccion = limpiar_vias_duplicadas(direccion)

    # **Reemplazar abreviaturas en la dirección**
    for abreviatura, reemplazo in abreviaturas.items():
        direccion = re.sub(abreviatura, reemplazo, direccion)

    # **Identificar si contiene ESQ o ESQUINA**
    tiene_esquina = bool(re.search(r"\bESQ\b|\bESQUINA\b", direccion))
    
    # **Expresión regular para segmentar la dirección correctamente**
    patron = re.compile(
        r"(?P<tipo_via>\w+)\s*"                      # Tipo de vía (Calle, Carrera, etc.)
        r"(?P<num1>\d+)\s*"                          # Primer número
        r"(?P<letra1>BIS|[A-F]?)\s*"                 # Letra opcional o "BIS" después del primer número
        r"(?P<orient1>NORTE|SUR|ESTE|OESTE)?\s*"     # Orientación opcional
        r"(N|NO|N.|#|no)?\s*"                        # Símbolo "#" opcional
        r"(?P<num2>\d+)\s*"                          # Segundo número
        r"(?P<letra2>BIS|[A-F]?)\s*"                 # Letra opcional o "BIS" después del segundo número
        r"(?P<orient2>NORTE|SUR|ESTE|OESTE|N|NO|no)?\s*"  # Otra orientación opcional
        r"-?\s*(?P<num3>\d+)?\s*"                    # Tercer número 
        r"(?!\S*-?\d+)(?P<complemento>.*)"           # Complemento 
    )

    match = patron.match(direccion)

    if not match:
        return direccion

    tipo_via = match.group("tipo_via") or ""
    num1 = match.group("num1") or ""
    letra1 = match.group("letra1") or ""
    orient1 = match.group("orient1") or ""
    num2 = match.group("num2") or ""
    letra2 = match.group("letra2") or ""
    orient2 = match.group("orient2") or ""
    num3 = match.group("num3") or ""
    complemento = match.group("complemento").strip()

    # Si "N", "No" o "no" están después de num2, lo tratamos como "NORTE"
    if orient2 in ["N", "NO", "no"]:
        orient2 = "NORTE"

    # Si "N", "No" o "no" aparecen antes de num2 y NO hay un `#` explícito, se considera como `#`
    elif orient1 in ["N", "NO", "no","N.", "NO.", "no."]:
        orient1 = "#"

    orient1 = normalizar_orientacion.get(orient1.upper(), orient1) if orient1 else orient1
    orient2 = normalizar_orientacion.get(orient2.upper(), orient2) if orient2 else orient2

    partes = [tipo_via, num1, letra1, orient1, "#", num2, letra2, orient2]

    if num3:
        partes.extend(["-", num3])

    direccion_normalizada = " ".join(filter(None, partes)).strip()

    if tiene_esquina and not num3:
        direccion_normalizada += " ESQUINA"
    elif complemento:
        direccion_normalizada += f" {complemento}"

    return direccion_normalizada

# Leer archivo Excel con direcciones
df = pd.read_excel("direcciones.xlsx")

df["Direccion Normalizada"] = df["DIRECCION"].apply(lambda x: normalizar_direccion(x, abreviaturas))

df.to_excel("direcciones_normalizadas.xlsx", index=False)

print(" Direcciones normalizadas y guardadas en 'direcciones_normalizadas.xlsx'")
