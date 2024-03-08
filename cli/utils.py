def validate_price(price: str):
    try:
        float(price)
        return True
    except:
        return False