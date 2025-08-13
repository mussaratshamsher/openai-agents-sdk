from agents import function_tool


@function_tool
def Add(n1:int, n2:int):
    """Addition function."""
    print("plus tool fire....")
    return n1 + n2