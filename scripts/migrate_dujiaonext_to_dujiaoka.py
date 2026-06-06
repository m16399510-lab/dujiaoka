#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert Dujiao-Next PostgreSQL data into the old dujiaoka MySQL schema.

Default mode is dry-run only. Use --apply to write to MySQL.

Example:
  python scripts/migrate_dujiaonext_to_dujiaoka.py ^
    --pg-dsn "postgresql://user:pass@127.0.0.1:5432/dujiao_next" ^
    --mysql-host 127.0.0.1 --mysql-port 3306 --mysql-db dujiaoka ^
    --mysql-user root --mysql-password "password" --dry-run
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import decimal
import json
import os
import re
import sys
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

try:
    import pymysql
except ImportError:
    pymysql = None


OLD_STATUS_WAIT_PAY = 1
OLD_STATUS_PENDING = 2
OLD_STATUS_COMPLETED = 4
OLD_STATUS_FAILURE = 5
OLD_STATUS_EXPIRED = -1
OLD_STATUS_ABNORMAL = 6

OLD_AUTO_DELIVERY = 1
OLD_CARMI_UNSOLD = 1
OLD_CARMI_SOLD = 2

DATETIME_TEXT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")
LOCALE_KEYS = ("zh-CN", "zh_CN", "zh", "zh-TW", "zh_TW", "en-US", "en_US", "en")


def now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def scalar(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    if isinstance(value, decimal.Decimal):
        return float(value)
    if isinstance(value, (dt.datetime, dt.date)):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str) and DATETIME_TEXT_RE.match(value):
        text = value.replace("T", " ")
        text = text.rstrip("Z")
        text = re.sub(r"\.\d+", "", text)
        text = re.sub(r"([+-]\d{2}:?\d{2})$", "", text)
        return text[:19]
    return value


def pick(row: Dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return scalar(row[name])
    return default


def parse_jsonish(value: Any) -> Any:
    value = scalar(value)
    if value in (None, ""):
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text[0] in "[{":
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        return text
    return value


def first_text(value: Any) -> str:
    data = parse_jsonish(value)
    if data is None:
        return ""
    if isinstance(data, dict):
        for key in LOCALE_KEYS:
            text = first_text(data.get(key))
            if text:
                return text
        for item in data.values():
            text = first_text(item)
            if text:
                return text
        return ""
    if isinstance(data, list):
        texts = [first_text(item) for item in data]
        return " / ".join(text for text in texts if text)
    return str(data).strip()


def localized(row: Dict[str, Any], *names: str, default: str = "") -> str:
    for name in names:
        if name in row and row[name] not in (None, ""):
            text = first_text(row[name])
            if text:
                return text
    return default


def json_list(value: Any) -> List[Any]:
    data = parse_jsonish(value)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return list(data.values())
    if data not in (None, ""):
        return [data]
    return []


def first_image(row: Dict[str, Any], *names: str) -> str:
    for name in names:
        if name not in row or row[name] in (None, ""):
            continue
        for item in json_list(row[name]):
            if isinstance(item, dict):
                item = item.get("url") or item.get("src") or item.get("path") or item.get("image")
            text = first_text(item)
            if text:
                return text
    return ""


def tags_text(row: Dict[str, Any]) -> str:
    tags = [first_text(item) for item in json_list(pick(row, "tags", default=None))]
    return ", ".join(tag for tag in tags if tag)


def sku_display_name(row: Dict[str, Any], fallback_code: str) -> str:
    name = localized(row, "name_json", "title_json", "name", "sku_name", "title", default="")
    if name:
        return name
    spec = parse_jsonish(pick(row, "spec_values_json", "spec_values", "sku_snapshot_json", "sku_snapshot", default=None))
    if isinstance(spec, dict):
        values = []
        for value in spec.values():
            text = first_text(value)
            if text:
                values.append(text)
        if values:
            return " / ".join(values)
    if isinstance(spec, list):
        values = [first_text(item) for item in spec]
        values = [value for value in values if value]
        if values:
            return " / ".join(values)
    if fallback_code and fallback_code.upper() != "DEFAULT":
        return fallback_code
    return "默认规格"


def trim(value: Any, length: int, default: str = "") -> str:
    text = str(value if value is not None else default)
    return text[:length]


def money(value: Any, default: float = 0.0) -> float:
    if value in (None, ""):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def int_or_zero(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def enabled(value: Any) -> int:
    if value is None:
        return 1
    if isinstance(value, bool):
        return 1 if value else 0
    text = str(value).lower()
    return 0 if text in {"0", "false", "closed", "disabled", "inactive", "archived"} else 1


def map_order_status(status: Any, paid: bool = False) -> int:
    text = str(status or "").lower()
    if text in {"completed", "success", "succeeded", "paid", "fulfilled", "delivered"}:
        return OLD_STATUS_COMPLETED
    if text in {"expired", "timeout"}:
        return OLD_STATUS_EXPIRED
    if text in {"failed", "failure", "cancelled", "canceled", "refunded"}:
        return OLD_STATUS_FAILURE
    if paid:
        return OLD_STATUS_PENDING
    if text in {"processing", "pending_fulfillment"}:
        return OLD_STATUS_PENDING
    return OLD_STATUS_WAIT_PAY


def map_carmi_status(row: Dict[str, Any]) -> int:
    status = str(pick(row, "status", default="")).lower()
    if status in {"sold", "used", "delivered", "consumed"}:
        return OLD_CARMI_SOLD
    if pick(row, "order_id", "order_item_id", default=None):
        return OLD_CARMI_SOLD
    return OLD_CARMI_UNSOLD


def card_is_unused(row: Dict[str, Any]) -> bool:
    return map_carmi_status(row) == OLD_CARMI_UNSOLD


def safe_filename(value: str, default: str = "untitled") -> str:
    text = re.sub(r'[\\/:*?"<>|\r\n]+', "_", value).strip(" ._")
    return trim(text or default, 120)


def category_path(category_id: int, categories_by_id: Dict[int, Dict[str, Any]]) -> List[str]:
    if category_id not in categories_by_id:
        return ["未分类"]
    names: List[str] = []
    seen = set()
    current_id = category_id
    for _ in range(12):
        if not current_id or current_id in seen:
            break
        seen.add(current_id)
        category = categories_by_id.get(current_id)
        if not category:
            break
        names.append(localized(category, "name_json", "name", "title_json", "title", default=f"分类 {current_id}"))
        current_id = int_or_zero(pick(category, "parent_id", default=0))
    names.reverse()
    return [name for name in names if name] or ["未分类"]


def export_unused_cards(source: Dict[str, List[Dict[str, Any]]], target_dir: str) -> Dict[str, Any]:
    categories_by_id = {int_or_zero(pick(row, "id")): row for row in source["categories"]}
    products_by_id = {int_or_zero(pick(row, "id")): row for row in source["products"]}
    skus_by_id = {int_or_zero(pick(row, "id")): row for row in source["product_skus"]}

    grouped: Dict[Tuple[str, str, str, int, int], List[str]] = defaultdict(list)
    for card in source["card_secrets"]:
        if not card_is_unused(card):
            continue
        content = pick(card, "secret", "card", "carmi", "content", "value", default="")
        if not content:
            continue
        product_id = int_or_zero(pick(card, "product_id", "goods_id"))
        sku_id = int_or_zero(pick(card, "sku_id", "product_sku_id", default=0))
        product = products_by_id.get(product_id, {})
        sku = skus_by_id.get(sku_id, {})
        title = localized(product, "title_json", "title", "name_json", "name", default=f"商品 {product_id}")
        category_id = int_or_zero(pick(product, "category_id", "group_id", default=0))
        category = " / ".join(category_path(category_id, categories_by_id))
        sku_name = sku_display_name(sku, pick(sku, "sku_code", default="DEFAULT")) if sku else "默认规格"
        grouped[(category, title, sku_name, product_id, sku_id)].append(str(content))

    os.makedirs(target_dir, exist_ok=True)
    summary = []
    for (category, title, sku_name, product_id, sku_id), lines in sorted(grouped.items()):
        category_dir = os.path.join(target_dir, *[safe_filename(part) for part in category.split(" / ")])
        os.makedirs(category_dir, exist_ok=True)
        filename = f"{product_id}-{safe_filename(title)}"
        if sku_name and sku_name != "默认规格":
            filename += f"-{safe_filename(sku_name)}"
        path = os.path.join(category_dir, f"{filename}.txt")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(lines))
            fh.write("\n")
        summary.append(
            {
                "category": category,
                "product_id": product_id,
                "product": title,
                "sku_id": sku_id,
                "sku": sku_name,
                "count": len(lines),
                "file": path,
            }
        )

    csv_path = os.path.join(target_dir, "_summary.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["category", "product_id", "product", "sku_id", "sku", "count", "file"])
        writer.writeheader()
        writer.writerows(summary)

    json_path = os.path.join(target_dir, "_summary.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    return {"groups": len(summary), "cards": sum(row["count"] for row in summary), "dir": target_dir}


def table_exists_pg(conn, table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "select exists(select 1 from information_schema.tables where table_schema='public' and table_name=%s)",
            (table,),
        )
        return bool(cur.fetchone()[0])


def fetch_table_pg(conn, table: str) -> List[Dict[str, Any]]:
    if not table_exists_pg(conn, table):
        return []
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(f'SELECT * FROM "{table}" ORDER BY id')
        return [dict(row) for row in cur.fetchall()]


def group_by(rows: Iterable[Dict[str, Any]], *keys: str) -> Dict[Any, List[Dict[str, Any]]]:
    grouped: Dict[Any, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = pick(row, *keys, default=None)
        grouped[key].append(row)
    return grouped


def old_pay_map(mysql_conn) -> Tuple[Dict[str, int], Dict[str, int]]:
    by_check: Dict[str, int] = {}
    by_name: Dict[str, int] = {}
    with mysql_conn.cursor() as cur:
        cur.execute("SELECT id, pay_name, pay_check FROM pays")
        for row in cur.fetchall():
            by_check[str(row["pay_check"]).lower()] = int(row["id"])
            by_name[str(row["pay_name"]).lower()] = int(row["id"])
    return by_check, by_name


def mysql_column_exists(cur, table: str, column: str) -> bool:
    cur.execute(f"SHOW COLUMNS FROM `{table}` LIKE %s", (column,))
    return cur.fetchone() is not None


def mysql_index_exists(cur, table: str, index: str) -> bool:
    cur.execute(f"SHOW INDEX FROM `{table}` WHERE Key_name=%s", (index,))
    return cur.fetchone() is not None


def ensure_target_schema(cur) -> None:
    cur.execute("ALTER TABLE `orders` MODIFY `info` MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL")
    cur.execute("ALTER TABLE `carmis` MODIFY `carmi` MEDIUMTEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL")
    if not mysql_column_exists(cur, "goods_group", "parent_id"):
        cur.execute("ALTER TABLE `goods_group` ADD `parent_id` int NOT NULL DEFAULT 0 AFTER `id`")
    if not mysql_index_exists(cur, "goods_group", "idx_parent_id"):
        cur.execute("ALTER TABLE `goods_group` ADD INDEX `idx_parent_id` (`parent_id`)")


def guess_pay_id(payment: Optional[Dict[str, Any]], maps: Tuple[Dict[str, int], Dict[str, int]]) -> Tuple[Optional[int], str]:
    if not payment:
        return None, "no payment row"
    by_check, by_name = maps
    candidates = [
        pick(payment, "channel_type", "provider_type", "type", default=""),
        pick(payment, "channel_name", "provider_name", "gateway_name", default=""),
        pick(payment, "provider", "gateway", default=""),
    ]
    joined = " ".join(str(item).lower() for item in candidates if item)
    direct = [
        "alipay",
        "zfbf2f",
        "wxpay",
        "wechat",
        "vwx",
        "vpay",
        "epay",
        "yipay",
        "paypal",
        "stripe",
    ]
    for key in direct:
        if key in joined and key in by_check:
            return by_check[key], f"matched pay_check={key}"
    for check, pay_id in by_check.items():
        if check and check in joined:
            return pay_id, f"matched pay_check={check}"
    for name, pay_id in by_name.items():
        if name and name in joined:
            return pay_id, f"matched pay_name={name}"
    return None, f"unmatched: {joined or 'empty'}"


def upsert(cur, table: str, row: Dict[str, Any]) -> None:
    cols = list(row.keys())
    placeholders = ", ".join(["%s"] * len(cols))
    names = ", ".join(f"`{col}`" for col in cols)
    updates = ", ".join(f"`{col}`=VALUES(`{col}`)" for col in cols if col != "id")
    sql = f"INSERT INTO `{table}` ({names}) VALUES ({placeholders})"
    if updates:
        sql += f" ON DUPLICATE KEY UPDATE {updates}"
    cur.execute(sql, [row[col] for col in cols])


def latest(rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not rows:
        return None
    return sorted(rows, key=lambda row: str(pick(row, "created_at", "updated_at", default="")), reverse=True)[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Dujiao-Next PostgreSQL -> old dujiaoka MySQL migration helper")
    parser.add_argument("--pg-dsn", default=os.getenv("NEXT_PG_DSN"), help="PostgreSQL DSN for Dujiao-Next")
    parser.add_argument("--source-json", help="Read Dujiao-Next source rows from an exported JSON file")
    parser.add_argument("--export-json", help="Export Dujiao-Next source rows to JSON before applying")
    parser.add_argument("--mysql-host", default=os.getenv("OLD_MYSQL_HOST", "127.0.0.1"))
    parser.add_argument("--mysql-port", type=int, default=int(os.getenv("OLD_MYSQL_PORT", "3306")))
    parser.add_argument("--mysql-db", default=os.getenv("OLD_MYSQL_DB"))
    parser.add_argument("--mysql-user", default=os.getenv("OLD_MYSQL_USER", "root"))
    parser.add_argument("--mysql-password", default=os.getenv("OLD_MYSQL_PASSWORD", ""))
    parser.add_argument("--dry-run", action="store_true", help="Only print report. This is the default.")
    parser.add_argument("--apply", action="store_true", help="Write converted data into MySQL.")
    parser.add_argument("--truncate-target", action="store_true", help="Delete target goods/orders/carmis data before import.")
    parser.add_argument("--skip-unsold-cards", action="store_true", help="Do not import unused card inventory into old dujiaoka.")
    parser.add_argument("--export-unused-cards-dir", help="Export unused card secrets grouped by category/product/SKU.")
    args = parser.parse_args()

    pg = None
    if args.source_json:
        with open(args.source_json, "r", encoding="utf-8-sig") as fh:
            source = json.load(fh)
    else:
        if not args.pg_dsn:
            print("Please provide --pg-dsn, NEXT_PG_DSN, or --source-json.", file=sys.stderr)
            return 2
        if psycopg2 is None:
            print("Missing dependency: psycopg2-binary", file=sys.stderr)
            print("Install with: pip install psycopg2-binary", file=sys.stderr)
            return 2
        pg = psycopg2.connect(args.pg_dsn)
        source = {
            "categories": fetch_table_pg(pg, "categories"),
            "products": fetch_table_pg(pg, "products"),
            "product_skus": fetch_table_pg(pg, "product_skus"),
            "card_secrets": fetch_table_pg(pg, "card_secrets"),
            "orders": fetch_table_pg(pg, "orders"),
            "order_items": fetch_table_pg(pg, "order_items"),
            "payments": fetch_table_pg(pg, "payments"),
            "fulfillments": fetch_table_pg(pg, "fulfillments"),
            "payment_channels": fetch_table_pg(pg, "payment_channels"),
        }

    for name in [
        "categories",
        "products",
        "product_skus",
        "card_secrets",
        "orders",
        "order_items",
        "payments",
        "fulfillments",
        "payment_channels",
    ]:
        source.setdefault(name, [])

    unused_cards_report = None
    if args.export_unused_cards_dir:
        unused_cards_report = export_unused_cards(source, args.export_unused_cards_dir)

    if args.export_json:
        with open(args.export_json, "w", encoding="utf-8") as fh:
            json.dump(source, fh, ensure_ascii=False, indent=2, default=str)
        print(f"Exported source JSON: {args.export_json}")

    report = {
        "mode": "apply" if args.apply else "dry-run",
        "source_counts": {name: len(rows) for name, rows in source.items()},
        "generated_at": now(),
    }
    if unused_cards_report:
        report["unused_cards_export"] = unused_cards_report
    parent_ids = {int_or_zero(pick(order, "parent_id", default=0)) for order in source["orders"]}
    parent_ids.discard(0)
    if parent_ids:
        report["order_parent_child_mode"] = {
            "parent_orders": len(parent_ids),
            "target_sale_orders": len(source["orders"]) - len(parent_ids),
        }

    status_counts: Dict[str, int] = defaultdict(int)
    for order in source["orders"]:
        status_counts[str(pick(order, "status", default="unknown"))] += 1
    report["order_status_counts"] = dict(status_counts)

    channels = []
    for channel in source["payment_channels"]:
        channels.append(
            {
                "id": pick(channel, "id"),
                "name": pick(channel, "name", "channel_name"),
                "type": pick(channel, "type", "channel_type", "provider_type"),
            }
        )
    report["payment_channels"] = channels

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if not args.apply:
        if pg is not None:
            pg.close()
        print("\nDry-run finished. Add --apply to write into MySQL.")
        return 0

    if not args.mysql_db:
        print("Please provide --mysql-db or OLD_MYSQL_DB when using --apply.", file=sys.stderr)
        if pg is not None:
            pg.close()
        return 2
    if pymysql is None:
        print("Missing dependency: pymysql", file=sys.stderr)
        print("Install with: pip install pymysql", file=sys.stderr)
        if pg is not None:
            pg.close()
        return 2

    mysql_conn = pymysql.connect(
        host=args.mysql_host,
        port=args.mysql_port,
        user=args.mysql_user,
        password=args.mysql_password,
        database=args.mysql_db,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )

    order_items_by_order = group_by(source["order_items"], "order_id")
    payments_by_order = group_by(source["payments"], "order_id")
    fulfillments_by_order = group_by(source["fulfillments"], "order_id")
    fulfillments_by_item = group_by(source["fulfillments"], "order_item_id")
    cards_by_order = group_by(source["card_secrets"], "order_id")
    skus_by_product = group_by(source["product_skus"], "product_id", "goods_id")
    products_by_id = {int_or_zero(pick(product, "id")): product for product in source["products"]}
    orders_by_id = {int_or_zero(pick(order, "id")): order for order in source["orders"]}
    children_by_parent = group_by(
        [order for order in source["orders"] if int_or_zero(pick(order, "parent_id", default=0))],
        "parent_id",
    )
    sale_orders = [
        order
        for order in source["orders"]
        if not children_by_parent.get(int_or_zero(pick(order, "id")))
    ]
    source_order_count = len(source["orders"])
    if source_order_count != len(sale_orders):
        print(f"Parent/child orders detected: importing {len(sale_orders)} sale orders from {source_order_count} source orders.")

    sku_id_map: Dict[Tuple[str, int], int] = {}
    pay_maps = old_pay_map(mysql_conn)
    unmatched_payments: List[Dict[str, Any]] = []

    try:
        with mysql_conn.cursor() as cur:
            ensure_target_schema(cur)
            if args.truncate_target:
                for table in ["orders", "carmis", "goods_skus", "goods", "goods_group"]:
                    cur.execute(f"DELETE FROM `{table}`")

            for category in source["categories"]:
                category_id = int_or_zero(pick(category, "id"))
                upsert(
                    cur,
                    "goods_group",
                    {
                        "id": category_id,
                        "parent_id": int_or_zero(pick(category, "parent_id", default=0)),
                        "gp_name": trim(localized(category, "name_json", "name", "title_json", "title", default=f"分类 {category_id}"), 200),
                        "is_open": enabled(pick(category, "is_active", "is_enabled", "enabled", "status", default=1)),
                        "ord": int_or_zero(pick(category, "sort_order", "sort", "ord", "priority", default=1)),
                        "created_at": pick(category, "created_at", default=now()),
                        "updated_at": pick(category, "updated_at", default=now()),
                        "deleted_at": None,
                    },
                )

            if source["products"] and not source["categories"]:
                upsert(
                    cur,
                    "goods_group",
                    {
                        "id": 1,
                        "parent_id": 0,
                        "gp_name": "默认分类",
                        "is_open": 1,
                        "ord": 1,
                        "created_at": now(),
                        "updated_at": now(),
                        "deleted_at": None,
                    },
                )

            for product in source["products"]:
                product_id = int_or_zero(pick(product, "id"))
                product_skus = skus_by_product.get(product_id, [])
                sku_prices = [money(pick(sku, "price_amount", "price", "actual_price", "sale_price", default=None)) for sku in product_skus]
                sku_prices = [price for price in sku_prices if price > 0]
                product_price = money(
                    pick(product, "price_amount", "price", "actual_price", "sale_price", default=None),
                    min(sku_prices) if sku_prices else 0.0,
                )
                product_image = first_image(product, "images", "image", "picture", "cover")
                product_title = localized(product, "title_json", "title", "name_json", "name", default=f"商品 {product_id}")
                product_description = localized(product, "description_json", "description", "subtitle", "short_description", default="")
                product_content = localized(product, "content_json", "content", "description_json", "description", default=product_description)
                upsert(
                    cur,
                    "goods",
                    {
                        "id": product_id,
                        "group_id": int_or_zero(pick(product, "category_id", "group_id", default=1)) or 1,
                        "gd_name": trim(product_title, 200),
                        "gd_description": trim(product_description, 200),
                        "gd_keywords": trim(tags_text(product) or pick(product, "keywords", default=""), 200),
                        "picture": product_image,
                        "retail_price": money(pick(product, "retail_price", "original_price", default=0)),
                        "actual_price": product_price,
                        "in_stock": int_or_zero(pick(product, "manual_stock_total", "stock", "in_stock", default=0)),
                        "sales_volume": int_or_zero(pick(product, "sales_volume", "sold_count", default=0)),
                        "ord": int_or_zero(pick(product, "sort_order", "sort", "ord", "priority", default=1)),
                        "buy_limit_num": int_or_zero(pick(product, "max_purchase_quantity", "buy_limit", "buy_limit_num", default=0)),
                        "buy_prompt": localized(product, "instructions_json", "buy_prompt", "purchase_notice", default=""),
                        "description": product_content,
                        "type": OLD_AUTO_DELIVERY,
                        "wholesale_price_cnf": None,
                        "other_ipu_cnf": None,
                        "api_hook": None,
                        "is_open": enabled(pick(product, "is_active", "is_enabled", "enabled", "status", default=1)),
                        "created_at": pick(product, "created_at", default=now()),
                        "updated_at": pick(product, "updated_at", default=now()),
                        "deleted_at": None,
                    },
                )

                default_sku = {
                    "goods_id": product_id,
                    "sku_name": "默认规格",
                    "sku_code": "DEFAULT",
                    "actual_price": product_price,
                    "picture": product_image,
                    "in_stock": int_or_zero(pick(product, "manual_stock_total", "stock", "in_stock", default=0)),
                    "ord": 1,
                    "is_open": 1,
                    "created_at": pick(product, "created_at", default=now()),
                    "updated_at": pick(product, "updated_at", default=now()),
                    "deleted_at": None,
                }
                cur.execute(
                    """
                    INSERT INTO goods_skus
                    (goods_id, sku_name, sku_code, actual_price, picture, in_stock, ord, is_open, created_at, updated_at, deleted_at)
                    VALUES (%(goods_id)s, %(sku_name)s, %(sku_code)s, %(actual_price)s, %(picture)s, %(in_stock)s, %(ord)s, %(is_open)s, %(created_at)s, %(updated_at)s, %(deleted_at)s)
                    ON DUPLICATE KEY UPDATE
                    sku_name=VALUES(sku_name), actual_price=VALUES(actual_price), picture=VALUES(picture),
                    in_stock=VALUES(in_stock), ord=VALUES(ord), is_open=VALUES(is_open), updated_at=VALUES(updated_at)
                    """,
                    default_sku,
                )
                cur.execute("SELECT id FROM goods_skus WHERE goods_id=%s AND sku_code='DEFAULT'", (product_id,))
                sku_id_map[("default", product_id)] = int(cur.fetchone()["id"])

                for sku in product_skus:
                    source_sku_id = int_or_zero(pick(sku, "id"))
                    sku_code = trim(pick(sku, "code", "sku_code", default=f"SKU-{source_sku_id}"), 64) or f"SKU-{source_sku_id}"
                    if sku_code.upper() == "DEFAULT":
                        sku_id_map[("sku", source_sku_id)] = sku_id_map[("default", product_id)]
                        continue
                    sku_image = first_image(sku, "images", "image", "picture", "cover") or product_image
                    row = {
                        "goods_id": product_id,
                        "sku_name": trim(sku_display_name(sku, sku_code), 150),
                        "sku_code": sku_code,
                        "actual_price": money(pick(sku, "price_amount", "price", "actual_price", "sale_price", default=product_price)),
                        "picture": sku_image,
                        "in_stock": int_or_zero(pick(sku, "manual_stock_total", "stock", "in_stock", default=0)),
                        "ord": int_or_zero(pick(sku, "sort_order", "sort", "ord", "priority", default=1)),
                        "is_open": enabled(pick(sku, "is_active", "is_enabled", "enabled", "status", default=1)),
                        "created_at": pick(sku, "created_at", default=now()),
                        "updated_at": pick(sku, "updated_at", default=now()),
                        "deleted_at": None,
                    }
                    upsert(cur, "goods_skus", row)
                    cur.execute("SELECT id FROM goods_skus WHERE goods_id=%s AND sku_code=%s", (product_id, sku_code))
                    sku_id_map[("sku", source_sku_id)] = int(cur.fetchone()["id"])

            for card in source["card_secrets"]:
                if args.skip_unsold_cards and card_is_unused(card):
                    continue
                product_id = int_or_zero(pick(card, "product_id", "goods_id"))
                source_sku_id = int_or_zero(pick(card, "product_sku_id", "sku_id"))
                sku_id = sku_id_map.get(("sku", source_sku_id)) or sku_id_map.get(("default", product_id))
                content = pick(card, "secret", "card", "carmi", "content", "value", default="")
                upsert(
                    cur,
                    "carmis",
                    {
                        "id": int_or_zero(pick(card, "id")),
                        "goods_id": product_id,
                        "sku_id": sku_id,
                        "status": map_carmi_status(card),
                        "is_loop": 0,
                        "carmi": content,
                        "created_at": pick(card, "created_at", default=now()),
                        "updated_at": pick(card, "updated_at", default=now()),
                        "deleted_at": None,
                    },
                )

            for order in sale_orders:
                order_id = int_or_zero(pick(order, "id"))
                parent_id = int_or_zero(pick(order, "parent_id", default=0))
                parent = orders_by_id.get(parent_id, {}) if parent_id else {}
                item_rows = order_items_by_order.get(order_id) or order_items_by_order.get(parent_id) or [{}]
                item = item_rows[0]
                product_id = int_or_zero(pick(item, "product_id", "goods_id", default=pick(order, "product_id", "goods_id", default=0)))
                source_sku_id = int_or_zero(pick(item, "product_sku_id", "sku_id"))
                sku_id = sku_id_map.get(("sku", source_sku_id)) or sku_id_map.get(("default", product_id))
                payment = latest(payments_by_order.get(order_id, []) or payments_by_order.get(parent_id, []))
                pay_id, pay_note = guess_pay_id(payment, pay_maps)
                if payment and not pay_id:
                    unmatched_payments.append({"order_id": order_id, "note": pay_note, "payment": payment})
                fulfillment_rows = (
                    fulfillments_by_order.get(order_id, [])
                    + fulfillments_by_order.get(parent_id, [])
                    + fulfillments_by_item.get(pick(item, "id", default=None), [])
                )
                info_lines = []
                seen_fulfillment_ids = set()
                for fulfillment in fulfillment_rows:
                    fulfillment_id = pick(fulfillment, "id", default=None)
                    if fulfillment_id in seen_fulfillment_ids:
                        continue
                    seen_fulfillment_ids.add(fulfillment_id)
                    value = pick(fulfillment, "payload", "content", "secret", "card_secret", "delivered_content", default="")
                    if not value:
                        value = first_text(pick(fulfillment, "logistics_json", "delivery_data", default=""))
                    if value:
                        info_lines.append(str(value))
                seen_info = set(info_lines)
                for sold_card in cards_by_order.get(order_id, []) + cards_by_order.get(parent_id, []):
                    if card_is_unused(sold_card):
                        continue
                    value = pick(sold_card, "secret", "card", "carmi", "content", "value", default="")
                    if value and str(value) not in seen_info:
                        info_lines.append(str(value))
                        seen_info.add(str(value))
                paid = bool(payment and str(pick(payment, "status", default="")).lower() in {"paid", "success", "succeeded", "completed"})
                paid = paid or bool(pick(order, "paid_at", default=pick(parent, "paid_at", default=None)))
                siblings = children_by_parent.get(parent_id, []) if parent_id else []
                order_no_source = parent if parent and len(siblings) == 1 else order
                order_sn = trim(pick(order_no_source, "order_no", "order_sn", "no", default=f"NEXT{order_id}"), 150)
                quantity = int_or_zero(pick(item, "quantity", "buy_amount", default=1)) or 1
                goods_price = money(pick(item, "unit_price", "unit_price_amount", "price", "actual_price", default=pick(order, "total_amount", "total_price", default=0)))
                item_total = money(pick(item, "total_price", "total_amount", default=goods_price * quantity), goods_price * quantity)
                actual = money(
                    pick(
                        payment or {},
                        "amount",
                        "fee_amount",
                        default=pick(order, "online_paid_amount", "paid_amount", "total_amount", "total_price", default=pick(parent, "online_paid_amount", "total_amount", default=item_total)),
                    )
                )
                product = products_by_id.get(product_id, {})
                title = localized(item, "title_json", "title", "product_name", default="")
                if not title:
                    title = localized(product, "title_json", "title", "name_json", "name", default=order_sn)
                upsert(
                    cur,
                    "orders",
                    {
                        "id": order_id,
                        "order_sn": order_sn,
                        "goods_id": product_id,
                        "sku_id": sku_id,
                        "coupon_id": 0,
                        "title": trim(title, 200),
                        "type": OLD_AUTO_DELIVERY,
                        "goods_price": goods_price,
                        "buy_amount": quantity,
                        "coupon_discount_price": 0,
                        "wholesale_discount_price": 0,
                        "total_price": item_total,
                        "actual_price": actual,
                        "search_pwd": trim(pick(order, "guest_password", default=pick(parent, "guest_password", default="")), 200),
                        "email": trim(pick(order, "guest_email", "email", "user_email", default=pick(parent, "guest_email", "email", "user_email", default="")), 200),
                        "info": "\n".join(info_lines),
                        "pay_id": pay_id,
                        "buy_ip": trim(pick(order, "client_ip", "buy_ip", "ip", default=pick(parent, "client_ip", "buy_ip", "ip", default="127.0.0.1")), 50),
                        "trade_no": trim(pick(payment or {}, "trade_no", "gateway_order_no", "provider_ref", default=""), 200),
                        "status": map_order_status(pick(order, "status", default=pick(parent, "status", default=None)), bool(paid)),
                        "coupon_ret_back": 0,
                        "created_at": pick(order, "created_at", default=now()),
                        "updated_at": pick(order, "updated_at", default=now()),
                        "deleted_at": None,
                    },
                )

            mysql_conn.commit()
    except Exception:
        mysql_conn.rollback()
        raise
    finally:
        mysql_conn.close()
        if pg is not None:
            pg.close()

    print("\nApply finished.")
    if unmatched_payments:
        print("\nUnmatched payment rows. Please map these manually:")
        print(json.dumps(unmatched_payments[:50], ensure_ascii=False, indent=2, default=str))
        if len(unmatched_payments) > 50:
            print(f"... and {len(unmatched_payments) - 50} more.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
