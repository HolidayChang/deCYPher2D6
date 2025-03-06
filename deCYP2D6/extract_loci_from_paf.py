import sys
import os
import gzip
from Bio import SeqIO

def open_fasta_file(file_path):
    """Open regular or gzipped FASTA files."""
    if file_path.endswith(".gz"):
        return gzip.open(file_path, "rt")
    else:
        return open(file_path, "r")

def extract_sequence_from_fasta(fasta_file, target_name, start, end, output_file):
    """Extract a sequence from a fasta file given target name and start/end positions."""
    with open_fasta_file(fasta_file) as fasta_handle:
        for record in SeqIO.parse(fasta_handle, "fasta"):
            if record.id == target_name:
                extracted_sequence = record.seq[start:end]
                with open(output_file, "w") as output_handle:
                    new_record = record[start:end]
                    new_record.description = f"Region {start+1}-{end} extracted from {record.id}"
                    SeqIO.write(new_record, output_handle, "fasta")
                    print(f"Extracted sequence written to {output_file}")
                    return
        print(f"Target name '{target_name}' not found in the FASTA file.")

def parse_paf_and_extract_sequences(fasta_file, paf_file, output_path):
    """Parse a PAF file and extract sequences from the fasta file for each entry."""
    with open(paf_file, "r") as paf_handle:
        for i, line in enumerate(paf_handle):
            columns = line.strip().split()
            target_name = columns[5]  # Target name in the PAF file
            target_start = int(columns[7])  # Start coordinate in the PAF file (0-based)
            target_end = int(columns[8])    # End coordinate in the PAF file (0-based)
            output_file = f"{output_path}/extracted_sequence_{i+1}.fasta"
            extract_sequence_from_fasta(fasta_file, target_name, target_start, target_end, output_file)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script_name.py <input_fasta> <input_paf> <output_path>")
        sys.exit(1)
    
    fasta_file = sys.argv[1]
    paf_file = sys.argv[2]
    output_path = sys.argv[3]
    
    parse_paf_and_extract_sequences(fasta_file, paf_file, output_path)

