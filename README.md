## Chameleon String Editor

You can now modify the strings made by any Chameleon Engine games (NFSHP10, NFSMW12, NFSHPR) without having to mass edit offsets.

### Prerequisites
* DGI's [bundle_unpacker](https://github.com/DGIorio/bundle_packer_unpacker)
* Python (only tested on 3.12 and above, but should work on 3.0 and above)

## Usage

1. **Unpack a desired language file** from your chosen game. It should be located under `..\UI\LANGUAGE`.

   **List of languages:**
   
   - `0001.BNDL` (English US)
   - `0002.BNDL` (English UK)
   - `0003.BNDL` (French)
   - `0004.BNDL` (Spanish)
   - `0005.BNDL` (Italian)
   - `0006.BNDL` (German)
   - `0007.BNDL` (Russian)
   - `0008.BNDL` (Polish)
   - `0009.BNDL` (Czech)
   - `0010.BNDL` (Hungarian)
   - `0011.BNDL` (Japanese)
   - `0012.BNDL` (Traditional Chinese)
   - `0013.BNDL` (Dutch)

2. **After unpacking the BNDL file**, modify the `example.bat` file to change the settings, or just launch it through a shell. It includes the following parameters:

   - `<input_file>`: Directory to your input file (should be `.dat` or `.json` only).
   - `<bit>`: Bit version of the game, either `32` (NFSHP10, NFSMW12) or `64` (NFSHPR) only.
   - `<mode>`: Use `-u` for Unpack, or `-p` for Packing.
   - Example: `python chameleon_string_editor.py input.dat 64 -u`

3. **After modifying the JSON file**, use `-p` as the packing argument. Then, pack the new `.dat` file and restart your game for the changes to take effect.

# Notes
- I completely eyeballed this project and it's not thoroughly tested, but it should work just fineee based on what I know about the file.. I think?
- It doesn't display the font colours quite properly, as I've never bothered to go dig the game code to figure out what each colour hex is. In the json file, the code may appear as a `` symbol. You have to manually modify it through a hex editor if you wish to change the colour of that specific string.
- Please make backup before you do any modifications, it's not my responsibility to remind you but you kno.. :^