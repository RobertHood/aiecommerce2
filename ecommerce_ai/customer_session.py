def current_customer(request):
    return request.session.get("customer")


def set_current_customer(request, customer):
    request.session["customer"] = {
        "id": customer.id,
        "email": customer.email,
        "full_name": customer.full_name,
    }
    request.session.modified = True


def clear_current_customer(request):
    request.session.pop("customer", None)
    request.session.modified = True


def auth_context(request):
    return {"customer": current_customer(request)}
