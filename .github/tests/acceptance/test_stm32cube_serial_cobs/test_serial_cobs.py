import time

from conftest import press_button

# COBS encoding of float 34.52 (little-endian bytes: 7B 14 0A 42) with term char.
# Verified manually: COBS([7B, 14, 0A, 42]) = [05, 7B, 14, 0A, 42], then + 00.
EXPECTED_COBS_PACKET = bytes([0x05, 0x7B, 0x14, 0x0A, 0x42, 0x00])

# COBS-encoded float 5.156 (little-endian bytes: F4 FD A4 40).
# COBS([F4, FD, A4, 40]) = [05, F4, FD, A4, 40], then + 00.
COBS_PACKET_TO_SEND = bytes([0x05, 0xF4, 0xFD, 0xA4, 0x40, 0x00])
EXPECTED_DECODED_ECHO = bytes([0xF4, 0xFD, 0xA4, 0x40])

UART_TERM_CHAR = 0x00


def read_cobs_packet(ser, timeout=2.0):
    """Read bytes from ser until the COBS term char (0x00) is received or timeout."""
    packet = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        byte = ser.read(1)
        if byte:
            packet += byte
            if byte[0] == UART_TERM_CHAR:
                return packet
    return packet


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_no_output_initially(setup_hardware):
    """No serial output must appear before any button press."""
    ser = setup_hardware
    data = b""
    start = time.time()
    while time.time() - start < 2.0:
        chunk = ser.read(ser.in_waiting or 1)
        if chunk:
            data += chunk
    assert len(data) == 0, (
        f"Expected no serial output initially, but received: {data.hex(' ')}"
    )
    print("No output received before button press")


def test_button_press_sends_cobs_encoded_float(setup_hardware):
    """Pressing the button must send the COBS-encoded float 34.52 via serial."""
    ser = setup_hardware

    print("Pressing button...")
    press_button()

    packet = read_cobs_packet(ser)
    assert packet == EXPECTED_COBS_PACKET, (
        f"Expected {EXPECTED_COBS_PACKET.hex(' ')}, got {packet.hex(' ')}"
    )
    print(f"Received correct COBS packet: {packet.hex(' ')}")


def test_multiple_button_presses_produce_multiple_packets(setup_hardware):
    """Each button press must generate exactly one COBS packet."""
    ser = setup_hardware
    n_presses = 3

    for _ in range(n_presses):
        press_button()

    packets = []
    for _ in range(n_presses):
        packet = read_cobs_packet(ser)
        packets.append(packet)

    assert len(packets) == n_presses, (
        f"Expected {n_presses} packets, got {len(packets)}"
    )
    for i, pkt in enumerate(packets):
        assert pkt == EXPECTED_COBS_PACKET, (
            f"Packet {i + 1} mismatch: expected {EXPECTED_COBS_PACKET.hex(' ')}, "
            f"got {pkt.hex(' ')}"
        )
    print(f"Received {n_presses} correct COBS packets, one per button press")


def test_cobs_receive_decode_echo(setup_hardware):
    """Sending a COBS packet must cause the MCU to echo back the decoded bytes."""
    ser = setup_hardware

    print(f"Sending COBS packet: {COBS_PACKET_TO_SEND.hex(' ')}")
    ser.write(COBS_PACKET_TO_SEND)

    echo = ser.read(len(EXPECTED_DECODED_ECHO))
    assert echo == EXPECTED_DECODED_ECHO, (
        f"Expected decoded echo {EXPECTED_DECODED_ECHO.hex(' ')}, got {echo.hex(' ')}"
    )
    print(f"Received correct decoded echo: {echo.hex(' ')}")
