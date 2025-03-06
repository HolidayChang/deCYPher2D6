import os
import sys

def extract_matching_star_allele(txt_file, paf_file, output_file):
    
    if not os.path.exists(txt_file):
        print(f"Error: TXT file '{txt_file}' not found.")
        sys.exit(1)

    if not os.path.exists(paf_file):
        print(f"Error: PAF file '{paf_file}' not found.")
        sys.exit(1)

    matching_variants = set()
    found_cyp2d6_4 = False  
    found_cyp2d6_74 = False 
    start_parsing = False  
    no_matching_variants = False  
    hahaha_found = False  

    
    with open(txt_file, 'r') as txt:
        lines = txt.readlines()
        for line in lines:
            line = line.strip()

            
            if "HAHAHAHA" in line:
                hahaha_found = True
                break  

            if "No files with 100% matching variants." in line:
                no_matching_variants = True
                break  

            if "Files with 100% matching variants" in line:
                start_parsing = True
                continue

            if start_parsing and line.startswith("-"):
                variant = "*" + line.replace(".vcf", "").split(".")[-1]  
                matching_variants.add(variant)

                
                if "CYP2D6.4.vcf" in line:
                    found_cyp2d6_4 = True
                if "CYP2D6.74.vcf" in line:
                    found_cyp2d6_74 = True

    
    if hahaha_found:
        result = "*5"
    elif no_matching_variants:
        
        result = "*1"
    else:
        
        result = "No matching allele found"
        with open(paf_file, 'r') as paf:
            for line in paf:
                columns = line.strip().split('\t')
                if len(columns) > 5 and "*" in columns[5]:
                    star_allele = "*" + columns[5].split("*")[-1]
                    if star_allele in matching_variants:
                        result = star_allele
                        break

    
    if result == "*10" and found_cyp2d6_4:
        result = "*4"

   
    if result == "*36" and found_cyp2d6_74:
        result = "*68"

    
    with open(output_file, 'w') as out:
        out.write(result + '\n')

    return result


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <txt_file> <paf_file> <output_file>")
        sys.exit(1)

    txt_file = sys.argv[1]
    paf_file = sys.argv[2]
    output_file = sys.argv[3]

    result = extract_matching_star_allele(txt_file, paf_file, output_file)
    print(f"Result saved to {output_file}: {result}")








