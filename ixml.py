#!/usr/bin/env python3

import struct
import os
import sys
import argparse
import configparser
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any

"""
BWF Metadata Writer - Write comprehensive BWF metadata to WAVE files
Reads metadata from dictionaries and writes to BEXT, ID3, LIST INFO, iXML, and XMP chunks
"""

class BWFMetadataWriter:
    """Write comprehensive BWF metadata to WAVE files"""
    
    def __init__(self, wav_filepath: str, metadata_dict: Dict[str, Any]):
        """
        Initialize BWF Metadata Writer
        
        Args:
            wav_filepath: Path to WAV file to write metadata to
            metadata_dict: Dictionary containing metadata fields
        """
        self.wav_filepath = wav_filepath
        self.metadata_dict = metadata_dict
        
        # Auto-write metadata on construction
        self.write_metadata()
    
    def write_metadata(self):
        """Write metadata to the WAV file using provided dictionary"""
        # Convert dictionary format to internal format
        metadata = self._convert_dict_to_metadata(self.metadata_dict)
        
        # Write to WAV file
        self.write_metadata_to_wav(self.wav_filepath, metadata)
    
    def _convert_dict_to_metadata(self, metadata_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Convert flat input dictionary to internal metadata format"""
        # Extract filename from filepath
        filename = os.path.basename(self.wav_filepath)
        
        return {
            'metadata': metadata_dict,
            'filename': filename
        }
    
    def read_ini_metadata(self, ini_file: str, source_filename: str) -> Dict[str, Any]:
        """Read metadata from .ini file for specific source filename (legacy method)"""
        config = configparser.ConfigParser()
        config.read(ini_file, encoding='utf-8')
        
        if source_filename not in config:
            raise ValueError(f"Section '{source_filename}' not found in {ini_file}")
        
        # Read the metadata from the section
        section = config[source_filename]
        
        # Convert to flat dictionary
        metadata = {}
        for key in section:
            metadata[key] = section[key]
        
        return metadata
    
    def create_bext_chunk(self, metadata: Dict[str, Any]) -> bytes:
        """Create BEXT chunk from metadata"""
        meta = metadata['metadata']
        
        # BEXT structure (BWF version 0)
        bext_data = bytearray(602)  # Fixed size for version 0
        
        # Originator (32 bytes) - use Designer
        originator = meta.get('Designer', '')[:31].encode('ascii', errors='replace')
        bext_data[0:len(originator)] = originator
        
        # OriginatorReference (32 bytes) - use CatID + Source ID
        ref = f"{meta.get('CatID', '')}_{meta.get('Source ID', '')}"[:31]
        ref_bytes = ref.encode('ascii', errors='replace')
        bext_data[32:32+len(ref_bytes)] = ref_bytes
        
        # Description (256 bytes)
        desc = meta.get('Description', '')[:255].encode('ascii', errors='replace')
        bext_data[64:64+len(desc)] = desc
        
        # OriginationDate (10 bytes) - current date YYYY-MM-DD
        date_str = datetime.now().strftime('%Y-%m-%d').encode('ascii')
        bext_data[320:320+len(date_str)] = date_str
        
        # OriginationTime (8 bytes) - current time HH:MM:SS
        time_str = datetime.now().strftime('%H:%M:%S').encode('ascii')
        bext_data[330:330+len(time_str)] = time_str
        
        # TimeReference (8 bytes) - set to 0
        struct.pack_into('<Q', bext_data, 338, 0)
        
        # Version (2 bytes) - BWF version 0
        struct.pack_into('<H', bext_data, 346, 0x0000)
        
        # UMID (64 bytes) - leave empty
        # Reserved (190 bytes) - leave empty
        # CodingHistory - leave empty for version 0
        
        return bytes(bext_data)
    
    def create_id3_chunk(self, metadata: Dict[str, Any]) -> bytes:
        """Create ID3v2.3 chunk from metadata"""
        meta = metadata['metadata']
        
        frames = []
        
        # Helper function to create text frame
        def create_text_frame(frame_id: str, text: str) -> bytes:
            if not text:
                return b''
            text_data = text.encode('utf-8', errors='replace')
            frame_data = b'\x03' + text_data  # UTF-8 encoding
            frame_size = len(frame_data)
            frame_flags = b'\x00\x00'
            return frame_id.encode('ascii') + struct.pack('>I', frame_size) + frame_flags + frame_data
        
        # Create frames
        frames.append(create_text_frame('TIT2', meta.get('Title', '')))  # Title
        frames.append(create_text_frame('TCON', meta.get('Category', '')))  # Genre/Category
        frames.append(create_text_frame('TPE1', meta.get('Designer', '')))  # Artist
        frames.append(create_text_frame('TPE2', meta.get('Library', '')))  # Album Artist
        frames.append(create_text_frame('TOAL', meta.get('Library', '')))  # Original Album
        frames.append(create_text_frame('TPUB', meta.get('URL', '')))  # Publisher
        frames.append(create_text_frame('TIT1', meta.get('URL', '')))  # Content Group
        frames.append(create_text_frame('TYER', str(datetime.now().year)))  # Year
        frames.append(create_text_frame('TORY', str(datetime.now().year)))  # Original Year
        frames.append(create_text_frame('TCOP', f"{datetime.now().year} {meta.get('Manufacturer', '')}"))  # Copyright
        frames.append(create_text_frame('TIT3', meta.get('Notes', '')))  # Subtitle
        frames.append(create_text_frame('TOWN', meta.get('Library', '')))  # Owner
        frames.append(create_text_frame('TRCK', meta.get('Source ID', '0')))  # Track
        
        # Comment frame (COMM)
        description = meta.get('Description', '')
        if description:
            comm_data = b'\x03eng\x00' + description.encode('utf-8', errors='replace')
            comm_frame = b'COMM' + struct.pack('>I', len(comm_data)) + b'\x00\x00' + comm_data
            frames.append(comm_frame)
        
        # Combine all frames
        frames_data = b''.join(frames)
        
        # ID3v2 header
        id3_size = len(frames_data)
        # Convert to syncsafe integer
        syncsafe_size = ((id3_size & 0x0FE00000) << 3) | ((id3_size & 0x001FC000) << 2) | ((id3_size & 0x00003F80) << 1) | (id3_size & 0x0000007F)
        
        header = b'ID3\x03\x00\x00' + struct.pack('>I', syncsafe_size)
        
        return header + frames_data
    
    def create_list_info_chunk(self, metadata: Dict[str, Any]) -> bytes:
        """Create LIST INFO chunk from metadata"""
        meta = metadata['metadata']
        
        def create_info_subchunk(chunk_id: str, text: str) -> bytes:
            if not text:
                return b''
            text_data = text.encode('utf-8', errors='replace') + b'\x00'
            # Pad to even length
            if len(text_data) % 2:
                text_data += b'\x00'
            return chunk_id.encode('ascii') + struct.pack('<I', len(text_data)) + text_data
        
        subchunks = []
        subchunks.append(create_info_subchunk('ISFT', 'BWF Metadata Writer'))  # Software
        subchunks.append(create_info_subchunk('INAM', metadata['filename']))  # Name
        subchunks.append(create_info_subchunk('ICRD', datetime.now().strftime('%Y-%m-%d')))  # Creation date
        subchunks.append(create_info_subchunk('IPRD', meta.get('Library', '')))  # Product
        subchunks.append(create_info_subchunk('IGNR', meta.get('Category', '')))  # Genre
        subchunks.append(create_info_subchunk('ICOP', f"{datetime.now().year} {meta.get('Manufacturer', '')}"))  # Copyright
        subchunks.append(create_info_subchunk('ICMT', meta.get('Description', '')))  # Comment
        subchunks.append(create_info_subchunk('IARL', f"© {datetime.now().year} {meta.get('Manufacturer', '')} All Rights Reserved"))  # Archival location
        subchunks.append(create_info_subchunk('IART', meta.get('Designer', '')))  # Artist
        
        info_data = b'INFO' + b''.join(subchunks)
        list_size = len(info_data)
        
        return b'LIST' + struct.pack('<I', list_size) + info_data
    
    def create_ixml_chunk(self, metadata: Dict[str, Any]) -> bytes:
        """Create iXML chunk with both Steinberg and USER sections"""
        meta = metadata['metadata']
        current_year = str(datetime.now().year)
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Build Steinberg ATTR_LIST
        steinberg_attrs = [
            ('MediaLibrary', 'string', meta.get('Library', '')),
            ('MediaCategoryPost', 'string', meta.get('Category', '')),
            ('MediaRecordingMethod', 'string', meta.get('Microphone', '')),
            ('MediaComment', 'string', meta.get('Description', '')),
            ('MusicalCategory', 'string', meta.get('SubCategory', '')),
            ('MediaCompany', 'string', meta.get('URL', '')),
            ('MediaLibraryManufacturerName', 'string', meta.get('Manufacturer', '')),
            ('MediaArtist', 'string', meta.get('Designer', '')),
            ('MediaTrackNumber', 'string', meta.get('Source ID', '0')),
            ('SmfSongName', 'string', metadata['filename']),
            ('MusicalInstrument', 'string', metadata['filename']),
        ]
        
        # Build USER section fields
        subcategory = meta.get('SubCategory', '') or meta.get('Subcategory', '')
        category = meta.get('Category', '')
        category_full = f"{category}-{subcategory}" if category and subcategory else category or subcategory
        
        # Handle field name variations
        rec_medium = meta.get('Recording Medium', '') or meta.get('RecMedium', '')
        mic_perspective = meta.get('Microphone Perspective', '') or meta.get('MicPerspective', '')
        
        user_fields = [
            ('MICROPHONE', meta.get('Microphone', '')),
            ('LIBRARY', meta.get('Library', '')),
            ('CATEGORYFULL', category_full),
            ('DESCRIPTION', meta.get('Description', '')),
            ('TRACKTITLE', meta.get('TrackTitle', '') or metadata['filename']),
            ('NOTES', meta.get('Notes', '')),
            ('ARTIST', meta.get('Designer', '')),
            ('TRACKYEAR', current_year),
            ('CATEGORY', category),
            ('SOURCE', meta.get('URL', '')),
            ('EMBEDDER', 'BWF Metadata Writer'),
            ('TRACK', meta.get('Source ID', '0')),
            ('KEYWORDS', meta.get('Keywords', '') or metadata['filename']),
            ('URL', meta.get('URL', '')),
            ('VOLUME', meta.get('URL', '')),
            ('SHOOTDATE', current_datetime),
            ('SUBCATEGORY', subcategory),
            ('MANUFACTURER', meta.get('Manufacturer', '')),
            ('RATING', '0'),
            ('FXNAME', meta.get('FX Name', '')),
            ('CATID', meta.get('CatID', '') or meta.get('CatId', '')),
            ('RELEASEDATE', current_date),
            ('MICPERSPECTIVE', mic_perspective),
            ('RECORDINGMEDIUM', rec_medium),
            ('MICCONFIG', meta.get('Microphone Configuration', '')),
            ('INOUTSIDE', meta.get('Inside or Outside', '')),
            ('LOCATION', meta.get('Location', '')),
            ('USERCATEGORY', meta.get('User Category', '')),
            ('VENDORCATEGORY', meta.get('Vendor Category', '')),
        ]
        
        # Build XML structure
        root = ET.Element('BWFXML')
        
        # IXML_VERSION
        version_elem = ET.SubElement(root, 'IXML_VERSION')
        version_elem.text = '1.61'
        
        # STEINBERG section
        steinberg_elem = ET.SubElement(root, 'STEINBERG')
        attr_list_elem = ET.SubElement(steinberg_elem, 'ATTR_LIST')
        
        for name, attr_type, value in steinberg_attrs:
            if value:  # Only add non-empty values
                attr_elem = ET.SubElement(attr_list_elem, 'ATTR')
                name_elem = ET.SubElement(attr_elem, 'NAME')
                name_elem.text = name
                type_elem = ET.SubElement(attr_elem, 'TYPE')
                type_elem.text = attr_type
                value_elem = ET.SubElement(attr_elem, 'VALUE')
                value_elem.text = str(value)
        
        # USER section
        user_elem = ET.SubElement(root, 'USER')
        for field_name, field_value in user_fields:
            if field_value:  # Only add non-empty values
                field_elem = ET.SubElement(user_elem, field_name)
                field_elem.text = str(field_value)
        
        # Convert to string with proper formatting
        xml_str = ET.tostring(root, encoding='unicode')
        # Add proper indentation
        xml_formatted = self._format_xml(xml_str)
        
        xml_data = xml_formatted.encode('utf-8')
        return xml_data
    
    def _format_xml(self, xml_str: str) -> str:
        """Format XML with proper indentation"""
        # Simple formatting - add newlines and indentation
        formatted = xml_str.replace('><', '>\n<')
        lines = formatted.split('\n')
        indented_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith('</'):
                indent_level -= 1
            
            indented_lines.append('  ' * indent_level + line)
            
            if line.startswith('<') and not line.startswith('</') and not line.endswith('/>') and not '>' in line[1:]:
                indent_level += 1
            elif line.startswith('<') and not line.startswith('</') and not line.endswith('/>'):
                # Opening tag with content
                pass
        
        return '\n'.join(indented_lines)
    
    def create_xmp_chunk(self, metadata: Dict[str, Any]) -> bytes:
        """Create XMP (_PMX) chunk from metadata"""
        meta = metadata['metadata']
        current_datetime = datetime.now().isoformat()
        
        # Escape XML special characters
        def escape_xml(text):
            if not text:
                return ''
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
        
        category = meta.get('Category', '')
        subcategory = meta.get('SubCategory', '')
        genre = f"{category}-{subcategory}" if category and subcategory else category or subcategory
        
        xmp_template = f'''<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.5.0">
   <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:about=""
            xmlns:xmp="http://ns.adobe.com/xap/1.0/"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:xmpDM="http://ns.adobe.com/xmp/1.0/DynamicMedia/">
         <xmp:CreatorTool>BWF Metadata Writer</xmp:CreatorTool>
         <xmp:MetadataDate>{current_datetime}</xmp:MetadataDate>
         <xmp:ModifyDate>{current_datetime}</xmp:ModifyDate>
         <xmp:rating>0.000000</xmp:rating>
         <dc:description>
            <rdf:Alt>
               <rdf:li xml:lang="x-default">{escape_xml(meta.get('Description', ''))}</rdf:li>
               <rdf:li xml:lang="en-US">{escape_xml(meta.get('Description', ''))}</rdf:li>
            </rdf:Alt>
         </dc:description>
         <dc:publisher>
            <rdf:Bag>
               <rdf:li>{escape_xml(meta.get('URL', ''))}</rdf:li>
            </rdf:Bag>
         </dc:publisher>
         <dc:title>
            <rdf:Alt>
               <rdf:li xml:lang="x-default">{escape_xml(meta.get('FX Name', ''))}</rdf:li>
               <rdf:li xml:lang="en-US">{escape_xml(meta.get('FX Name', ''))}</rdf:li>
            </rdf:Alt>
         </dc:title>
         <xmpDM:comment>{escape_xml(meta.get('Notes', ''))}</xmpDM:comment>
         <xmpDM:logComment>{escape_xml(meta.get('Notes', ''))}</xmpDM:logComment>
         <xmpDM:album>{escape_xml(meta.get('Library', ''))}</xmpDM:album>
         <xmpDM:artist>{escape_xml(meta.get('Designer', ''))}</xmpDM:artist>
         <xmpDM:genre>{escape_xml(genre)}</xmpDM:genre>
      </rdf:Description>
   </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''
        
        return xmp_template.encode('utf-8')
    
    def write_metadata_to_wav(self, wav_file: str, metadata: Dict[str, Any]):
        """Write all metadata chunks to existing WAV file"""
        # Create all chunks
        bext_chunk = self.create_bext_chunk(metadata)
        id3_chunk = self.create_id3_chunk(metadata)
        list_chunk = self.create_list_info_chunk(metadata)
        ixml_chunk = self.create_ixml_chunk(metadata)
        xmp_chunk = self.create_xmp_chunk(metadata)
        
        # Read existing WAV file
        with open(wav_file, 'rb') as f:
            original_data = f.read()
        
        # Parse existing RIFF structure
        if original_data[:4] != b'RIFF' or original_data[8:12] != b'WAVE':
            raise ValueError("Not a valid WAV file")
        
        # Find existing chunks and remove metadata chunks if they exist
        chunks_to_keep = []
        pos = 12  # Skip RIFF header
        original_size = struct.unpack('<I', original_data[4:8])[0]
        
        while pos < len(original_data) and pos < original_size + 8:
            if pos + 8 > len(original_data):
                break
                
            chunk_id = original_data[pos:pos+4]
            chunk_size = struct.unpack('<I', original_data[pos+4:pos+8])[0]
            
            # Skip metadata chunks we're replacing
            if chunk_id not in [b'bext', b'ID3 ', b'LIST', b'iXML', b'_PMX']:
                chunk_data = original_data[pos:pos+8+chunk_size]
                # Add padding if needed
                if chunk_size % 2:
                    if pos + 8 + chunk_size < len(original_data):
                        chunk_data += original_data[pos+8+chunk_size:pos+8+chunk_size+1]
                chunks_to_keep.append(chunk_data)
            
            # Move to next chunk
            pos += 8 + chunk_size
            if chunk_size % 2:  # Skip padding
                pos += 1
        
        # Build new file
        new_chunks = []
        
        # Add our metadata chunks first
        new_chunks.append(b'bext' + struct.pack('<I', len(bext_chunk)) + bext_chunk)
        if len(bext_chunk) % 2:
            new_chunks[-1] += b'\x00'
            
        new_chunks.append(b'ID3 ' + struct.pack('<I', len(id3_chunk)) + id3_chunk)
        if len(id3_chunk) % 2:
            new_chunks[-1] += b'\x00'
            
        new_chunks.append(list_chunk)  # LIST chunk includes its own header
        if len(list_chunk) % 2:
            new_chunks[-1] += b'\x00'
            
        new_chunks.append(b'iXML' + struct.pack('<I', len(ixml_chunk)) + ixml_chunk)
        if len(ixml_chunk) % 2:
            new_chunks[-1] += b'\x00'
            
        new_chunks.append(b'_PMX' + struct.pack('<I', len(xmp_chunk)) + xmp_chunk)
        if len(xmp_chunk) % 2:
            new_chunks[-1] += b'\x00'
        
        # Add existing chunks
        new_chunks.extend(chunks_to_keep)
        
        # Calculate new file size
        new_data = b''.join(new_chunks)
        new_file_size = len(new_data) + 4  # +4 for 'WAVE'
        
        # Write new file
        with open(wav_file, 'wb') as f:
            f.write(b'RIFF')
            f.write(struct.pack('<I', new_file_size))
            f.write(b'WAVE')
            f.write(new_data)
        
        print(f"Successfully wrote metadata to {wav_file}")


def main():
    parser = argparse.ArgumentParser(description='BWF Metadata Writer - Write metadata to WAV files')
    parser.add_argument('wav_file', help='Path to WAV file to write metadata to')
    
    args = parser.parse_args()
    
    print("BWFMetadataWriter class is ready for use.")
    print("Usage: BWFMetadataWriter(wav_filepath, metadata_dict)")
    print("See documentation for metadata dictionary structure.")


if __name__ == "__main__":
    main()