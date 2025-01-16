import os
import json
import sys
from tkinter import filedialog

def skip4Bytes(f):
    f.seek(0x04 + f.tell())

def write_padding(f, padding_size):
    f.write(b'\x00' * padding_size)

def bytes_to_int32(aob):
    return int.from_bytes(aob, "little", signed="False")

def int32_to_4bytes(intValue):
    return intValue.to_bytes(4, "little", signed="False") # the file should never accomodate negative integers

def bytes_to_aob_formatted(b):
    return ' '.join(f'{byte:02X}' for byte in b)

def hexify_string(str):
    return str.encode("utf-16").hex()[4:] + "0000"

def main():
    if len(sys.argv) < 3:
        print("Usage: python chameleon_string_editor.py <input_file> <bit: 32/64> <mode: -u/-p>")
        print("Example: python chameleon_string_editor.py input.dat 64 -u")
        sys.exit(1)

    input_file = sys.argv[1]
    bit = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else None

    if bit not in ["32", "64"]:
        print("Error: <bit> must be '32' or '64'.")
        sys.exit(1)
    bit = int(bit)

    if mode not in ["-u", "-p"]:
        print("Error: <mode> must be '-u' (unpack) or '-p' (pack).")
        sys.exit(1)

    if not os.path.isfile(input_file):
        print(f"Error: Input file does not exist: {input_file}")
        sys.exit(1)

    file_extension = os.path.splitext(input_file)[1][1:]
    if mode == "-u" and file_extension != "dat":
        print("Error: File extension must be .dat for unpacking.")
        sys.exit(1)
    elif mode == "-p" and file_extension != "json":
        print("Error: File extension must be .json for packing.")
        sys.exit(1)

    if mode == "-u":
        mode_Unpack(input_file, bit)
    elif mode == "-p":
        mode_Pack(input_file, bit)
    
class mode_Unpack:

    Language_IDs = []
    Language_String = []
    Language_Indicator = None

    def __init__(self, dat_file, bit):
        with open(dat_file, 'rb') as f:
            if (bit == 32):
                self.Language_Indicator = bytes_to_aob_formatted(f.read(0x04))
                lang_entry_count = bytes_to_int32(f.read(0x04))
                pointer_langIDs = bytes_to_int32(f.read(0x04))
                pointer_langInformations = bytes_to_int32(f.read(0x04))

                f.seek(pointer_langIDs)
                for i in range(lang_entry_count):
                    self.Language_IDs.append(bytes_to_aob_formatted(f.read(0x04)))

                f.seek(pointer_langInformations)
                pointer_langStoredAt = []
                pointer_langLength = []
                for i in range(lang_entry_count):
                    pointer_langStoredAt.append(bytes_to_int32(f.read(0x04)))
                    pointer_langLength.append(bytes_to_int32(f.read(0x04)))

                for i in range(lang_entry_count):
                    f.seek(pointer_langStoredAt[i])
                    tempString = f.read(pointer_langLength[i]*2).hex()
                    tempString = tempString[:-4]
                    decodedString = bytes.fromhex(tempString).decode("utf-16")
                    self.Language_String.append(decodedString)

            elif (bit == 64):
                self.Language_Indicator = bytes_to_aob_formatted(f.read(0x04))
                lang_entry_count = bytes_to_int32(f.read(0x04))
                pointer_langIDs = bytes_to_int32(f.read(0x04))
                skip4Bytes(f)
                pointer_langInformations = bytes_to_int32(f.read(0x04))

                f.seek(pointer_langIDs)
                for i in range(lang_entry_count):
                    self.Language_IDs.append(bytes_to_aob_formatted(f.read(0x04)))

                f.seek(pointer_langInformations)
                pointer_langStoredAt = []
                pointer_langLength = []
                for i in range(lang_entry_count):
                    pointer_langStoredAt.append(bytes_to_int32(f.read(0x04)))
                    skip4Bytes(f)
                    pointer_langLength.append(bytes_to_int32(f.read(0x04)))
                    skip4Bytes(f)

                for i in range(lang_entry_count):
                    f.seek(pointer_langStoredAt[i])
                    tempString = f.read(pointer_langLength[i]*2).hex()
                    tempString = tempString[:-4]
                    decodedString = bytes.fromhex(tempString).decode("utf-16")
                    self.Language_String.append(decodedString)
            else:
                return

        self.jsonify()

    def jsonify(self):
        data = {
            "LangType": self.Language_Indicator,
            "Entries": [
                {"Language ID": lang_id, "Language String": lang_string}
                for lang_id, lang_string in zip(self.Language_IDs, self.Language_String)
            ]
        }
        json_data = json.dumps(data, indent=2, ensure_ascii=False)

        output_file = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")], 
            title="Save JSON File"
        )

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as json_file:
                json_file.write(json_data)
            print(f"JSON data saved successfully to {output_file}.")
        else:
            print("JSON data not saved.")

class mode_Pack:

    Language_IDs = []
    Language_String = []
    Language_String_Hexified = []
    Language_Indicator = None

    # Supporting variables
    lang_string_offset = []
    lang_string_length = []

    def __init__(self, json_file, bit):
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

            self.Language_Indicator = json_data.get("LangType")

            for item in json_data["Entries"]:
                self.Language_IDs.append(item["Language ID"])
                self.Language_String.append(item["Language String"])
                self.Language_String_Hexified.append(hexify_string(item["Language String"]))

            self.datify(bit)

    def datify(self, bit):
        output_file = filedialog.asksaveasfilename(
            defaultextension=".dat", 
            filetypes=[("DAT files", "*.dat"), ("All files", "*.*")], 
            title="Save DAT File"
        )

        if not output_file:
            print("DAT file not saved.")
            return
        
        with open(output_file, 'wb') as f:
            if (bit == 32):
                f.write(bytes.fromhex(self.Language_Indicator.replace(' ', '')))
                f.write(int32_to_4bytes(len(self.Language_IDs)))
                f.write(b'\x10\x00\x00\x00')
                f.write(int32_to_4bytes( (len(self.Language_IDs) * 4) + 16))

                for lang_id in self.Language_IDs:
                    f.write(bytes.fromhex(lang_id.replace(' ', '')))

                # Will come back to this later
                write_padding(f, len(self.Language_IDs) * 8)

                for hex_string in self.Language_String_Hexified:
                    self.lang_string_offset.append(f.tell())
                    self.lang_string_length.append(len(hex_string) // 4)
                    f.write(bytes.fromhex(hex_string))

                f.seek( (len(self.Language_IDs) * 4) + 16)
                for lang_str_pt, lang_str_len in zip(self.lang_string_offset, self.lang_string_length):
                    f.write(int32_to_4bytes(lang_str_pt))
                    f.write(int32_to_4bytes(lang_str_len))

                f.seek(0, os.SEEK_END)
                eof_offset = f.tell()
                if (eof_offset % 16 != 0):
                    padding_required = 16 - (eof_offset % 16)
                    write_padding(f, padding_required)

            elif (bit == 64):
                f.write(bytes.fromhex(self.Language_Indicator.replace(' ', '')))
                f.write(int32_to_4bytes(len(self.Language_IDs)))
                f.write(b'\x18\x00\x00\x00')
                write_padding(f, 4)
                f.write(int32_to_4bytes( (len(self.Language_IDs) * 4) + 24))
                write_padding(f, 4)

                for lang_id in self.Language_IDs:
                    f.write(bytes.fromhex(lang_id.replace(' ', '')))

                # Will come back to this later
                write_padding(f, len(self.Language_IDs) * 16)

                for hex_string in self.Language_String_Hexified:
                    self.lang_string_offset.append(f.tell())
                    self.lang_string_length.append(len(hex_string) // 4)
                    f.write(bytes.fromhex(hex_string))

                f.seek( (len(self.Language_IDs) * 4) + 24)
                for lang_str_pt, lang_str_len in zip(self.lang_string_offset, self.lang_string_length):
                    f.write(int32_to_4bytes(lang_str_pt))
                    skip4Bytes(f)
                    f.write(int32_to_4bytes(lang_str_len))
                    skip4Bytes(f)

                f.seek(0, os.SEEK_END)
                eof_offset = f.tell()
                if (eof_offset % 16 != 0):
                    padding_required = 16 - (eof_offset % 16)
                    write_padding(f, padding_required)
            else:
                return

        print(f"DAT file packed successfully to {output_file}.")

if __name__ == "__main__":
    main()