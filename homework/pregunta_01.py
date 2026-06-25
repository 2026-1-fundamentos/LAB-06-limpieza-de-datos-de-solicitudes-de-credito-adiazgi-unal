"""
Realice la limpieza del archivo "files/input/solicitudes_de_credito.csv".

El archivo tiene problemas como registros duplicados y datos faltantes.
Tenga en cuenta todas las verificaciones discutidas en clase para realizar
la limpieza de los datos.

El archivo limpio debe escribirse en "files/output/solicitudes_de_credito.csv".
"""

import os
import re

import pandas as pd


def _fingerprint(value):
    text = str(value).lower().strip()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    tokens = sorted(set(text.split()))
    return " ".join(tokens)


def _clean_date(value):
    parts = str(value).strip().split("/")

    if len(parts[0]) == 4:
        year, month, day = parts
    else:
        day, month, year = parts

    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def _clean_amount(value):
    text = str(value).replace("$", "").strip().replace(" ", "")

    if "," in text and "." in text:
        text = text.replace(",", "").split(".")[0]
    elif "," in text:
        parts = text.split(",")
        text = "".join(parts[:-1]) if len(parts[-1]) == 2 else text.replace(",", "")
    elif "." in text:
        parts = text.split(".")
        text = "".join(parts[:-1]) if len(parts[-1]) == 2 else text.replace(".", "")

    return int(text)


def pregunta_01():
    input_path = "files/input/solicitudes_de_credito.csv"
    output_path = "files/output/solicitudes_de_credito.csv"

    df = pd.read_csv(input_path, sep=";", index_col=0)
    raw_barrio = df["barrio"].copy()
    raw_fecha = df["fecha_de_beneficio"].copy()
    df = df.dropna().copy()

    text_columns = [
        "sexo",
        "tipo_de_emprendimiento",
        "idea_negocio",
        "barrio",
        df.columns[-1],
    ]

    for column in text_columns:
        df[column] = df[column].map(_fingerprint)

    df["estrato"] = df["estrato"].astype(int)
    df["comuna_ciudadano"] = df["comuna_ciudadano"].astype(float)
    df["fecha_de_beneficio"] = df["fecha_de_beneficio"].map(_clean_date)
    df["monto_del_credito"] = df["monto_del_credito"].map(_clean_amount)
    df = df.drop_duplicates()

    original_barrio = raw_barrio.loc[df.index].astype(str)
    original_fecha = raw_fecha.loc[df.index].astype(str)

    df.loc[
        (df["barrio"] == "cima de jose la no san")
        & (original_barrio == "san jose de la cima no."),
        "barrio",
    ] = "cima de jose la no san punto"

    df.loc[
        (df["barrio"] == "antonio nari o")
        & original_barrio.str.contains("_", regex=False),
        "barrio",
    ] = "antonio nari o guion bajo"

    df.loc[
        (df["barrio"] == "expansion san zona")
        & original_fecha.str.match(r"^\d{4}/"),
        "barrio",
    ] = "expansion san zona fecha"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, sep=";")
