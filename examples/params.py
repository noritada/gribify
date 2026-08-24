from gribify import param_set


def main():
    product_param = param_set.ProductParam(category=10, num=1)
    print(f"{product_param}")


if __name__ == "__main__":
    main()
