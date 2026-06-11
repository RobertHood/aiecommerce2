import json

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import InventoryItem, StockMovement, Warehouse


def parse_json(request):
    try:
        return json.loads(request.body or "{}"), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON format"}, status=400)


def warehouse_payload(warehouse):
    return {
        "id": warehouse.id,
        "code": warehouse.code,
        "name": warehouse.name,
        "address": warehouse.address,
        "city": warehouse.city,
        "is_active": warehouse.is_active,
    }


def inventory_payload(item):
    return {
        "id": item.id,
        "warehouse": warehouse_payload(item.warehouse),
        "product_id": item.product_id,
        "sku": item.sku,
        "product_name": item.product_name,
        "quantity_available": item.quantity_available,
        "quantity_reserved": item.quantity_reserved,
        "quantity_total": item.quantity_total,
        "reorder_level": item.reorder_level,
        "needs_reorder": item.needs_reorder,
        "updated_at": item.updated_at.isoformat(),
    }


def movement_payload(movement):
    return {
        "id": movement.id,
        "inventory_item_id": movement.inventory_item_id,
        "sku": movement.inventory_item.sku,
        "movement_type": movement.movement_type,
        "quantity": movement.quantity,
        "reference": movement.reference,
        "note": movement.note,
        "created_at": movement.created_at.isoformat(),
    }


def health(request):
    return JsonResponse({"service": "products", "status": "ok"})


@csrf_exempt
def warehouse_list_create(request):
    if request.method == "GET":
        warehouses = Warehouse.objects.all()
        return JsonResponse({"results": [warehouse_payload(warehouse) for warehouse in warehouses]})
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    code = str(data.get("code", "")).strip().lower()
    name = str(data.get("name", "")).strip()
    if not code or not name:
        return JsonResponse({"error": "code and name are required"}, status=400)

    warehouse, created = Warehouse.objects.get_or_create(
        code=code,
        defaults={
            "name": name,
            "address": str(data.get("address", "")).strip(),
            "city": str(data.get("city", "")).strip(),
        },
    )
    return JsonResponse(warehouse_payload(warehouse), status=201 if created else 200)


@csrf_exempt
def inventory_list_create(request):
    if request.method == "GET":
        items = InventoryItem.objects.select_related("warehouse").all()
        return JsonResponse({"results": [inventory_payload(item) for item in items]})
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    try:
        warehouse = Warehouse.objects.get(id=int(data["warehouse_id"]))
        quantity = int(data.get("quantity_available", 0))
        item = InventoryItem.objects.create(
            warehouse=warehouse,
            product_id=int(data["product_id"]),
            sku=str(data["sku"]).strip(),
            product_name=str(data["product_name"]).strip(),
            quantity_available=max(quantity, 0),
            reorder_level=max(int(data.get("reorder_level", 5)), 0),
        )
        StockMovement.objects.create(
            inventory_item=item,
            movement_type=StockMovement.TYPE_INBOUND,
            quantity=item.quantity_available,
            reference=data.get("reference", "initial-stock"),
        )
        return JsonResponse(inventory_payload(item), status=201)
    except (KeyError, ValueError, Warehouse.DoesNotExist):
        return JsonResponse({"error": "Invalid inventory payload"}, status=400)


def inventory_detail(request, item_id):
    item = InventoryItem.objects.select_related("warehouse").filter(id=item_id).first()
    if not item:
        return JsonResponse({"error": "Inventory item not found"}, status=404)
    return JsonResponse(inventory_payload(item))


@csrf_exempt
def inventory_adjust(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    try:
        delta = int(data["quantity_delta"])
    except (KeyError, ValueError):
        return JsonResponse({"error": "quantity_delta is required"}, status=400)

    with transaction.atomic():
        item = InventoryItem.objects.select_for_update().select_related("warehouse").filter(id=item_id).first()
        if not item:
            return JsonResponse({"error": "Inventory item not found"}, status=404)
        next_quantity = item.quantity_available + delta
        if next_quantity < 0:
            return JsonResponse({"error": "quantity_available cannot be negative"}, status=409)
        item.quantity_available = next_quantity
        item.save(update_fields=["quantity_available", "updated_at"])
        StockMovement.objects.create(
            inventory_item=item,
            movement_type=StockMovement.TYPE_ADJUSTMENT,
            quantity=delta,
            reference=data.get("reference", ""),
            note=data.get("note", ""),
        )

    return JsonResponse(inventory_payload(item))


@csrf_exempt
def inventory_reserve(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    try:
        quantity = int(data["quantity"])
        if quantity <= 0:
            raise ValueError
    except (KeyError, ValueError):
        return JsonResponse({"error": "positive quantity is required"}, status=400)

    with transaction.atomic():
        item = InventoryItem.objects.select_for_update().select_related("warehouse").filter(id=item_id).first()
        if not item:
            return JsonResponse({"error": "Inventory item not found"}, status=404)
        if item.quantity_available < quantity:
            return JsonResponse({"error": "not enough available inventory"}, status=409)
        item.quantity_available -= quantity
        item.quantity_reserved += quantity
        item.save(update_fields=["quantity_available", "quantity_reserved", "updated_at"])
        StockMovement.objects.create(
            inventory_item=item,
            movement_type=StockMovement.TYPE_RESERVE,
            quantity=quantity,
            reference=data.get("reference", ""),
            note=data.get("note", ""),
        )

    return JsonResponse(inventory_payload(item))


@csrf_exempt
def inventory_release(request, item_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    data, error = parse_json(request)
    if error:
        return error

    try:
        quantity = int(data["quantity"])
        if quantity <= 0:
            raise ValueError
    except (KeyError, ValueError):
        return JsonResponse({"error": "positive quantity is required"}, status=400)

    with transaction.atomic():
        item = InventoryItem.objects.select_for_update().select_related("warehouse").filter(id=item_id).first()
        if not item:
            return JsonResponse({"error": "Inventory item not found"}, status=404)
        if item.quantity_reserved < quantity:
            return JsonResponse({"error": "not enough reserved inventory"}, status=409)
        item.quantity_reserved -= quantity
        item.quantity_available += quantity
        item.save(update_fields=["quantity_available", "quantity_reserved", "updated_at"])
        StockMovement.objects.create(
            inventory_item=item,
            movement_type=StockMovement.TYPE_RELEASE,
            quantity=quantity,
            reference=data.get("reference", ""),
            note=data.get("note", ""),
        )

    return JsonResponse(inventory_payload(item))


def stock_movement_list(request):
    movements = StockMovement.objects.select_related("inventory_item", "inventory_item__warehouse").all()[:100]
    return JsonResponse({"results": [movement_payload(movement) for movement in movements]})
