import psycopg2
from psycopg2.extras import DictCursor
import sqlite3
from collections import defaultdict
import textwrap


class ContextConstructor:
    """Class for building database context as a formatted string."""
    
    SYSTEM_SCHEMAS_PG = {
        "pg_catalog",
        "information_schema",
        "pg_toast",
        "pg_temp_1",
        "pg_toast_temp_1",
    }
    
    def __init__(self, db_backend="sqlite", postgres_config=None, sqlite_path="./db.sqlite"):
        """
        Initialize ContextBuilder.
        
        Args:
            db_backend: "postgres" or "sqlite"
            postgres_config: dict with host, port, dbname, user, password
            sqlite_path: path to SQLite database file
        """
        self.db_backend = db_backend
        self.postgres_config = postgres_config or {
            "host": "localhost",
            "port": 5432,
            "dbname": "your_db_name",
            "user": "your_username",
            "password": "your_password",
        }
        self.sqlite_path = sqlite_path
    
    @staticmethod
    def _decode_action(code):
        """Map postgres single-letter FK action codes."""
        mapping = {
            "a": "NO ACTION",
            "r": "RESTRICT",
            "c": "CASCADE",
            "n": "SET NULL",
            "d": "SET DEFAULT",
        }
        return mapping.get(code, code)
    
    @staticmethod
    def _fetch_all(cursor, query, params=None):
        """Execute query and fetch all results."""
        cursor.execute(query, params or ())
        return cursor.fetchall()
    
    def introspect_postgres(self):
        """Introspect PostgreSQL database schema."""
        conn = psycopg2.connect(**self.postgres_config)
        cur = conn.cursor(cursor_factory=DictCursor)

        # --- tables
        tables = self._fetch_all(cur, """
            SELECT
                n.nspname        AS schema_name,
                c.relname        AS table_name,
                c.relkind        AS relkind,
                obj_description(c.oid) AS table_comment
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r', 'p', 'v', 'm')
            ORDER BY schema_name, table_name;
        """)

        # --- columns
        columns = self._fetch_all(cur, """
            SELECT
                n.nspname      AS schema_name,
                c.relname      AS table_name,
                a.attnum       AS ordinal_position,
                a.attname      AS column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                pg_get_expr(ad.adbin, ad.adrelid) AS column_default,
                a.attnotnull   AS not_null,
                col_description(a.attrelid, a.attnum) AS column_comment
            FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            LEFT JOIN pg_attrdef ad ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
            WHERE
                a.attnum > 0
                AND NOT a.attisdropped
                AND c.relkind IN ('r', 'p', 'v', 'm')
            ORDER BY schema_name, table_name, ordinal_position;
        """)

        # --- primary keys
        pks = self._fetch_all(cur, """
            SELECT
                n.nspname      AS schema_name,
                c.relname      AS table_name,
                con.conname    AS constraint_name,
                a.attname      AS column_name,
                con.conkey     AS attnums
            FROM pg_constraint con
            JOIN pg_class c ON con.conrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            JOIN unnest(con.conkey) WITH ORDINALITY AS cols(attnum, ordinality) ON true
            JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = cols.attnum
            WHERE con.contype = 'p'
            ORDER BY schema_name, table_name, constraint_name, cols.ordinality;
        """)

        # --- foreign keys
        fks = self._fetch_all(cur, """
            SELECT
                src_ns.nspname           AS src_schema,
                src_tbl.relname          AS src_table,
                src_col.attname          AS src_column,
                tgt_ns.nspname           AS tgt_schema,
                tgt_tbl.relname          AS tgt_table,
                tgt_col.attname          AS tgt_column,
                con.conname              AS constraint_name,
                con.confdeltype          AS on_delete_rule,
                con.confupdtype          AS on_update_rule,
                cols_src.ordinality      AS col_order
            FROM pg_constraint con
            JOIN pg_class src_tbl ON con.conrelid = src_tbl.oid
            JOIN pg_namespace src_ns ON src_tbl.relnamespace = src_ns.oid
            JOIN pg_class tgt_tbl ON con.confrelid = tgt_tbl.oid
            JOIN pg_namespace tgt_ns ON tgt_tbl.relnamespace = tgt_ns.oid
            JOIN unnest(con.conkey, con.confkey) WITH ORDINALITY AS cols_src(src_attnum, tgt_attnum, ordinality) ON true
            JOIN pg_attribute src_col ON src_col.attrelid = src_tbl.oid AND src_col.attnum = cols_src.src_attnum
            JOIN pg_attribute tgt_col ON tgt_col.attrelid = tgt_tbl.oid AND tgt_col.attnum = cols_src.tgt_attnum
            WHERE con.contype = 'f'
            ORDER BY src_schema, src_table, constraint_name, col_order;
        """)

        # --- uniques
        uniques = self._fetch_all(cur, """
            SELECT
                n.nspname      AS schema_name,
                c.relname      AS table_name,
                con.conname    AS constraint_name,
                a.attname      AS column_name,
                cols.ordinality AS col_order
            FROM pg_constraint con
            JOIN pg_class c ON con.conrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            JOIN unnest(con.conkey) WITH ORDINALITY AS cols(attnum, ordinality) ON true
            JOIN pg_attribute a ON a.attrelid = con.conrelid AND a.attnum = cols.attnum
            WHERE con.contype = 'u'
            ORDER BY schema_name, table_name, constraint_name, col_order;
        """)

        # --- indexes
        indexes = self._fetch_all(cur, """
            SELECT
                ns.n.nspname                           AS schema_name,
                tbl.relname                            AS table_name,
                idx.relname                            AS index_name,
                pg_get_indexdef(i.indexrelid)          AS index_def,
                i.indisunique                          AS is_unique,
                i.indisprimary                         AS is_primary
            FROM pg_index i
            JOIN pg_class idx ON idx.oid = i.indexrelid
            JOIN pg_class tbl ON tbl.oid = i.indrelid
            JOIN pg_namespace ns.n ON ns.n.oid = tbl.relnamespace
            WHERE ns.n.nspname NOT IN ('pg_catalog', 'pg_toast', 'information_schema')
            ORDER BY schema_name, table_name, index_name;
        """.replace("ns.n", "ns"))  # little hack so Python doesn't think ns.n is attr access

        cur.close()
        conn.close()

        # ---- assemble
        schemas = defaultdict(lambda: defaultdict(dict))

        for row in tables:
            s = row["schema_name"]
            t = row["table_name"]
            if s in self.SYSTEM_SCHEMAS_PG:
                continue
            schemas[s][t] = {
                "kind": row["relkind"],
                "comment": row["table_comment"],
                "columns": [],
                "pk": [],
                "fks": [],
                "uniques": defaultdict(list),
                "indexes": [],
            }

        for col in columns:
            s = col["schema_name"]
            t = col["table_name"]
            if s not in schemas or t not in schemas[s]:
                continue
            schemas[s][t]["columns"].append({
                "name": col["column_name"],
                "type": col["data_type"],
                "default": col["column_default"],
                "not_null": col["not_null"],
                "comment": col["column_comment"],
                "order": col["ordinal_position"],
            })

        # PK
        pk_map = defaultdict(lambda: defaultdict(list))
        for row in pks:
            pk_map[row["schema_name"]][row["table_name"]].append(row["column_name"])
        for s, tables_map in pk_map.items():
            for t, cols_list in tables_map.items():
                if s in schemas and t in schemas[s]:
                    schemas[s][t]["pk"] = cols_list

        # FK
        fk_tmp = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
            "src_cols": [],
            "tgt_schema": None,
            "tgt_table": None,
            "tgt_cols": [],
            "on_delete": None,
            "on_update": None,
        })))

        for row in fks:
            block = fk_tmp[row["src_schema"]][row["src_table"]][row["constraint_name"]]
            block["tgt_schema"] = row["tgt_schema"]
            block["tgt_table"] = row["tgt_table"]
            block["on_delete"] = self._decode_action(row["on_delete_rule"])
            block["on_update"] = self._decode_action(row["on_update_rule"])
            block["src_cols"].append(row["src_column"])
            block["tgt_cols"].append(row["tgt_column"])

        for s, tables_map in fk_tmp.items():
            for t, constraints in tables_map.items():
                if s in schemas and t in schemas[s]:
                    for cname, data in constraints.items():
                        schemas[s][t]["fks"].append({
                            "name": cname,
                            "src_cols": data["src_cols"],
                            "tgt": f"{data['tgt_schema']}.{data['tgt_table']}",
                            "tgt_cols": data["tgt_cols"],
                            "on_delete": data["on_delete"],
                            "on_update": data["on_update"],
                        })

        # uniques
        uniq_tmp = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for row in uniques:
            uniq_tmp[row["schema_name"]][row["table_name"]][row["constraint_name"]].append(row["column_name"])

        for s, tables_map in uniq_tmp.items():
            for t, constraints in tables_map.items():
                if s in schemas and t in schemas[s]:
                    for cname, cols_list in constraints.items():
                        schemas[s][t]["uniques"][cname] = cols_list

        # indexes
        for row in indexes:
            s = row["schema_name"]
            t = row["table_name"]
            if s in schemas and t in schemas[s]:
                schemas[s][t]["indexes"].append({
                    "name": row["index_name"],
                    "def": row["index_def"],
                    "unique": row["is_unique"],
                    "primary": row["is_primary"],
                })

        return schemas


    def introspect_sqlite(self):
        """Introspect SQLite database schema."""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # таблицы и вьюхи из sqlite_master
        cur.execute("""
            SELECT name, type, sql
            FROM sqlite_master
            WHERE type IN ('table', 'view')
            ORDER BY name;
        """)
        master_rows = cur.fetchall()

        # мы будем считать, что всё в схеме "main"
        schemas = defaultdict(lambda: defaultdict(dict))
        schema_name = "main"

        for row in master_rows:
            tname = row["name"]
            ttype = row["type"]
            # пропускаем внутренние
            if tname.startswith("sqlite_"):
                continue

            schemas[schema_name][tname] = {
                "kind": ttype[0],  # 't'/'v' just to be closer to postgres idea
                "comment": None,   # SQLite не хранит comments отдельно
                "columns": [],
                "pk": [],
                "fks": [],
                "uniques": defaultdict(list),
                "indexes": [],
            }

        # колонки
        for table_name in list(schemas[schema_name].keys()):
            # PRAGMA table_info
            cur.execute(f'PRAGMA table_info("{table_name}");')
            cols = cur.fetchall()
            for c in cols:
                # c keys: cid, name, type, notnull, dflt_value, pk
                schemas[schema_name][table_name]["columns"].append({
                    "name": c["name"],
                    "type": c["type"],
                    "default": c["dflt_value"],
                    "not_null": bool(c["notnull"]),
                    "comment": None,
                    "order": c["cid"],
                })
                if c["pk"]:
                    schemas[schema_name][table_name]["pk"].append(c["name"])

            # PRAGMA foreign_key_list
            cur.execute(f'PRAGMA foreign_key_list("{table_name}");')
            fk_rows = cur.fetchall()
            # fk_rows: id, seq, table, from, to, on_update, on_delete, match
            fk_map = defaultdict(lambda: {
                "src_cols": [],
                "tgt": None,
                "tgt_cols": [],
                "on_delete": None,
                "on_update": None,
            })

            for fk in fk_rows:
                fid = fk["id"]  # group by FK id because compound FK has multiple rows
                block = fk_map[fid]
                block["tgt"] = fk["table"]
                block["src_cols"].append(fk["from"])
                block["tgt_cols"].append(fk["to"])
                block["on_delete"] = fk["on_delete"]
                block["on_update"] = fk["on_update"]

            for fid, data in fk_map.items():
                schemas[schema_name][table_name]["fks"].append({
                    "name": f"fk_{table_name}_{fid}",
                    "src_cols": data["src_cols"],
                    "tgt": data["tgt"],
                    "tgt_cols": data["tgt_cols"],
                    "on_delete": data["on_delete"],
                    "on_update": data["on_update"],
                })

            # индексы
            cur.execute(f'PRAGMA index_list("{table_name}");')
            idx_list = cur.fetchall()
            # idx_list: seq, name, unique, origin, partial
            for idx in idx_list:
                idx_name = idx["name"]
                unique = bool(idx["unique"])

                # columns in index
                cur.execute(f'PRAGMA index_info("{idx_name}");')
                idx_cols = cur.fetchall()
                cols_ordered = [r["name"] for r in sorted(idx_cols, key=lambda x: x["seqno"])]

                # в SQLite uniqueness через UNIQUE = unique
                if unique:
                    schemas[schema_name][table_name]["uniques"][idx_name] = cols_ordered

                # индекс дефолтного вида
                # у SQLite нет pg_get_indexdef, но можно примерно воссоздать
                index_def = f"INDEX {idx_name} ({', '.join(cols_ordered)})"
                if unique:
                    index_def = "UNIQUE " + index_def

                schemas[schema_name][table_name]["indexes"].append({
                    "name": idx_name,
                    "def": index_def,
                    "unique": unique,
                    "primary": False,  # primary key уже отражён в pk
                })

        cur.close()
        conn.close()

        return schemas


    def _format_schemas(self, schemas):
        """Format schemas dictionary as a string."""
        lines = []
        for schema_name, tables_map in sorted(schemas.items()):
            lines.append(f"SCHEMA {schema_name}")
            lines.append("=" * (7 + len(schema_name)))
            for table_name, meta in sorted(tables_map.items()):
                lines.append("")
                lines.append(f"TABLE {schema_name}.{table_name}")
                lines.append("-" * (6 + len(schema_name) + len(table_name)))

                if meta.get("comment"):
                    lines.append(f"  COMMENT: {meta['comment']}")

                lines.append("  COLUMNS:")
                for col in sorted(meta["columns"], key=lambda c: c["order"]):
                    line = f"    - {col['name']} {col['type']}"
                    if col["not_null"]:
                        line += " NOT NULL"
                    if col["default"] is not None:
                        line += f" DEFAULT {col['default']}"
                    lines.append(line)
                    if col.get("comment"):
                        wrapped = textwrap.fill(
                            col["comment"],
                            subsequent_indent="        ",
                            initial_indent="        ",
                        )
                        lines.append(wrapped)

                if meta.get("pk"):
                    lines.append("  PRIMARY KEY:")
                    lines.append(f"    ({', '.join(meta['pk'])})")

                uniques = meta.get("uniques", {})
                if uniques:
                    lines.append("  UNIQUE CONSTRAINTS / UNIQUE INDEXES:")
                    for cname, cols_list in uniques.items():
                        lines.append(f"    {cname}: ({', '.join(cols_list)})")

                fks = meta.get("fks", [])
                if fks:
                    lines.append("  FOREIGN KEYS:")
                    for fk in fks:
                        tgt_desc = fk["tgt"]
                        if "." not in tgt_desc and schema_name != "main":
                            # Postgres already has schema in fk["tgt"], SQLite doesn't.
                            # For SQLite we'll just assume same schema ("main").
                            tgt_full = f"{schema_name}.{tgt_desc}"
                        else:
                            tgt_full = tgt_desc
                        lines.append(f"    {fk['name']}: ({', '.join(fk['src_cols'])}) -> {tgt_full}({', '.join(fk['tgt_cols'])})")
                        if fk.get("on_update") or fk.get("on_delete"):
                            lines.append(f"        ON UPDATE {fk.get('on_update')} ON DELETE {fk.get('on_delete')}")

                idxs = meta.get("indexes", [])
                if idxs:
                    lines.append("  INDEXES:")
                    for idx in idxs:
                        lines.append(f"    - {idx['name']}: {idx['def']}")

                lines.append("")
        
        return "\n".join(lines)
    
    def build(self):
        """Build and return database context as a formatted string."""
        if self.db_backend == "postgres":
            schemas = self.introspect_postgres()
        elif self.db_backend == "sqlite":
            schemas = self.introspect_sqlite()
        else:
            raise ValueError("db_backend must be 'postgres' or 'sqlite'")
        
        return self._format_schemas(schemas)


def main():
    """Main function for command-line usage."""
    builder = ContextConstructor(db_backend="sqlite", sqlite_path="./db.sqlite")
    result = builder.build()
    print(result)


if __name__ == "__main__":
    main()
