from agents import function_tool


@function_tool
def Multiply(n1:int, n2:int):
    """Multilpication function."""
    print("Multiply tool fire......>")
    return n1 * n2