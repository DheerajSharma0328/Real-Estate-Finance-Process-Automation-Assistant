
import os

from neo4j import GraphDatabase
from dotenv import load_dotenv


load_dotenv()


def get_neo4j_driver():
    """Create a Neo4j driver using the project's environment settings."""

    required_settings = [
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD",
    ]

    missing_settings = [
        setting
        for setting in required_settings
        if not os.getenv(setting)
    ]

    if missing_settings:
        raise RuntimeError(
            "Missing Neo4j settings: " + ", ".join(missing_settings)
        )

    return GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(
            os.environ["NEO4J_USERNAME"],
            os.environ["NEO4J_PASSWORD"],
        ),
    )


def get_invoice_relationship_path(invoice_id: str):
    """Return the Property → Invoice → PurchaseOrder → Vendor path."""

    database = os.getenv("NEO4J_DATABASE", "neo4j")

    query = """
    MATCH path =
        (p:Property)-[:HAS_INVOICE]->
        (i:Invoice {invoice_id: $invoice_id})-[:REFERENCES_PO]->
        (po:PurchaseOrder)-[:ISSUED_TO]->
        (v:Vendor)
    RETURN
        p.property_id AS property_id,
        p.property_name AS property_name,
        i.invoice_id AS invoice_id,
        i.project_id AS project_id,
        i.invoice_amount AS invoice_amount,
        i.status AS invoice_status,
        po.po_id AS po_id,
        po.po_total AS po_total,
        v.vendor_id AS vendor_id,
        v.vendor_name AS vendor_name,
        [
            'Property',
            'Invoice',
            'PurchaseOrder',
            'Vendor'
        ] AS relationship_path
    """

    with get_neo4j_driver() as driver:
        with driver.session(database=database) as session:
            record = session.run(
                query,
                invoice_id=invoice_id,
            ).single()

    if record is None:
        return None

    return dict(record)
