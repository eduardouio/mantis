#!/usr/bin/env python3
"""
Script para comparar la estructura y datos de dos bases de datos MySQL.
Genera un informe HTML detallado con las diferencias encontradas.

Uso:
    pip install mysql-connector-python
    python docs/compare_databases.py
"""

import mysql.connector
from datetime import datetime

# ============================================================
# PARAMETROS DE CONEXION - MODIFICAR ANTES DE EJECUTAR
# ============================================================

SOURCE_DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "12Cs5003$$!!",
    "database": "mantis_origen",
}

TARGET_DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "12Cs5003$$!!",
    "database": "mantis_destino",
}

OUTPUT_FILE = "docs/db_comparison_report.html"

# ============================================================


def get_connection(config):
    return mysql.connector.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
    )


def get_tables(cursor, database):
    cursor.execute(
        "SELECT TABLE_NAME FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE' "
        "ORDER BY TABLE_NAME",
        (database,),
    )
    return [row[0] for row in cursor.fetchall()]


def get_row_counts(cursor, tables):
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        counts[table] = cursor.fetchone()[0]
    return counts


def get_columns(cursor, database, table):
    cursor.execute(
        "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA "
        "FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY ORDINAL_POSITION",
        (database, table),
    )
    return cursor.fetchall()


def get_primary_keys(cursor, database, table):
    cursor.execute(
        "SELECT COLUMN_NAME "
        "FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND CONSTRAINT_NAME = 'PRIMARY' "
        "ORDER BY ORDINAL_POSITION",
        (database, table),
    )
    return [row[0] for row in cursor.fetchall()]


def get_foreign_keys(cursor, database, table):
    cursor.execute(
        "SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
        "FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND REFERENCED_TABLE_NAME IS NOT NULL "
        "ORDER BY CONSTRAINT_NAME",
        (database, table),
    )
    return cursor.fetchall()


def get_indexes(cursor, database, table):
    cursor.execute(
        "SELECT INDEX_NAME, COLUMN_NAME, NON_UNIQUE, SEQ_IN_INDEX "
        "FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY INDEX_NAME, SEQ_IN_INDEX",
        (database, table),
    )
    return cursor.fetchall()


def extract_db_info(config):
    conn = get_connection(config)
    cursor = conn.cursor()
    db = config["database"]

    tables = get_tables(cursor, db)
    row_counts = get_row_counts(cursor, tables)

    columns = {}
    primary_keys = {}
    foreign_keys = {}
    indexes = {}

    for table in tables:
        columns[table] = get_columns(cursor, db, table)
        primary_keys[table] = get_primary_keys(cursor, db, table)
        foreign_keys[table] = get_foreign_keys(cursor, db, table)
        indexes[table] = get_indexes(cursor, db, table)

    cursor.close()
    conn.close()

    return {
        "tables": tables,
        "row_counts": row_counts,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
    }


def compare(source, target, source_name, target_name):
    issues = []
    warnings = []
    ok_items = []

    src_tables = set(source["tables"])
    tgt_tables = set(target["tables"])

    # --- Cantidad de tablas ---
    if len(src_tables) == len(tgt_tables):
        ok_items.append(f"Cantidad de tablas coincide: {len(src_tables)}")
    else:
        issues.append(
            f"Cantidad de tablas diferente: {source_name}={len(src_tables)}, "
            f"{target_name}={len(tgt_tables)}"
        )

    # --- Tablas faltantes ---
    only_source = sorted(src_tables - tgt_tables)
    only_target = sorted(tgt_tables - src_tables)
    if only_source:
        issues.append(f"Tablas solo en {source_name}: {', '.join(only_source)}")
    if only_target:
        issues.append(f"Tablas solo en {target_name}: {', '.join(only_target)}")
    if not only_source and not only_target:
        ok_items.append("Todas las tablas existen en ambas bases de datos")

    # --- Comparar tablas comunes ---
    common_tables = sorted(src_tables & tgt_tables)
    row_diffs = []
    column_diffs = []
    pk_diffs = []
    fk_diffs = []
    index_diffs = []

    for table in common_tables:
        # Registros
        src_count = source["row_counts"][table]
        tgt_count = target["row_counts"][table]
        if src_count != tgt_count:
            row_diffs.append((table, src_count, tgt_count))

        # Columnas
        src_cols = {c[0]: c for c in source["columns"][table]}
        tgt_cols = {c[0]: c for c in target["columns"][table]}
        src_col_names = set(src_cols.keys())
        tgt_col_names = set(tgt_cols.keys())

        only_src_cols = sorted(src_col_names - tgt_col_names)
        only_tgt_cols = sorted(tgt_col_names - src_col_names)
        if only_src_cols:
            column_diffs.append(
                (table, f"Columnas solo en {source_name}: {', '.join(only_src_cols)}")
            )
        if only_tgt_cols:
            column_diffs.append(
                (table, f"Columnas solo en {target_name}: {', '.join(only_tgt_cols)}")
            )

        # Comparar tipo de columnas comunes
        for col in sorted(src_col_names & tgt_col_names):
            s = src_cols[col]
            t = tgt_cols[col]
            if s[1] != t[1]:
                column_diffs.append(
                    (table, f"Columna '{col}' tipo diferente: {s[1]} vs {t[1]}")
                )
            if s[2] != t[2]:
                column_diffs.append(
                    (table, f"Columna '{col}' nullable diferente: {s[2]} vs {t[2]}")
                )

        if len(src_cols) == len(tgt_cols) and not only_src_cols and not only_tgt_cols:
            pass  # ok
        else:
            column_diffs.append(
                (table, f"Cantidad de columnas: {len(src_cols)} vs {len(tgt_cols)}")
            )

        # Claves primarias
        src_pk = source["primary_keys"][table]
        tgt_pk = target["primary_keys"][table]
        if src_pk != tgt_pk:
            pk_diffs.append((table, str(src_pk), str(tgt_pk)))

        # Claves foraneas
        src_fk = {(r[0], r[1], r[2], r[3]) for r in source["foreign_keys"][table]}
        tgt_fk = {(r[0], r[1], r[2], r[3]) for r in target["foreign_keys"][table]}
        if src_fk != tgt_fk:
            only_src_fk = src_fk - tgt_fk
            only_tgt_fk = tgt_fk - src_fk
            for fk in only_src_fk:
                fk_diffs.append((table, f"Solo en {source_name}: {fk[0]} ({fk[1]} -> {fk[2]}.{fk[3]})"))
            for fk in only_tgt_fk:
                fk_diffs.append((table, f"Solo en {target_name}: {fk[0]} ({fk[1]} -> {fk[2]}.{fk[3]})"))

        # Indices
        src_idx = {(r[0], r[1], r[2]) for r in source["indexes"][table]}
        tgt_idx = {(r[0], r[1], r[2]) for r in target["indexes"][table]}
        if src_idx != tgt_idx:
            only_src_idx = src_idx - tgt_idx
            only_tgt_idx = tgt_idx - src_idx
            for idx in only_src_idx:
                index_diffs.append((table, f"Solo en {source_name}: {idx[0]} col={idx[1]}"))
            for idx in only_tgt_idx:
                index_diffs.append((table, f"Solo en {target_name}: {idx[0]} col={idx[1]}"))

    return {
        "issues": issues,
        "warnings": warnings,
        "ok_items": ok_items,
        "row_diffs": row_diffs,
        "column_diffs": column_diffs,
        "pk_diffs": pk_diffs,
        "fk_diffs": fk_diffs,
        "index_diffs": index_diffs,
        "common_tables": common_tables,
        "source_counts": source["row_counts"],
        "target_counts": target["row_counts"],
    }


def generate_html(result, source_name, target_name):
    total_errors = (
        len(result["issues"])
        + len(result["row_diffs"])
        + len(result["column_diffs"])
        + len(result["pk_diffs"])
        + len(result["fk_diffs"])
        + len(result["index_diffs"])
    )
    status = "CORRECTO" if total_errors == 0 else f"{total_errors} DIFERENCIAS"
    status_color = "#27ae60" if total_errors == 0 else "#e74c3c"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Comparacion de Bases de Datos</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; color: #333; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
    h2 {{ color: #2c3e50; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }}
    .summary {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .status {{ font-size: 24px; font-weight: bold; color: {status_color}; }}
    .info {{ color: #7f8c8d; margin: 5px 0; }}
    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    th {{ background: #2c3e50; color: white; padding: 12px 15px; text-align: left; }}
    td {{ padding: 10px 15px; border-bottom: 1px solid #ecf0f1; }}
    tr:hover {{ background: #f8f9fa; }}
    .ok {{ color: #27ae60; font-weight: bold; }}
    .error {{ color: #e74c3c; font-weight: bold; }}
    .warning {{ color: #f39c12; font-weight: bold; }}
    .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
    .badge-ok {{ background: #d4edda; color: #155724; }}
    .badge-error {{ background: #f8d7da; color: #721c24; }}
    .section {{ background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .match {{ background-color: #d4edda; }}
    .mismatch {{ background-color: #f8d7da; }}
</style>
</head>
<body>
<div class="container">
<h1>Informe de Comparacion de Bases de Datos</h1>

<div class="summary">
    <p class="info">Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p class="info">Origen: <strong>{source_name}</strong></p>
    <p class="info">Destino: <strong>{target_name}</strong></p>
    <p class="status">{status}</p>
</div>
"""

    # Resumen general
    html += '<div class="section"><h2>Resumen General</h2><ul>'
    for item in result["ok_items"]:
        html += f'<li class="ok">&#10004; {item}</li>'
    for item in result["issues"]:
        html += f'<li class="error">&#10008; {item}</li>'
    html += "</ul></div>"

    # Tabla comparativa de registros
    html += '<div class="section"><h2>Registros por Tabla</h2>'
    html += "<table><tr><th>Tabla</th><th>Origen</th><th>Destino</th><th>Estado</th></tr>"
    for table in result["common_tables"]:
        src_c = result["source_counts"].get(table, 0)
        tgt_c = result["target_counts"].get(table, 0)
        match = src_c == tgt_c
        row_class = "match" if match else "mismatch"
        badge = '<span class="badge badge-ok">OK</span>' if match else f'<span class="badge badge-error">DIF: {tgt_c - src_c:+d}</span>'
        html += f'<tr class="{row_class}"><td>{table}</td><td>{src_c:,}</td><td>{tgt_c:,}</td><td>{badge}</td></tr>'
    html += "</table></div>"

    # Diferencias en columnas
    if result["column_diffs"]:
        html += '<div class="section"><h2>Diferencias en Columnas</h2>'
        html += "<table><tr><th>Tabla</th><th>Detalle</th></tr>"
        for table, detail in result["column_diffs"]:
            html += f'<tr class="mismatch"><td>{table}</td><td>{detail}</td></tr>'
        html += "</table></div>"

    # Diferencias en claves primarias
    if result["pk_diffs"]:
        html += '<div class="section"><h2>Diferencias en Claves Primarias</h2>'
        html += f"<table><tr><th>Tabla</th><th>{source_name}</th><th>{target_name}</th></tr>"
        for table, src_pk, tgt_pk in result["pk_diffs"]:
            html += f'<tr class="mismatch"><td>{table}</td><td>{src_pk}</td><td>{tgt_pk}</td></tr>'
        html += "</table></div>"

    # Diferencias en claves foraneas
    if result["fk_diffs"]:
        html += '<div class="section"><h2>Diferencias en Claves Foraneas</h2>'
        html += "<table><tr><th>Tabla</th><th>Detalle</th></tr>"
        for table, detail in result["fk_diffs"]:
            html += f'<tr class="mismatch"><td>{table}</td><td>{detail}</td></tr>'
        html += "</table></div>"

    # Diferencias en indices
    if result["index_diffs"]:
        html += '<div class="section"><h2>Diferencias en Indices</h2>'
        html += "<table><tr><th>Tabla</th><th>Detalle</th></tr>"
        for table, detail in result["index_diffs"]:
            html += f'<tr class="mismatch"><td>{table}</td><td>{detail}</td></tr>'
        html += "</table></div>"

    # Si no hay diferencias de estructura
    no_struct_diffs = (
        not result["column_diffs"]
        and not result["pk_diffs"]
        and not result["fk_diffs"]
        and not result["index_diffs"]
    )
    if no_struct_diffs:
        html += '<div class="section"><h2>Estructura</h2>'
        html += '<p class="ok">&#10004; La estructura de todas las tablas es identica (columnas, claves primarias, claves foraneas e indices).</p>'
        html += "</div>"

    html += "</div></body></html>"
    return html


def main():
    print(f"Conectando a origen: {SOURCE_DB['host']}:{SOURCE_DB['port']}/{SOURCE_DB['database']}")
    source = extract_db_info(SOURCE_DB)
    print(f"  -> {len(source['tables'])} tablas encontradas")

    print(f"Conectando a destino: {TARGET_DB['host']}:{TARGET_DB['port']}/{TARGET_DB['database']}")
    target = extract_db_info(TARGET_DB)
    print(f"  -> {len(target['tables'])} tablas encontradas")

    print("Comparando...")
    source_label = f"{SOURCE_DB['host']}/{SOURCE_DB['database']}"
    target_label = f"{TARGET_DB['host']}/{TARGET_DB['database']}"
    result = compare(source, target, source_label, target_label)

    html = generate_html(result, source_label, target_label)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nInforme generado: {OUTPUT_FILE}")

    total_errors = (
        len(result["issues"])
        + len(result["row_diffs"])
        + len(result["column_diffs"])
        + len(result["pk_diffs"])
        + len(result["fk_diffs"])
        + len(result["index_diffs"])
    )
    if total_errors == 0:
        print("RESULTADO: Las bases de datos son identicas.")
    else:
        print(f"RESULTADO: Se encontraron {total_errors} diferencias. Revisa el informe HTML.")


if __name__ == "__main__":
    main()
