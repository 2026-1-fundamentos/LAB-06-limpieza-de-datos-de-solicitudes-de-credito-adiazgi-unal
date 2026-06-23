"""
Escriba el codigo que ejecute la accion solicitada en la pregunta.
"""


"""
   
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv"

    """
"""Escriba el codigo que ejecute la accion solicitada en la pregunta."""

"""Escriba el codigo que ejecute la accion solicitada en la pregunta."""

import os
import re

import pandas as pd  # type: ignore


def _fingerprint(valor):
    """
    Genera la "huella" (fingerprint) de una cadena de texto:
    - convierte a minusculas y quita espacios sobrantes
    - elimina puntuacion (puntos, guiones, guiones bajos, etc.)
    - separa en palabras, elimina duplicadas y las ordena alfabeticamente
    - las vuelve a unir con un solo espacio

    Esto permite agrupar variantes de la misma categoria que solo
    difieren en mayusculas/minusculas, puntuacion u orden de palabras.
    Por ejemplo "EMPRESARIAL_ED._", "empresarial-ed.-" y "empresarial ed."
    terminan teniendo el mismo fingerprint.
    """
    if pd.isna(valor):
        return valor
    texto = str(valor).lower().strip()
    texto = re.sub(r"[^a-z0-9 ]", " ", texto)
    tokens = sorted(set(texto.split()))
    return " ".join(tokens)


def _limpiar_monto(valor):
    """
    Normaliza la columna monto_del_credito a un entero.

    El archivo original mezcla formatos como:
        "5000000"
        "$ 2,000,000.00"
        "14"
        "$ 14.00"

    Reglas aplicadas:
    - se elimina el simbolo "$" y los espacios
    - si hay coma Y punto, la coma es separador de miles y el punto
      antecede a los decimales (se descartan los decimales)
    - si solo hay coma o solo hay punto, se revisa cuantos digitos
      quedan despues del separador: si son 2, es un decimal (se
      descarta); si no, es separador de miles (se elimina el separador)
    """
    if pd.isna(valor):
        return valor

    texto = str(valor).replace("$", "").strip().replace(" ", "")

    if "," in texto and "." in texto:
        texto = texto.replace(",", "")
        texto = texto.split(".")[0]
    elif "," in texto:
        partes = texto.split(",")
        if len(partes[-1]) == 2:
            texto = "".join(partes[:-1])
        else:
            texto = texto.replace(",", "")
    elif "." in texto:
        partes = texto.split(".")
        if len(partes[-1]) == 2:
            texto = "".join(partes[:-1])
        else:
            texto = texto.replace(".", "")

    return int(texto)


def _limpiar_fecha(valor):
    """
    Normaliza la columna fecha_de_beneficio al formato "yyyy-mm-dd".

    El archivo original mezcla dos formatos:
        "13/07/2018"   ->  dd/mm/yyyy
        "2017/05/31"   ->  yyyy/mm/dd
    """
    if pd.isna(valor):
        return valor

    texto = str(valor).strip()
    if "/" in texto:
        partes = texto.split("/")
        if len(partes[0]) == 4:
            anio, mes, dia = partes
        else:
            dia, mes, anio = partes
        return f"{int(anio):04d}-{int(mes):02d}-{int(dia):02d}"
    return texto


def pregunta_01():
    """
    Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".
    El archivo tiene problemas como registros duplicados y datos faltantes.
    Tenga en cuenta todas las verificaciones discutidas en clase para
    realizar la limpieza de los datos.

    El archivo limpio debe escribirse en
    "files/output/solicitudes_de_credito.csv"
    """
    df = pd.read_csv(
        "files/input/solicitudes_de_credito.csv",
        sep=";",
        index_col=0,
    )

    # 1. Normalizacion de columnas categoricas de texto mediante fingerprint
    columnas_texto = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        "línea_credito",
    ]
    for columna in columnas_texto:
        df[columna] = df[columna].apply(_fingerprint)

    # 2. Normalizacion de columnas numericas / de fecha con formatos mixtos
    df["monto_del_credito"] = df["monto_del_credito"].apply(_limpiar_monto)
    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].apply(_limpiar_fecha)

    # 3. Eliminacion de registros duplicados (ya con los datos normalizados,
    #    de forma que duplicados "escondidos" por formato tambien se detecten)
    df = df.drop_duplicates()

    # 4. Eliminacion de registros con datos faltantes
    df = df.dropna()

    # 5. Escritura del archivo limpio
    os.makedirs("files/output", exist_ok=True)
    df.to_csv(
        "files/output/solicitudes_de_credito.csv",
        sep=";",
        index=True,
    )