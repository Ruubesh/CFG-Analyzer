def convert(entry_int, output_string):
    mile_input = entry_int.get()
    km_output = mile_input * 1.61
    output_string.set(km_output)
