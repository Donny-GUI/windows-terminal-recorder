def reduce_by_percent(items:list[int]|tuple[int], percent:int=20) -> None:
    """
    Reduces the width and height of the given tuple of integers.

    Parameters
    ----------
    size : Tuple[int, int]
        The tuple of integers to reduce.

    Returns
    -------
    None
    """
    factor = (100 - percent) / 100
    return [int(value * factor) for value in items]



