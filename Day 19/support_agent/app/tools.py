import fakeredis
import uuid

from app.db import db
from app.vector_store import recall
from app.approval import approval_gate

r = fakeredis.FakeStrictRedis()

STREAM = "emails"
ESC_STREAM = "escalations"
GROUP = "support"


try:
    r.xgroup_create(
        STREAM,
        GROUP,
        id="0",
        mkstream=True
    )
except Exception:
    pass


try:
    r.xgroup_create(
        ESC_STREAM,
        GROUP,
        id="0",
        mkstream=True
    )
except Exception:
    pass

def enqueue_email(
    to,
    subject,
    body
):

    job_id = uuid.uuid4().hex[:8]

    r.xadd(
        STREAM,
        {
            "job_id": job_id,
            "to": to,
            "subject": subject,
            "body": body
        }
    )

    r.set(
        f"job:{job_id}",
        "queued"
    )

    return job_id

def check_inventory(
    sku: str
):

    row = db.execute(
        """
        SELECT
            sku,
            name,
            qty,
            price
        FROM inventory
        WHERE sku=?
        LIMIT 1
        """,
        (sku,)
    ).fetchone()

    if not row:
        return {
            "error": f"unknown sku {sku}"
        }

    return {
        "sku": row[0],
        "name": row[1],
        "qty": row[2],
        "price": row[3]
    }

def create_order(
    sku: str,
    qty: int
):

    row = db.execute(
        """
        SELECT qty, price
        FROM inventory
        WHERE sku=?
        LIMIT 1
        """,
        (sku,)
    ).fetchone()

    if not row:
        return {
            "error": "unknown sku"
        }

    stock, price = row

    if qty <= 0:
        return {
            "error": "qty must be positive"
        }

    if stock < qty:
        return {
            "error":
            f"insufficient stock: {stock}"
        }

    db.execute(
        """
        UPDATE inventory
        SET qty=qty-?
        WHERE sku=?
        """,
        (qty, sku)
    )

    cur = db.execute(
        """
        INSERT INTO orders
        (
            sku,
            qty,
            total,
            status
        )
        VALUES (?,?,?,?)
        """,
        (
            sku,
            qty,
            round(price * qty, 2),
            "created"
        )
    )

    db.commit()

    return {
        "order_id": cur.lastrowid,
        "sku": sku,
        "qty": qty,
        "total": round(
            price * qty,
            2
        )
    }

def send_confirmation(
    to,
    order_id
):

    job_id = enqueue_email(
        to,
        f"Order {order_id}",
        f"Order {order_id} confirmed"
    )

    return {
        "job_id": job_id,
        "status": "queued"
    }

def check_job(
    job_id
):

    value = r.get(
        f"job:{job_id}"
    )

    if not value:
        return {
            "status": "unknown"
        }

    return {
        "job_id": job_id,
        "status": value.decode()
    }

def search_kb(
    question
):

    hits = recall(
        question,
        k=3
    )

    return {
        "results": [
            h["text"]
            for h in hits
        ]
    }

def create_ticket(
    customer,
    issue
):

    cur = db.execute(
        """
        INSERT INTO tickets
        (
            customer,
            issue,
            status
        )
        VALUES (?,?,?)
        """,
        (
            customer,
            issue,
            "open"
        )
    )

    db.commit()

    return {
        "ticket_id": cur.lastrowid,
        "status": "open"
    }

def get_ticket(
    ticket_id
):

    row = db.execute(
        """
        SELECT
            id,
            customer,
            issue,
            status
        FROM tickets
        WHERE id=?
        LIMIT 1
        """,
        (ticket_id,)
    ).fetchone()

    if not row:
        return {
            "error":
            "ticket not found"
        }

    return {
        "ticket_id": row[0],
        "customer": row[1],
        "issue": row[2],
        "status": row[3]
    }

def escalate_ticket(
    ticket_id,
    reason
):

    gate = approval_gate(
        "escalate_ticket",
        {
            "ticket_id": ticket_id,
            "reason": reason
        }
    )

    if gate:
        return gate

    job_id = uuid.uuid4().hex[:8]

    r.xadd(
        ESC_STREAM,
        {
            "job_id": job_id,
            "ticket_id": ticket_id,
            "reason": reason
        }
    )

    r.set(
        f"esc:{job_id}",
        "queued"
    )

    return {
        "job_id": job_id,
        "status": "queued"
    }

def run_worker(
    max_msgs=10
):

    processed = 0

    email_msgs = r.xreadgroup(
        GROUP,
        "worker-1",
        {STREAM: ">"},
        count=max_msgs
    )

    for _, msgs in email_msgs or []:

        for msg_id, fields in msgs:

            payload = {
                k.decode():
                v.decode()
                for k, v in fields.items()
            }

            r.set(
                f"job:{payload['job_id']}",
                "sent"
            )

            r.xack(
                STREAM,
                GROUP,
                msg_id
            )

            processed += 1

    esc_msgs = r.xreadgroup(
        GROUP,
        "worker-1",
        {ESC_STREAM: ">"},
        count=max_msgs
    )

    for _, msgs in esc_msgs or []:

        for msg_id, fields in msgs:

            payload = {
                k.decode():
                v.decode()
                for k, v in fields.items()
            }

            r.set(
                f"esc:{payload['job_id']}",
                "assigned"
            )

            r.xack(
                ESC_STREAM,
                GROUP,
                msg_id
            )

            processed += 1

    return processed

TOOLS = {
    "check_inventory":
        check_inventory,

    "create_order":
        create_order,

    "send_confirmation":
        send_confirmation,

    "check_job":
        check_job,

    "search_kb":
        search_kb,

    "create_ticket":
        create_ticket,

    "get_ticket":
        get_ticket,

    "escalate_ticket":
        escalate_ticket
}

def run_tool(
    tool_name,
    args
):

    fn = TOOLS.get(
        tool_name
    )

    if not fn:

        return (
            {
                "error":
                f"unknown tool {tool_name}"
            },
            True
        )

    try:

        result = fn(
            **args
        )

        return (
            result,
            isinstance(result, dict)
            and "error" in result
        )

    except Exception as e:

        return (
            {
                "error": repr(e)
            },
            True
        )