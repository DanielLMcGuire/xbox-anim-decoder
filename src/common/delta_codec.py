def decompress_delta_stream(raw_ints, ncount, escape_byte,
                             first_can_escape=False, on_missing='truncate'):
    b = raw_ints
    n = len(b)
    out = [0] * ncount
    if n == 0:
        return out if on_missing == 'hold' else out[:0]

    if first_can_escape and b[0] == escape_byte:
        val = _read_escaped_i16(b, 1)
        out[0] = val
        pbytes_offset = 2
    else:
        out[0] = b[0]
        pbytes_offset = 0

    actual_count = 1
    for i in range(1, ncount):
        idx = pbytes_offset + i
        if idx >= n:
            if on_missing == 'hold':
                out[i] = out[i - 1]
                actual_count = i + 1
                continue
            break
        if b[idx] == escape_byte:
            if idx + 2 >= n:
                if on_missing == 'hold':
                    out[i] = out[i - 1]
                    actual_count = i + 1
                    continue
                break
            out[i] = out[i - 1] + _read_escaped_i16(b, idx + 1)
            pbytes_offset += 2
        else:
            out[i] = out[i - 1] + b[idx]
        actual_count = i + 1

    return out if on_missing == 'hold' else out[:actual_count]


def _read_escaped_i16(b, hi_idx):
    hi, lo = b[hi_idx], b[hi_idx + 1]
    val = ((hi & 0xff) << 8) | (lo & 0xff)
    if val >= 0x8000:
        val -= 0x10000
    return val
