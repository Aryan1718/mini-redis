import struct
import time

def load_rdb(filename):
    """
    Parses a Redis RDB file and returns a dictionary of data and expiry times.
    Returns: (data_store, expiry_store)
    """
    data_store = {}
    expiry_store = {}
    
    try:
        with open(filename, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        return {}, {}
        
    if not data.startswith(b"REDIS"):
        print("Invalid RDB file format")
        return {}, {}
    
    pos = 9 # Skip REDIS + 4 byte version
    
    while pos < len(data):
        opcode = data[pos]
        pos += 1
        
        if opcode == 0xFF: # EOF
            break
        elif opcode == 0xFE: # Select DB
            # Read database index (length encoded)
            db_index, new_pos = read_length(data, pos)
            pos = new_pos
            # We only support one DB (0) for now or merge all
            continue
        elif opcode == 0xFD: # Expire time in seconds
            expiry_s = struct.unpack("<I", data[pos:pos+4])[0]
            pos += 4
            expiry_ms = expiry_s * 1000
            # Read value type and key/value
            value_type = data[pos]
            pos += 1
            key, new_pos = read_string(data, pos)
            pos = new_pos
            value, new_pos = read_string(data, pos)
            pos = new_pos
            
            data_store[key] = value
            expiry_store[key] = expiry_ms
            
        elif opcode == 0xFC: # Expire time in milliseconds
            expiry_ms = struct.unpack("<Q", data[pos:pos+8])[0]
            pos += 8
            # Read value type and key/value
            value_type = data[pos]
            pos += 1
            key, new_pos = read_string(data, pos)
            pos = new_pos
            value, new_pos = read_string(data, pos)
            pos = new_pos
            
            data_store[key] = value
            expiry_store[key] = expiry_ms
            
        elif opcode == 0xFA: # Aux field (metadata)
            key, new_pos = read_string(data, pos)
            pos = new_pos
            value, new_pos = read_string(data, pos)
            pos = new_pos
            
        elif opcode == 0xFB: # Resize DB
            # Reads two length-encoded integers (db_size, expires_size)
            _, new_pos = read_length(data, pos)
            pos = new_pos
            _, new_pos = read_length(data, pos)
            pos = new_pos
            
        else:
            # Assume it's a value type (0 = string) if it's not a special opcode
            # Wait, standard RDB format has Value Type BEFORE Key
            # But here, if we hit a Value Type directly, it means no expiry
            value_type = opcode
            if value_type == 0: # String
                key, new_pos = read_string(data, pos)
                pos = new_pos
                value, new_pos = read_string(data, pos)
                pos = new_pos
                data_store[key] = value
            else:
                 # TODO: Handle other types if necessary
                 # For now, just try to read key/value as string? No, structure is different.
                 print(f"Unknown Opcode or Type: {opcode}")
                 break

    return data_store, expiry_store

def read_length(data, pos):
    """
    Reads a length-encoded integer from the RDB data at pos.
    Returns (length, new_pos)
    """
    first_byte = data[pos]
    pos += 1
    
    # 00xxxxxx: 6-bit length
    if (first_byte & 0xC0) == 0:
        length = first_byte & 0x3F
        return length, pos
        
    # 01xxxxxx: 14-bit length
    elif (first_byte & 0xC0) == 0x40:
        next_byte = data[pos]
        pos += 1
        length = ((first_byte & 0x3F) << 8) | next_byte
        return length, pos
        
    # 10xxxxxx: 32-bit length
    elif (first_byte & 0xC0) == 0x80:
        length = struct.unpack(">I", data[pos:pos+4])[0]
        pos += 4
        return length, pos
        
    # 11xxxxxx: Special format (encoded integer)
    elif (first_byte & 0xC0) == 0xC0:
        encoding_type = first_byte & 0x3F
        if encoding_type == 0: # 8 bit integer
            val = int.from_bytes(data[pos:pos+1], 'little')
            pos += 1
            return val, pos
        elif encoding_type == 1: # 16 bit integer
            val = int.from_bytes(data[pos:pos+2], 'little')
            pos += 2
            return val, pos
        elif encoding_type == 2: # 32 bit integer
            val = int.from_bytes(data[pos:pos+4], 'little')
            pos += 4
            return val, pos
            
    return 0, pos

def read_string(data, pos):
    """
    Reads a string (key or value) from RDB data.
    First reads length (which might indicate integer encoding), then reads content.
    """
    first_byte = data[pos]
    
    # Check if it's length encoded or special integer encoding
    # 11xxxxxx indicates special integer encoding for the string object itself
    if (first_byte & 0xC0) == 0xC0:
        # It's an integer encoded as a string
        val, new_pos = read_length(data, pos)
        return str(val), new_pos
        
    length, new_pos = read_length(data, pos)
    pos = new_pos
    
    val = data[pos:pos+length].decode()
    pos += length
    
    return val, pos

def save_rdb(filename, data_store, expiry_store):
    """
    Saves the current state to an RDB file.
    """
    with open(filename, "wb") as f:
        # Header
        f.write(b"REDIS0009")
        
        # Database Selection (DB 0)
        f.write(b"\xFE\x00")
        
        # Iterate through data
        for key, value in data_store.items():
            # Check expiry
            if key in expiry_store:
                expiry = expiry_store[key]
                if time.time() * 1000 > expiry:
                    continue # Skip expired keys
                
                # Write Expire Time (ms)
                f.write(b"\xFC")
                f.write(struct.pack("<Q", int(expiry)))
                
            # Value Type (0 = String)
            f.write(b"\x00")
            
            # Key
            f.write(encode_string(key))
            
            # Value
            f.write(encode_string(value))
            
        # EOF
        f.write(b"\xFF")
        
        # Checksum (8 bytes) - using 0 as placeholder
        f.write(b"\x00" * 8)
        
def encode_length(length):
    """
    Encodes a length into RDB format bytes.
    """
    if length < 64:
        # 00xxxxxx
        return struct.pack("B", length)
    elif length < 16384:
        # 01xxxxxx
        return struct.pack(">H", length | 0x4000)
    else:
        # 10xxxxxx + 4 bytes
        return b"\x80" + struct.pack(">I", length)

def encode_string(s):
    """
    Encodes a string into RDB format bytes.
    """
    encoded = s.encode()
    length = len(encoded)
    return encode_length(length) + encoded
