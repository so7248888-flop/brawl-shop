async def fulfill_order(order: dict) -> bool:
    """Пока вручную. Админ будет дарить пасс по Supercell ID."""
    print(f"Нужно выполнить заказ {order['id']} для {order['supercell_id']}")
    return False  # False = ручная обработка
