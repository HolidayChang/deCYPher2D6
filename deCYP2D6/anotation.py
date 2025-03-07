import os
import sys

def load_variants(vcf_file):
    variants = set()
    line_count = 0
    with open(vcf_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.strip().split('\t', 5)  
            try:
                pos = int(parts[1])
                ref = parts[3]
                alt = parts[4]
                variants.add((pos, ref, alt))
                line_count += 1
            except (IndexError, ValueError):
                continue
    return variants, line_count

def compare_vcfs(reference_vcf, compare_dir, output_file):
    
    reference_variants, line_count = load_variants(reference_vcf)
    total_ref_variants = len(reference_variants)

    
    with open(output_file, 'w') as out_f:
        if line_count > 250:
            out_f.write("HAHAHAHA\n")
            print("HAHAHAHA written to output file.")
            return

    similarities = {}

    for file in os.listdir(compare_dir):
        
        if not (file.endswith('.vcf') or file.endswith('.vcf.gz')):
            continue

        compare_vcf = os.path.join(compare_dir, file)
        compare_variants, _ = load_variants(compare_vcf)

        
        common = reference_variants & compare_variants
        matches = len(common)
        total_variants = len(compare_variants)

        
        percentage = (matches / total_variants * 100) if total_variants else 0
        similarities[file] = (matches, total_variants, percentage)

    
    with open(output_file, 'a') as out_f:
        perfect_matches = []
        for file, (matches, total, percentage) in similarities.items():
            out_f.write(f"VCF file: {file} - Matches: {matches}/{total} ({percentage:.2f}%)\n")
            
            if matches == total:
                perfect_matches.append(file)

        if perfect_matches:
            out_f.write("\nFiles with 100% matching variants (POS, REF, ALT):\n")
            for file in perfect_matches:
                out_f.write(f" - {file}\n")
        else:
            out_f.write("\nNo files with 100% matching variants.\n")

    print(f"Results have been written to {output_file}")

def extract_matching_star_allele(txt_file, paf_file, output_file):
    start_parsing = False  
    with open(txt_file) as f:
        for line in f:
            if start_parsing and line.startswith("-"):
                ...
            if "some condition" in line:  
                start_parsing = True

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python compare_vcfs.py <reference_vcf> <compare_dir> <output_file>")
        sys.exit(1)

    reference_vcf = sys.argv[1]
    compare_dir = sys.argv[2]
    output_file = sys.argv[3]

    compare_vcfs(reference_vcf, compare_dir, output_file)



