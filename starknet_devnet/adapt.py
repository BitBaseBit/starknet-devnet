from starknet_devnet.util import StarknetDevnetException

def adapt_calldata(calldata, expected_inputs, types):
    """
    Simulatenously iterates over `calldata` and `expected_inputs`.

    The `calldata` is converted to types specified by `expected_inputs`.

    `types` is a dict that maps a type's name to its specification.

    Returns a list representing adapted `calldata`.
    """

    last_name = None
    last_value = None
    calldata_i = 0
    adapted_calldata = []
    for input_entry in expected_inputs:
        input_name = input_entry["name"]
        input_type = input_entry["type"]
        if calldata_i >= len(calldata):
            if input_type == "felt*" and last_name == f"{input_name}_len" and last_value == 0:
                # This means that an empty array is provided.
                # Last element was array length (0), it's replaced with the array itself
                adapted_calldata[-1] = []
                continue
            else:
                message = f"Too few function arguments provided: {len(calldata)}."
                raise StarknetDevnetException(message=message)
        input_value = calldata[calldata_i]

        if input_type == "felt*":
            if last_name != f"{input_name}_len":
                raise StarknetDevnetException(f"Array size argument {last_name} must appear right before {input_name}.")

            arr_length = int(last_value)
            arr = calldata[calldata_i : calldata_i + arr_length]
            if len(arr) < arr_length:
                message = f"Too few function arguments provided: {len(calldata)}."
                raise StarknetDevnetException(message=message)

            # last element was array length, it's replaced with the array itself
            adapted_calldata[-1] = arr
            calldata_i += arr_length

        elif input_type == "felt":
            adapted_calldata.append(input_value)
            calldata_i += 1

        else: # struct
            generated_complex, calldata_i = generate_complex(calldata, calldata_i, input_type, types)
            adapted_calldata.append(generated_complex)

        last_name = input_name
        last_value = input_value

    return adapted_calldata

def adapt_output(received):
    """
    Adapts the `received` object to format expected by client (list of hex strings).
    If `received` is an instance of `list`, it is understood that it corresponds to a felt*, so first its length is appended.
    If `received` is iterable, it is either a struct, a tuple or a felt*.
    Otherwise it is a `felt`.
    `ret` is recursively populated (and should probably be empty on first call).

    Example:
    >>> adapt_output((1, [5, 10]))
    ['0x1', '0x2', '0x5', '0xa']
    """

    ret = []
    adapt_output_rec(received, ret)
    return ret

def adapt_output_rec(received, ret):
    """
    Recursion called by adapt_output.
    """

    if isinstance(received, list):
        ret.append(hex(len(received)))
    try:
        for el in received:
            adapt_output_rec(el, ret)
    except TypeError:
        ret.append(hex(received))

def generate_complex(calldata, calldata_i: int, input_type: str, types):
    """
    Converts members of `calldata` to a more complex type specified by `input_type`:
    - puts members of a struct into a tuple
    - puts members of a tuple into a tuple

    The `calldata_i` is incremented according to how many `calldata` members were consumed.
    `types` is a dict that maps a type's name to its specification.

    Returns the `calldata` converted to the type specified by `input_type` (tuple if struct or tuple, number). Also returns the incremented `calldata_i`.
    """

    if input_type == "felt":
        return calldata[calldata_i], calldata_i + 1

    arr = []
    if input_type[0] == "(" and input_type[-1] == ")":
        members = input_type[1:-1].split(", ")
    else:
        if input_type not in types:
            raise ValueError(f"Unsupported type: {input_type}")
        struct = types[input_type]
        members = [entry["type"] for entry in struct["members"]]

    for member in members:
        generated_complex, calldata_i = generate_complex(calldata, calldata_i, member, types)
        arr.append(generated_complex)

    return tuple(arr), calldata_i
