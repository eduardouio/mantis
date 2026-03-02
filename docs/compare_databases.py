#!/usr/bin/env python3
"""
Script para comparar la estructura y datos de dos bases de datos MySQL.
Genera un informe HTML detallado con las diferencias encontradas.

Uso:
    pip install mysql-connector-python

    python docs/compare_databases.py --validate-all
    python docs/compare_databases.py --validate-all --password mi_clave
    python docs/compare_databases.py --validate-tables
    python docs/compare_databases.py --validate-data --table nombre_de_la_tabla

    Si no se pasa --password, se solicita de forma interactiva (oculto).
"""

import argparse
import getpass
import hashlib
import mysql.connector
from datetime import datetime

# ============================================================
# PARAMETROS DE CONEXION - MODIFICAR ANTES DE EJECUTAR
# ============================================================

SOURCE_DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "database": "mantis_origen",
}

TARGET_DB = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
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


def extract_db_info(config, only_tables=False):
    conn = get_connection(config)
    cursor = conn.cursor()
    db = config["database"]

    tables = get_tables(cursor, db)
    row_counts = get_row_counts(cursor, tables)

    columns = {}
    primary_keys = {}
    foreign_keys = {}
    indexes = {}

    if not only_tables:
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


def extract_table_data(config, table):
    """Extrae los datos completos de una tabla para comparacion fila a fila."""
    conn = get_connection(config)
    cursor = conn.cursor()
    db = config["database"]

    # Obtener columnas ordenadas
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s "
        "ORDER BY ORDINAL_POSITION",
        (db, table),
    )
    col_names = [row[0] for row in cursor.fetchall()]

    # Obtener clave primaria para ordenar
    pk_cols = get_primary_keys(cursor, db, table)
    order_by = ", ".join(f"`{c}`" for c in pk_cols) if pk_cols else f"`{col_names[0]}`"

    # Obtener total de registros
    cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
    total = cursor.fetchone()[0]

    # Obtener todos los registros ordenados por PK
    cols_select = ", ".join(f"`{c}`" for c in col_names)
    cursor.execute(f"SELECT {cols_select} FROM `{table}` ORDER BY {order_by}")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "columns": col_names,
        "pk_columns": pk_cols,
        "rows": rows,
        "total": total,
    }


def compare_table_data(source_data, target_data, table_name, source_name, target_name):
    """Compara los datos fila a fila de una tabla entre origen y destino."""
    result = {
        "table": table_name,
        "source_total": source_data["total"],
        "target_total": target_data["total"],
        "columns_match": source_data["columns"] == target_data["columns"],
        "source_columns": source_data["columns"],
        "target_columns": target_data["columns"],
        "missing_in_target": [],
        "missing_in_source": [],
        "different_rows": [],
        "identical_rows": 0,
    }

    if not result["columns_match"]:
        return result

    # Crear hash de cada fila para comparacion rapida
    pk_cols = source_data["pk_columns"]
    col_names = source_data["columns"]

    if pk_cols:
        pk_indexes = [col_names.index(pk) for pk in pk_cols]
    else:
        pk_indexes = [0]

    def row_pk(row):
        return tuple(row[i] for i in pk_indexes)

    def row_hash(row):
        return hashlib.md5(str(row).encode()).hexdigest()

    # Indexar filas por PK
    src_by_pk = {}
    for row in source_data["rows"]:
        pk = row_pk(row)
        src_by_pk[pk] = row

    tgt_by_pk = {}
    for row in target_data["rows"]:
        pk = row_pk(row)
        tgt_by_pk[pk] = row

    src_keys = set(src_by_pk.keys())
    tgt_keys = set(tgt_by_pk.keys())

    # Filas solo en origen
    for pk in sorted(src_keys - tgt_keys):
        pk_display = dict(zip(pk_cols or [col_names[0]], pk))
        result["missing_in_target"].append(pk_display)

    # Filas solo en destino
    for pk in sorted(tgt_keys - src_keys):
        pk_display = dict(zip(pk_cols or [col_names[0]], pk))
        result["missing_in_source"].append(pk_display)

    # Filas en ambas: comparar contenido
    for pk in sorted(src_keys & tgt_keys):
        src_row = src_by_pk[pk]
        tgt_row = tgt_by_pk[pk]
        if row_hash(src_row) != row_hash(tgt_row):
            diffs = []
            for i, col in enumerate(col_names):
                if src_row[i] != tgt_row[i]:
                    diffs.append({
                        "column": col,
                        "source_value": str(src_row[i]),
                        "target_value": str(tgt_row[i]),
                    })
            pk_display = dict(zip(pk_cols or [col_names[0]], pk))
            result["different_rows"].append({"pk": pk_display, "diffs": diffs})
        else:
            result["identical_rows"] += 1

    return result


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

        # Si solo se pidio validar tablas, saltar estructura detallada
        if not source["columns"]:
            continue

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


# ============================================================
# GENERACION DE HTML
# ============================================================

HTML_STYLE = """
<style>
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; color: #333; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
    h2 { color: #2c3e50; margin-top: 30px; border-left: 4px solid #3498db; padding-left: 10px; }
    h3 { color: #34495e; }
    .summary { background: white; border-radius: 8px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .info { color: #7f8c8d; margin: 5px 0; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    th { background: #2c3e50; color: white; padding: 12px 15px; text-align: left; }
    td { padding: 10px 15px; border-bottom: 1px solid #ecf0f1; }
    tr:hover { background: #f8f9fa; }
    .ok { color: #27ae60; font-weight: bold; }
    .error { color: #e74c3c; font-weight: bold; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .badge-ok { background: #d4edda; color: #155724; }
    .badge-error { background: #f8d7da; color: #721c24; }
    .section { background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .match { background-color: #d4edda; }
    .mismatch { background-color: #f8d7da; }
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }
    .stat-card { background: white; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .stat-number { font-size: 32px; font-weight: bold; }
    .stat-label { color: #7f8c8d; font-size: 14px; }
</style>
"""


def html_header(title, source_name, target_name, subtitle=""):
    status_line = f'<p class="info">{subtitle}</p>' if subtitle else ""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{HTML_STYLE}
</head>
<body>
<div class="container">
<h1>{title}</h1>
<div class="summary">
    <p class="info">Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p class="info">Origen: <strong>{source_name}</strong></p>
    <p class="info">Destino: <strong>{target_name}</strong></p>
    {status_line}
</div>
"""


HTML_FOOTER = "</div></body></html>"


def generate_html_validate_all(result, source_name, target_name):
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

    html = html_header(
        "Informe Completo de Comparacion de Bases de Datos",
        source_name, target_name,
        f'<span style="font-size:24px;font-weight:bold;color:{status_color}">{status}</span>',
    )

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

    html += HTML_FOOTER
    return html


def generate_html_validate_tables(result, source_name, target_name):
    total_issues = len(result["issues"]) + len(result["row_diffs"])
    status = "CORRECTO" if total_issues == 0 else f"{total_issues} DIFERENCIAS"
    status_color = "#27ae60" if total_issues == 0 else "#e74c3c"

    html = html_header(
        "Validacion de Tablas",
        source_name, target_name,
        f'<span style="font-size:24px;font-weight:bold;color:{status_color}">{status}</span>',
    )

    html += '<div class="section"><h2>Resumen</h2><ul>'
    for item in result["ok_items"]:
        html += f'<li class="ok">&#10004; {item}</li>'
    for item in result["issues"]:
        html += f'<li class="error">&#10008; {item}</li>'
    html += "</ul></div>"

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

    html += HTML_FOOTER
    return html


def generate_html_validate_data(data_result, source_name, target_name):
    table_name = data_result["table"]
    total_issues = (
        len(data_result["missing_in_target"])
        + len(data_result["missing_in_source"])
        + len(data_result["different_rows"])
    )
    status = "IDENTICA" if total_issues == 0 else f"{total_issues} DIFERENCIAS"
    status_color = "#27ae60" if total_issues == 0 else "#e74c3c"

    html = html_header(
        f"Validacion de Datos: {table_name}",
        source_name, target_name,
        f'<span style="font-size:24px;font-weight:bold;color:{status_color}">{status}</span>',
    )

    # Estadisticas
    html += '<div class="stats-grid">'
    html += f'<div class="stat-card"><div class="stat-number">{data_result["source_total"]:,}</div><div class="stat-label">Registros en Origen</div></div>'
    html += f'<div class="stat-card"><div class="stat-number">{data_result["target_total"]:,}</div><div class="stat-label">Registros en Destino</div></div>'
    html += f'<div class="stat-card"><div class="stat-number ok">{data_result["identical_rows"]:,}</div><div class="stat-label">Filas Identicas</div></div>'
    html += f'<div class="stat-card"><div class="stat-number error">{total_issues}</div><div class="stat-label">Diferencias</div></div>'
    html += "</div>"

    # Verificar columnas
    if not data_result["columns_match"]:
        html += '<div class="section"><h2>Columnas NO coinciden</h2>'
        html += f'<p>Origen: {", ".join(data_result["source_columns"])}</p>'
        html += f'<p>Destino: {", ".join(data_result["target_columns"])}</p>'
        html += "</div>"
        html += HTML_FOOTER
        return html

    # Filas faltantes en destino
    if data_result["missing_in_target"]:
        html += f'<div class="section"><h2>Filas solo en Origen ({len(data_result["missing_in_target"])})</h2>'
        html += "<table><tr><th>Clave Primaria</th></tr>"
        for pk in data_result["missing_in_target"][:100]:
            pk_str = ", ".join(f"{k}={v}" for k, v in pk.items())
            html += f'<tr class="mismatch"><td>{pk_str}</td></tr>'
        if len(data_result["missing_in_target"]) > 100:
            html += f'<tr><td>... y {len(data_result["missing_in_target"]) - 100} mas</td></tr>'
        html += "</table></div>"

    # Filas faltantes en origen
    if data_result["missing_in_source"]:
        html += f'<div class="section"><h2>Filas solo en Destino ({len(data_result["missing_in_source"])})</h2>'
        html += "<table><tr><th>Clave Primaria</th></tr>"
        for pk in data_result["missing_in_source"][:100]:
            pk_str = ", ".join(f"{k}={v}" for k, v in pk.items())
            html += f'<tr class="mismatch"><td>{pk_str}</td></tr>'
        if len(data_result["missing_in_source"]) > 100:
            html += f'<tr><td>... y {len(data_result["missing_in_source"]) - 100} mas</td></tr>'
        html += "</table></div>"

    # Filas con diferencias
    if data_result["different_rows"]:
        html += f'<div class="section"><h2>Filas con Datos Diferentes ({len(data_result["different_rows"])})</h2>'
        html += "<table><tr><th>Clave Primaria</th><th>Columna</th><th>Origen</th><th>Destino</th></tr>"
        shown = 0
        for row_diff in data_result["different_rows"]:
            if shown >= 200:
                break
            pk_str = ", ".join(f"{k}={v}" for k, v in row_diff["pk"].items())
            for diff in row_diff["diffs"]:
                src_val = diff["source_value"][:80]
                tgt_val = diff["target_value"][:80]
                html += f'<tr class="mismatch"><td>{pk_str}</td><td>{diff["column"]}</td><td>{src_val}</td><td>{tgt_val}</td></tr>'
                shown += 1
        if len(data_result["different_rows"]) > 200:
            html += f'<tr><td colspan="4">... y mas filas con diferencias</td></tr>'
        html += "</table></div>"

    # Todo ok
    if total_issues == 0:
        html += '<div class="section">'
        html += f'<p class="ok">&#10004; Los datos de la tabla <strong>{table_name}</strong> son identicos en ambas bases de datos ({data_result["identical_rows"]:,} filas verificadas).</p>'
        html += "</div>"

    html += HTML_FOOTER
    return html


# ============================================================
# COMANDOS PRINCIPALES
# ============================================================

def cmd_validate_all():
    print("=" * 60)
    print("  VALIDACION COMPLETA")
    print("=" * 60)

    print(f"\nConectando a origen: {SOURCE_DB['host']}:{SOURCE_DB['port']}/{SOURCE_DB['database']}")
    source = extract_db_info(SOURCE_DB)
    print(f"  -> {len(source['tables'])} tablas encontradas")

    print(f"Conectando a destino: {TARGET_DB['host']}:{TARGET_DB['port']}/{TARGET_DB['database']}")
    target = extract_db_info(TARGET_DB)
    print(f"  -> {len(target['tables'])} tablas encontradas")

    print("Comparando estructura completa...")
    source_label = f"{SOURCE_DB['host']}/{SOURCE_DB['database']}"
    target_label = f"{TARGET_DB['host']}/{TARGET_DB['database']}"
    result = compare(source, target, source_label, target_label)

    html = generate_html_validate_all(result, source_label, target_label)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    total_errors = (
        len(result["issues"])
        + len(result["row_diffs"])
        + len(result["column_diffs"])
        + len(result["pk_diffs"])
        + len(result["fk_diffs"])
        + len(result["index_diffs"])
    )

    print(f"\nInforme generado: {OUTPUT_FILE}")
    if total_errors == 0:
        print("RESULTADO: Las bases de datos son identicas.")
    else:
        print(f"RESULTADO: Se encontraron {total_errors} diferencias. Revisa el informe HTML.")


def cmd_validate_tables():
    print("=" * 60)
    print("  VALIDACION DE TABLAS")
    print("=" * 60)

    print(f"\nConectando a origen: {SOURCE_DB['host']}:{SOURCE_DB['port']}/{SOURCE_DB['database']}")
    source = extract_db_info(SOURCE_DB, only_tables=True)
    print(f"  -> {len(source['tables'])} tablas encontradas")

    print(f"Conectando a destino: {TARGET_DB['host']}:{TARGET_DB['port']}/{TARGET_DB['database']}")
    target = extract_db_info(TARGET_DB, only_tables=True)
    print(f"  -> {len(target['tables'])} tablas encontradas")

    print("Comparando tablas y registros...")
    source_label = f"{SOURCE_DB['host']}/{SOURCE_DB['database']}"
    target_label = f"{TARGET_DB['host']}/{TARGET_DB['database']}"
    result = compare(source, target, source_label, target_label)

    html = generate_html_validate_tables(result, source_label, target_label)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nInforme generado: {OUTPUT_FILE}")
    if not result["issues"] and not result["row_diffs"]:
        print("RESULTADO: Tablas y conteos identicos.")
    else:
        print(f"RESULTADO: Se encontraron diferencias. Revisa el informe HTML.")


def cmd_validate_data(table_name):
    print("=" * 60)
    print(f"  VALIDACION DE DATOS: {table_name}")
    print("=" * 60)

    source_label = f"{SOURCE_DB['host']}/{SOURCE_DB['database']}"
    target_label = f"{TARGET_DB['host']}/{TARGET_DB['database']}"

    # Verificar que la tabla existe en ambas BD
    print(f"\nConectando a origen...")
    src_conn = get_connection(SOURCE_DB)
    src_cursor = src_conn.cursor()
    src_tables = get_tables(src_cursor, SOURCE_DB["database"])
    src_cursor.close()
    src_conn.close()

    print(f"Conectando a destino...")
    tgt_conn = get_connection(TARGET_DB)
    tgt_cursor = tgt_conn.cursor()
    tgt_tables = get_tables(tgt_cursor, TARGET_DB["database"])
    tgt_cursor.close()
    tgt_conn.close()

    if table_name not in src_tables:
        print(f"ERROR: La tabla '{table_name}' no existe en {source_label}")
        return
    if table_name not in tgt_tables:
        print(f"ERROR: La tabla '{table_name}' no existe en {target_label}")
        return

    print(f"Extrayendo datos de '{table_name}' en origen...")
    source_data = extract_table_data(SOURCE_DB, table_name)
    print(f"  -> {source_data['total']:,} registros")

    print(f"Extrayendo datos de '{table_name}' en destino...")
    target_data = extract_table_data(TARGET_DB, table_name)
    print(f"  -> {target_data['total']:,} registros")

    print("Comparando fila a fila...")
    data_result = compare_table_data(source_data, target_data, table_name, source_label, target_label)

    html = generate_html_validate_data(data_result, source_label, target_label)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    total_issues = (
        len(data_result["missing_in_target"])
        + len(data_result["missing_in_source"])
        + len(data_result["different_rows"])
    )

    print(f"\nInforme generado: {OUTPUT_FILE}")
    print(f"  Filas identicas: {data_result['identical_rows']:,}")
    print(f"  Solo en origen:  {len(data_result['missing_in_target'])}")
    print(f"  Solo en destino: {len(data_result['missing_in_source'])}")
    print(f"  Diferentes:      {len(data_result['different_rows'])}")

    if total_issues == 0:
        print(f"RESULTADO: La tabla '{table_name}' es identica en ambas bases de datos.")
    else:
        print(f"RESULTADO: Se encontraron {total_issues} diferencias. Revisa el informe HTML.")


def main():
    parser = argparse.ArgumentParser(
        description="Comparar dos bases de datos MySQL y generar informe HTML.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python docs/compare_databases.py --validate-all
  python docs/compare_databases.py --validate-tables
  python docs/compare_databases.py --validate-data --table auth_user
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--validate-all",
        action="store_true",
        help="Validacion completa: tablas, estructura, columnas, claves, indices y conteo de registros",
    )
    group.add_argument(
        "--validate-tables",
        action="store_true",
        help="Solo validar nombres de tablas y conteo de registros",
    )
    group.add_argument(
        "--validate-data",
        action="store_true",
        help="Comparar datos fila a fila de una tabla especifica (requiere --table)",
    )

    parser.add_argument(
        "--table",
        type=str,
        help="Nombre de la tabla a comparar (solo con --validate-data)",
    )
    parser.add_argument(
        "--password", "-p",
        type=str,
        default=None,
        help="Password de MySQL. Si no se proporciona, se solicita de forma interactiva",
    )

    args = parser.parse_args()

    if args.validate_data and not args.table:
        parser.error("--validate-data requiere --table nombre_de_la_tabla")

    # Obtener password
    password = args.password
    if password is None:
        password = getpass.getpass("Password de MySQL: ")

    SOURCE_DB["password"] = password
    TARGET_DB["password"] = password

    if args.validate_all:
        cmd_validate_all()
    elif args.validate_tables:
        cmd_validate_tables()
    elif args.validate_data:
        cmd_validate_data(args.table)


if __name__ == "__main__":
    main()
