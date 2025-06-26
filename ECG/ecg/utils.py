def pad_buffer(buffer, size):
    if len(buffer) < size:
        return [buffer[0]] * (size - len(buffer)) + buffer
    return buffer