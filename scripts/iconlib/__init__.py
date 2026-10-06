"""Utilidades para generar librerías de iconos de Draw.io (mxlibrary).

Módulos:
    manifest       Lectura de libraries.json (qué carpeta genera qué librería).
    titles         Reglas para derivar el título visible de cada icono.
    mxlibrary      Empaquetado de una carpeta de SVG en un .xml mxlibrary.
    svg_normalize  Normalización de SVG a 64×64 (mide el bbox con Inkscape).
"""
